"""
GenAI 보안 실습 공통 유틸리티 (Track 2. AWS Generative AI 보안 with Amazon Bedrock)

모든 노트북에서 다음처럼 불러옵니다.
    import sys; sys.path.append("..")
    from common.labutils import *
"""
import json
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------------------
REGION = os.environ.get("LAB_REGION") or boto3.session.Session().region_name or "us-east-1"
LAB_PREFIX = os.environ.get("LAB_PREFIX", "gsec")          # 리소스 이름 접두어 (수강생별로 바꾸면 충돌 방지)
STATE_FILE = Path(__file__).resolve().parent.parent / "lab_state.json"
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"            # 한국어를 지원하는 임베딩 모델 (1024차원)

session = boto3.session.Session(region_name=REGION)
ACCOUNT_ID = session.client("sts").get_caller_identity()["Account"]


def client(name):
    return session.client(name, region_name=REGION)


# ---------------------------------------------------------------------------
# 실습 상태 저장 (정리 노트북이 이 파일을 읽어 리소스를 지웁니다)
# ---------------------------------------------------------------------------
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(**kwargs):
    state = load_state()
    state.update(kwargs)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    return state


# ---------------------------------------------------------------------------
# 모델 선택: 계정·리전에서 사용 가능한 Claude 추론 프로파일을 자동으로 고릅니다.
# 원하는 모델이 있으면 환경 변수 LAB_MODEL_ID 로 지정하세요.
# ---------------------------------------------------------------------------
def pick_model(prefer=("haiku", "sonnet")):
    if os.environ.get("LAB_MODEL_ID"):
        return os.environ["LAB_MODEL_ID"]
    bedrock = client("bedrock")
    profiles = []
    paginator = bedrock.get_paginator("list_inference_profiles")
    for page in paginator.paginate(typeEquals="SYSTEM_DEFINED"):
        profiles += page["inferenceProfileSummaries"]
    claude = [p for p in profiles if "anthropic.claude" in p["inferenceProfileId"] and p.get("status") == "ACTIVE"]
    for word in prefer:
        cands = sorted([p["inferenceProfileId"] for p in claude if word in p["inferenceProfileId"]], reverse=True)
        if cands:
            return cands[0]
    if claude:
        return sorted(p["inferenceProfileId"] for p in claude)[-1]
    raise RuntimeError("사용 가능한 Claude 추론 프로파일이 없습니다. Bedrock 콘솔에서 모델 액세스를 확인하거나 LAB_MODEL_ID를 지정하세요.")


def guardrail_profile_id():
    """Guardrails STANDARD 티어(한국어 포함 다국어 지원)에 필요한 교차 리전 프로파일 ID"""
    if REGION.startswith("us-"):
        return "us.guardrail.v1:0"
    if REGION.startswith("eu-"):
        return "eu.guardrail.v1:0"
    if REGION.startswith("ap-"):
        return "apac.guardrail.v1:0"
    raise RuntimeError(f"{REGION} 리전의 guardrail 프로파일을 Bedrock 콘솔에서 확인해 주세요.")


# ---------------------------------------------------------------------------
# 대기 도우미
# ---------------------------------------------------------------------------
def wait_for(fetch, ok=("READY", "ACTIVE"), fail=("FAILED", "CREATE_FAILED", "UPDATE_FAILED", "UPDATE_UNSUCCESSFUL"),
             key="status", timeout=600, interval=5, label="resource"):
    start = time.time()
    while True:
        res = fetch()
        status = res.get(key)
        if status in ok:
            print(f"  {label}: {status}")
            return res
        if status in fail:
            raise RuntimeError(f"{label} 실패: {status} {res.get('statusReasons') or res.get('failureReasons') or ''}")
        if time.time() - start > timeout:
            raise TimeoutError(f"{label} 대기 시간 초과 (마지막 상태: {status})")
        time.sleep(interval)


def ensure_role(role_name, trust_service, inline_policy, managed_arns=(), source_account_condition=True):
    """실습용 IAM 역할을 만들거나 갱신합니다."""
    iam = client("iam")
    stmt = {"Effect": "Allow", "Principal": {"Service": trust_service}, "Action": "sts:AssumeRole"}
    if source_account_condition:
        stmt["Condition"] = {"StringEquals": {"aws:SourceAccount": ACCOUNT_ID}}
    trust = {"Version": "2012-10-17", "Statement": [stmt]}
    try:
        arn = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust),
                              Tags=[{"Key": "lab", "Value": LAB_PREFIX}])["Role"]["Arn"]
        created = True
    except ClientError as e:
        if e.response["Error"]["Code"] != "EntityAlreadyExists":
            raise
        iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust))
        arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
        created = False
    iam.put_role_policy(RoleName=role_name, PolicyName=f"{role_name}-inline", PolicyDocument=json.dumps(inline_policy))
    for m in managed_arns:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=m)
    if created:
        time.sleep(10)  # IAM 전파 대기
    return arn


# ---------------------------------------------------------------------------
# 출력 도우미
# ---------------------------------------------------------------------------
def table(rows, headers):
    """간단한 텍스트 표 출력 (한글 폭 고려)"""
    import unicodedata

    def w(s):
        return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))

    def cut(s, n):
        s = str(s).replace("\n", " ")
        out, cur = "", 0
        for c in s:
            cw = 2 if unicodedata.east_asian_width(c) in "WF" else 1
            if cur + cw > n - 1:
                return out + "…"
            out += c
            cur += cw
        return out

    widths = [min(max(w(h), *(w(r[i]) for r in rows)) if rows else w(h), 48) for i, h in enumerate(headers)]

    def line(vals):
        cells = []
        for v, n in zip(vals, widths):
            v = cut(v, n) if w(v) > n else str(v).replace("\n", " ")
            cells.append(v + " " * (n - w(v)))
        return "| " + " | ".join(cells) + " |"

    print(line(headers))
    print("|" + "|".join("-" * (n + 2) for n in widths) + "|")
    for r in rows:
        print(line(r))


def converse(model_id, user_text, system=None, guardrail=None, history=None, max_tokens=600, temperature=0.2,
             extra_content=None):
    """Bedrock Converse API 간단 호출. (응답 텍스트, 원본 응답) 반환"""
    rt = client("bedrock-runtime")
    content = [{"text": user_text}] if user_text else []
    if extra_content:
        content += extra_content
    messages = (history or []) + [{"role": "user", "content": content}]
    kwargs = dict(modelId=model_id, messages=messages,
                  inferenceConfig={"maxTokens": max_tokens, "temperature": temperature})
    if system:
        kwargs["system"] = [{"text": system}]
    if guardrail:
        kwargs["guardrailConfig"] = {**guardrail, "trace": "enabled"}
    res = rt.converse(**kwargs)
    text = "".join(c.get("text", "") for c in res["output"]["message"]["content"])
    return text, res

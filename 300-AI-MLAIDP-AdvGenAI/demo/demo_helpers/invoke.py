"""배포된 AgentCore Runtime 을 호출하는 헬퍼.

- invoke_with_iam : boto3 (SigV4 서명) 로 호출 — 02장
- invoke_with_jwt : HTTPS + Bearer 토큰으로 직접 호출 — 03장 이후
"""

import json
import urllib.parse
import uuid

import boto3
import requests
from IPython.display import Markdown, display

from .aws_setup import get_region


def new_session_id(prefix: str = "session") -> str:
    """런타임 세션 ID 는 33자 이상이어야 합니다."""
    return f"{prefix}-{uuid.uuid4().hex}"


def _parse_body(raw: str, content_type: str):
    if "text/event-stream" in (content_type or ""):
        chunks = [line[6:] for line in raw.splitlines() if line.startswith("data: ")]
        raw = "".join(json.loads(c) if c.startswith('"') else c for c in chunks)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def invoke_with_iam(agent_arn: str, prompt: str, session_id: str, qualifier: str = "DEFAULT",
                    user_id: str = None, **payload_extra):
    """IAM(SigV4) 인증으로 런타임 호출 — InvokeAgentRuntime API."""
    client = boto3.client("bedrock-agentcore", region_name=get_region())
    kwargs = dict(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        qualifier=qualifier,
        payload=json.dumps({"prompt": prompt, **payload_extra}).encode("utf-8"),
    )
    if user_id:
        kwargs["runtimeUserId"] = user_id
    resp = client.invoke_agent_runtime(**kwargs)
    raw = resp["response"].read().decode("utf-8")
    return _parse_body(raw, resp.get("contentType", ""))


def runtime_invocation_url(agent_arn: str, qualifier: str = "DEFAULT") -> str:
    escaped_arn = urllib.parse.quote(agent_arn, safe="")
    return (f"https://bedrock-agentcore.{get_region()}.amazonaws.com/runtimes/"
            f"{escaped_arn}/invocations?qualifier={qualifier}")


def invoke_with_jwt(agent_arn: str, prompt: str, bearer_token: str, session_id: str,
                    qualifier: str = "DEFAULT", raise_on_error: bool = True, **payload_extra):
    """OAuth(JWT Bearer) 인증으로 런타임 호출 — POST /runtimes/{EncodedAgentARN}/invocations."""
    headers = {
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    resp = requests.post(
        runtime_invocation_url(agent_arn, qualifier),
        headers=headers,
        data=json.dumps({"prompt": prompt, **payload_extra}),
        timeout=300,
    )
    if resp.status_code >= 400:
        if raise_on_error:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
        return {"http_status": resp.status_code, "error": resp.text}
    return _parse_body(resp.text, resp.headers.get("Content-Type", ""))


def show(result):
    """에이전트 응답을 노트북에 보기 좋게 출력합니다."""
    if isinstance(result, dict) and "response" in result:
        meta = {k: v for k, v in result.items() if k != "response"}
        display(Markdown(str(result["response"])))
        if meta:
            print("─" * 60)
            for k, v in meta.items():
                print(f"{k}: {v}")
    elif isinstance(result, dict):
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        display(Markdown(str(result)))

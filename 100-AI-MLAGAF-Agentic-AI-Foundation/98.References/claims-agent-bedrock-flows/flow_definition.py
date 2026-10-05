"""Bedrock Flows 버전 보험 청구 처리 흐름 정의.

원본(AgentCore 버전)의 3단계 구조를 Flows 노드로 옮긴 것입니다.

    Phase 1 Claims Processor   -> Prompt 노드 (Sonnet)
    Phase 2 Validation Agent   -> Prompt 노드 (Haiku, 분류 작업이라 저렴한 모델)
    Phase 3 Execution          -> Inline code 노드 + Condition 노드 (LLM 호출 없음)

이메일 수신(SES -> S3 -> EventBridge -> Lambda)은 InvokeFlow 호출 하나로 대체했고,
Lambda 도구(정책 조회/청구 생성/사람 검토/알림)는 Inline code 노드 안으로 넣어서
추가 인프라 없이 흐름 하나만 배포하면 됩니다.
"""

import os

# 모델은 환경 변수로 교체 가능. 검증 에이전트는 분류 작업이므로 빠르고 저렴한 모델을 씁니다.
PROCESSOR_MODEL = os.getenv("PROCESSOR_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
VALIDATOR_MODEL = os.getenv("VALIDATOR_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

# 자동 승인 임계값 (원본 config.py의 AUTO_APPROVE_THRESHOLD와 동일)
AUTO_APPROVE_THRESHOLD = int(os.getenv("AUTO_APPROVE_THRESHOLD", "80"))


# ─────────────────────────────────────────────────────────────────────────────
# Inline code 1: 이메일 파싱 + 정책 조회
#   원본의 trigger Lambda(parse_email)와 policy_lookup Lambda를 합친 노드입니다.
#   Inline code 노드는 인터넷 접근이 없으므로 정책 데이터는 코드 안에 둡니다.
#   (실제 환경에서는 이 노드를 Lambda 노드로 바꿔 DynamoDB를 조회하면 됩니다.)
# ─────────────────────────────────────────────────────────────────────────────
PARSE_EMAIL_CODE = '''
import json
import re

POLICIES = {
    "POL-12345": {"policy_number": "POL-12345", "holder_name": "John Smith",
                  "email": "john.smith@example.com", "policy_type": "auto",
                  "coverage_amount": 50000, "deductible": 500, "status": "active"},
    "POL-67890": {"policy_number": "POL-67890", "holder_name": "Jane Doe",
                  "email": "jane.doe@example.com", "policy_type": "home",
                  "coverage_amount": 250000, "deductible": 1000, "status": "active"},
    "POL-11111": {"policy_number": "POL-11111", "holder_name": "Bob Johnson",
                  "email": "bob.j@example.com", "policy_type": "auto",
                  "coverage_amount": 75000, "deductible": 250, "status": "active"},
    "POL-99999": {"policy_number": "POL-99999", "holder_name": "Alice Williams",
                  "email": "alice.w@example.com", "policy_type": "auto",
                  "coverage_amount": 100000, "deductible": 1000, "status": "expired"},
}

text = emailText if isinstance(emailText, str) else str(emailText)

# From/Subject/Date 헤더와 본문 분리 (원본 trigger/handler.py의 parse_email과 동일한 규칙)
headers = {}
lines = text.split("\\n")
body_start = 0
for i, line in enumerate(lines):
    if line.strip() == "":
        body_start = i + 1
        break
    m = re.match(r"^(From|To|Subject|Date):\\s*(.+)$", line, re.IGNORECASE)
    if m:
        headers[m.group(1).lower()] = m.group(2).strip()

body = "\\n".join(lines[body_start:]).strip()
if not body:
    body = text.strip()

# 증권 번호 추출 후 정책 조회 (lookup_policy 도구 대체)
m = re.search(r"POL-\\d+", text)
policy_number = m.group(0) if m else ""
policy = POLICIES.get(policy_number)
if policy:
    policy_json = json.dumps(policy, ensure_ascii=False)
else:
    policy_json = json.dumps({"error": "Policy " + (policy_number or "(없음)") + " not found"}, ensure_ascii=False)

# From 헤더가 없으면(콘솔이나 --text로 본문만 넣은 경우) 본문에서 주소를 찾습니다.
claimant_email = headers.get("from", "")
if not claimant_email:
    m2 = re.search(r"[\\w.+-]+@[\\w-]+\\.[\\w.-]+", text)
    claimant_email = m2.group(0) if m2 else ""

result = {
    "claimant_email": claimant_email,
    "subject": headers.get("subject", ""),
    "body": body,
    "policy_number": policy_number,
    "policy_found": policy is not None,
    "policy_json": policy_json,
}
result
'''


# ─────────────────────────────────────────────────────────────────────────────
# Inline code 2: Processor 출력(JSON) 파싱
#   원본의 submit_decision 구조화 출력 도구 + routing.resolve_decision 역할.
#   JSON 파싱 실패 시 REJECT로 떨어지는 안전 기본값도 원본과 동일합니다.
# ─────────────────────────────────────────────────────────────────────────────
PARSE_DECISION_CODE = '''
import json
import re

def extract_json(s):
    if not isinstance(s, str):
        return {}
    t = s.strip()
    t = re.sub(r"^```[a-zA-Z]*", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start < 0 or end < 0:
        return {}
    try:
        return json.loads(t[start:end + 1])
    except Exception:
        return {}

d = extract_json(decisionText)

decision = str(d.get("decision", "")).upper()
if decision not in ("ACCEPT", "REJECT"):
    decision = "REJECT"          # 구조화 출력 실패 시 안전 기본값 (원본 routing.py와 동일)

try:
    amount = int(float(d.get("amount", 0)))
except Exception:
    amount = 0

out = dict(record) if isinstance(record, dict) else {}
out["decision"] = decision
out["amount"] = amount
out["category"] = d.get("category", "general")
out["claim_description"] = d.get("description", "")
out["reasoning"] = d.get("reasoning", "")
out["coverage_check"] = d.get("coverage_check", "")
out["decision_parsed"] = bool(d)
out["decision_json"] = json.dumps({
    "decision": decision,
    "amount": amount,
    "policy_number": out.get("policy_number", ""),
    "category": out["category"],
    "description": out["claim_description"],
    "reasoning": out["reasoning"],
    "coverage_check": out["coverage_check"],
}, ensure_ascii=False)
out
'''


# ─────────────────────────────────────────────────────────────────────────────
# Inline code 3: Phase 3 실행 (LLM 호출 없음)
#   원본 설계 결정 0014(deterministic phase 3)를 그대로 따릅니다.
#   create_claim / request_human_review / send_notification 도구 세 개를
#   결정론적 코드로 대체했습니다.
# ─────────────────────────────────────────────────────────────────────────────
EXECUTE_CODE = '''
import json
import re
import uuid
from datetime import datetime, timezone

AUTO_APPROVE_THRESHOLD = {threshold}

def extract_json(s):
    if not isinstance(s, str):
        return {}
    t = s.strip()
    t = re.sub(r"^```[a-zA-Z]*", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start < 0 or end < 0:
        return {}
    try:
        return json.loads(t[start:end + 1])
    except Exception:
        return {}

v = extract_json(validationText)

try:
    confidence = int(float(v.get("confidence", 0)))
except Exception:
    confidence = 0

routing = str(v.get("routing", "")).upper()
if routing not in ("AUTO_APPROVE", "HUMAN_REVIEW"):
    routing = "HUMAN_REVIEW"
# 검증 에이전트가 임계값과 다르게 말해도 임계값이 이깁니다 (원본 resolve_routing과 동일)
if confidence < AUTO_APPROVE_THRESHOLD:
    routing = "HUMAN_REVIEW"

rec = dict(record) if isinstance(record, dict) else {}
decision = rec.get("decision", "REJECT")

# REJECT 결정이 항상 우선 (원본 decide_action과 동일)
if decision == "REJECT":
    action = "REJECT"
else:
    action = routing

amount = rec.get("amount", 0)
policy_number = rec.get("policy_number", "") or "N/A"
category = rec.get("category", "general")
claimant = rec.get("claimant_email", "")
now = datetime.now(timezone.utc).isoformat()

claim_id = ""
review_id = ""
priority = ""

if action == "AUTO_APPROVE":
    status = "approved"
    claim_id = "CLM-" + uuid.uuid4().hex[:8].upper()
    subject = "청구 승인 - 증권 " + policy_number
    body = ("고객님의 청구가 승인되었습니다.\\n\\n"
            "청구 번호: " + claim_id + "\\n"
            "금액: $" + format(amount, ",") + "\\n"
            "분류: " + str(category) + "\\n\\n"
            "곧 후속 안내를 드리겠습니다.")
elif action == "HUMAN_REVIEW":
    status = "pending_review"
    claim_id = "CLM-" + uuid.uuid4().hex[:8].upper()
    review_id = "REV-" + uuid.uuid4().hex[:8].upper()
    priority = "high" if amount >= 50000 else "medium"   # 원본 human_review Lambda와 동일
    subject = "청구 검토 중 - 증권 " + policy_number
    body = ("고객님의 청구가 접수되어 담당자가 검토 중입니다.\\n\\n"
            "청구 번호: " + claim_id + "\\n"
            "금액: $" + format(amount, ",") + "\\n\\n"
            "검토가 끝나면 다시 연락드리겠습니다.")
else:
    status = "rejected"                                   # 원본과 동일하게 청구 레코드는 만들지 않음
    subject = "청구 처리 결과 - 증권 " + policy_number
    body = ("고객님의 청구가 검토 결과 거절되었습니다.\\n\\n"
            "사유: " + str(rec.get("reasoning", "정책 조건을 충족하지 않습니다.")))

result = {
    "action": action,
    "decision": decision,
    "confidence": confidence,
    "routing": routing,
    "threshold": AUTO_APPROVE_THRESHOLD,
    "status": status,
    "claim_id": claim_id,
    "review_id": review_id,
    "priority": priority,
    "policy_number": policy_number,
    "policy_found": rec.get("policy_found", False),
    "amount": amount,
    "category": category,
    "claimant_email": claimant,
    "subject": rec.get("subject", ""),
    "reasoning": rec.get("reasoning", ""),
    "coverage_check": rec.get("coverage_check", ""),
    "validation_notes": v.get("validation_notes", ""),
    "concerns": v.get("concerns", ""),
    "notification": {"recipient": claimant, "subject": subject, "body": body},
    "processed_at": now,
}
result
'''.replace("{threshold}", str(AUTO_APPROVE_THRESHOLD))


# ─────────────────────────────────────────────────────────────────────────────
# 프롬프트 (원본 main.py의 PROCESSOR_PROMPT / VALIDATOR_PROMPT를 Flows용으로 축약)
# ─────────────────────────────────────────────────────────────────────────────
PROCESSOR_PROMPT = """You are a Claims Processor for SecureGuard Insurance.

Claim submission (from a customer email):
<claim>
{{claimText}}
</claim>

Policy lookup result:
<policy>
{{policyJson}}
</policy>

Your job:
1. Extract the claim details (policy number, amount, category, description).
2. Evaluate the claim against the policy terms in the lookup result.
3. Decide ACCEPT or REJECT.

Rules:
- REJECT only for policy reasons: the lookup returned an error, the policy is
  inactive/expired, the amount exceeds the coverage limit, or the claim type is not covered.
- ACCEPT if the policy is active, the amount is within the coverage limit,
  and the claim type matches the policy type.
- A vague description or a missing amount is NOT a reason to REJECT. Accept the claim
  conditionally, set amount to 0 if it is not stated, and note in the reasoning that the
  loss amount must be verified. The validation agent downstream lowers the confidence
  for such claims so that a human reviews them.
- Always mention the deductible in your reasoning.
- Never invent policy details that are not in the lookup result.
- category must be one of: auto_collision, property_damage, theft, natural_disaster, medical, general

Respond with ONLY a JSON object, no markdown fences, no extra text:
{
  "decision": "ACCEPT or REJECT",
  "amount": <integer dollar amount>,
  "policy_number": "<policy number>",
  "category": "<category>",
  "description": "<one line description of the damage or loss>",
  "reasoning": "<왜 승인/거절했는지 한국어로 2~3문장>",
  "coverage_check": "<보장 한도, 정책 상태, 공제액 확인 결과를 한국어로 한 문장>"
}"""

VALIDATOR_PROMPT = """You are a Claims Validation Agent for SecureGuard Insurance.
You independently review the Claims Processor's decision.

Original claim submission:
<claim>
{{claimText}}
</claim>

Claims Processor decision:
<decision>
{{decisionJson}}
</decision>

Scoring guide:
- 90-100: clear-cut case, the decision is obviously correct
- 80-89: sound decision, minor questions but acceptable to auto-approve
- 60-79: some concerns, a human should review before finalizing
- 0-59: significant issues, must go to human review

Rules:
- If CONFIDENCE >= 80, routing is AUTO_APPROVE. Otherwise HUMAN_REVIEW.
- Be skeptical of high-value claims (over $25,000): lower the confidence unless clearly justified.
- Lower the confidence if the description is vague, or if the category does not match the description.
- The processor writes its reasoning fields in Korean by design. That is expected and is never a concern.
- Judge only the substance of the claim and the decision, not the language or formatting of the fields.

Respond with ONLY a JSON object, no markdown fences, no extra text:
{
  "confidence": <0-100 integer>,
  "routing": "AUTO_APPROVE or HUMAN_REVIEW",
  "validation_notes": "<처리 담당 에이전트의 판단에 대한 평가를 한국어로 2문장>",
  "concerns": "<우려 사항을 한국어로, 없으면 '없음'>"
}"""


def _prompt_node(name, model_id, template, variables, max_tokens=1200):
    return {
        "name": name,
        "type": "Prompt",
        "inputs": [
            {"name": var, "type": "String", "expression": expr}
            for var, expr in variables
        ],
        "outputs": [{"name": "modelCompletion", "type": "String"}],
        "configuration": {
            "prompt": {
                "sourceConfiguration": {
                    "inline": {
                        "modelId": model_id,
                        "templateType": "TEXT",
                        "templateConfiguration": {
                            "text": {
                                "text": template,
                                "inputVariables": [{"name": var} for var, _ in variables],
                            }
                        },
                        # Claude 최신 모델은 temperature와 topP를 동시에 지정할 수 없습니다.
                        "inferenceConfiguration": {
                            "text": {"maxTokens": max_tokens, "temperature": 0.0}
                        },
                    }
                }
            }
        },
    }


def _inline_code_node(name, code, inputs, output_type="Object"):
    return {
        "name": name,
        "type": "InlineCode",
        "inputs": [
            {"name": var, "type": vtype, "expression": expr} for var, vtype, expr in inputs
        ],
        "outputs": [{"name": "response", "type": output_type}],
        "configuration": {"inlineCode": {"code": code, "language": "Python_3"}},
    }


def _data_connection(source, source_output, target, target_input):
    return {
        "name": f"{source}_to_{target}_{target_input}",
        "source": source,
        "target": target,
        "type": "Data",
        "configuration": {"data": {"sourceOutput": source_output, "targetInput": target_input}},
    }


def _conditional_connection(source, target, condition):
    return {
        "name": f"{source}_to_{target}",
        "source": source,
        "target": target,
        "type": "Conditional",
        "configuration": {"conditional": {"condition": condition}},
    }


def build_definition():
    """CreateFlow / UpdateFlow의 definition 값을 만듭니다."""
    nodes = [
        # 입력: 이메일 원문 한 덩어리 (InvokeFlow의 content로 그대로 전달)
        {
            "name": "EmailInput",
            "type": "Input",
            "outputs": [{"name": "document", "type": "String"}],
            "configuration": {"input": {}},
        },
        # 수신 처리: 헤더/본문 분리 + 증권 조회
        _inline_code_node(
            "ParseEmail",
            PARSE_EMAIL_CODE,
            [("emailText", "String", "$.data")],
        ),
        # Phase 1
        _prompt_node(
            "ClaimsProcessor",
            PROCESSOR_MODEL,
            PROCESSOR_PROMPT,
            [("claimText", "$.data.body"), ("policyJson", "$.data.policy_json")],
        ),
        # Phase 1 결과 구조화
        _inline_code_node(
            "ParseDecision",
            PARSE_DECISION_CODE,
            [("decisionText", "String", "$.data"), ("record", "Object", "$.data")],
        ),
        # Phase 2
        _prompt_node(
            "ValidationAgent",
            VALIDATOR_MODEL,
            VALIDATOR_PROMPT,
            [("claimText", "$.data.body"), ("decisionJson", "$.data.decision_json")],
            max_tokens=800,
        ),
        # Phase 3: 임계값 적용 + 청구/검토 레코드 생성 + 알림 작성 (LLM 없음)
        _inline_code_node(
            "ExecuteDecision",
            EXECUTE_CODE,
            [("validationText", "String", "$.data"), ("record", "Object", "$.data")],
        ),
        # 라우팅: action 값에 따라 세 갈래로
        {
            "name": "RouteByAction",
            "type": "Condition",
            "inputs": [{"name": "action", "type": "String", "expression": "$.data.action"}],
            "configuration": {
                "condition": {
                    "conditions": [
                        {"name": "autoApprove", "expression": 'action == "AUTO_APPROVE"'},
                        {"name": "humanReview", "expression": 'action == "HUMAN_REVIEW"'},
                        {"name": "default"},
                    ]
                }
            },
        },
        # 세 갈래의 종료 노드. 어떤 노드가 결과를 냈는지로 경로를 바로 확인할 수 있습니다.
        {
            "name": "AutoApproved",
            "type": "Output",
            "inputs": [{"name": "document", "type": "Object", "expression": "$.data"}],
            "configuration": {"output": {}},
        },
        {
            "name": "HumanReview",
            "type": "Output",
            "inputs": [{"name": "document", "type": "Object", "expression": "$.data"}],
            "configuration": {"output": {}},
        },
        {
            "name": "Rejected",
            "type": "Output",
            "inputs": [{"name": "document", "type": "Object", "expression": "$.data"}],
            "configuration": {"output": {}},
        },
    ]

    connections = [
        _data_connection("EmailInput", "document", "ParseEmail", "emailText"),
        _data_connection("ParseEmail", "response", "ClaimsProcessor", "claimText"),
        _data_connection("ParseEmail", "response", "ClaimsProcessor", "policyJson"),
        _data_connection("ClaimsProcessor", "modelCompletion", "ParseDecision", "decisionText"),
        _data_connection("ParseEmail", "response", "ParseDecision", "record"),
        _data_connection("ParseDecision", "response", "ValidationAgent", "claimText"),
        _data_connection("ParseDecision", "response", "ValidationAgent", "decisionJson"),
        _data_connection("ValidationAgent", "modelCompletion", "ExecuteDecision", "validationText"),
        _data_connection("ParseDecision", "response", "ExecuteDecision", "record"),
        _data_connection("ExecuteDecision", "response", "RouteByAction", "action"),
        # 조건 연결은 "어느 갈래로 갈지"만 정합니다. 각 종료 노드가 받을 데이터는
        # ExecuteDecision에서 직접 연결해 주어야 합니다.
        _data_connection("ExecuteDecision", "response", "AutoApproved", "document"),
        _data_connection("ExecuteDecision", "response", "HumanReview", "document"),
        _data_connection("ExecuteDecision", "response", "Rejected", "document"),
        _conditional_connection("RouteByAction", "AutoApproved", "autoApprove"),
        _conditional_connection("RouteByAction", "HumanReview", "humanReview"),
        _conditional_connection("RouteByAction", "Rejected", "default"),
    ]

    return {"nodes": nodes, "connections": connections}


if __name__ == "__main__":
    import json

    print(json.dumps(build_definition(), indent=2, ensure_ascii=False))

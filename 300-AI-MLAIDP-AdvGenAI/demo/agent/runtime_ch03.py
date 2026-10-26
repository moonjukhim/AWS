"""[Chapter 03] + JWT 인바운드 인증(사용자 컨텍스트·감사 로그) + API 키 아웃바운드 인증."""
import base64
import hashlib
import json
import os
import threading
import time
import uuid

from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.identity.auth import requires_api_key  # [CH03]

from demo_helpers.config import MODEL_ID, PARTNER_API_PROVIDER
from demo_helpers.tools import SYSTEM_PROMPT, get_product_info, get_return_policy

REGION = os.environ.get("AWS_REGION", "us-east-1")
MICROVM_BOOT_ID = uuid.uuid4().hex[:8]

app = BedrockAgentCoreApp()


@tool
def generate_sales_report(duration_seconds: int = 20) -> str:
    """장시간 걸리는 '판매 리포트 생성' 작업을 백그라운드로 시작하고 즉시 응답합니다.

    Args:
        duration_seconds: 작업 소요 시간(초)
    """
    task_id = app.add_async_task("sales_report", {"duration": duration_seconds})

    def background_work():
        time.sleep(duration_seconds)
        app.complete_async_task(task_id)

    threading.Thread(target=background_work, daemon=True).start()
    return f"리포트 작업(ID: {task_id})을 시작했습니다. 약 {duration_seconds}초 후 완료됩니다."


# ── [CH03] 아웃바운드 인증: AgentCore Identity 에서 API 키를 받아옴 ─────────
@requires_api_key(provider_name=PARTNER_API_PROVIDER)
def _get_partner_api_key(*, api_key: str = "") -> str:
    return api_key  # 워크로드 액세스 토큰 → GetResourceApiKey 로 받은 키가 주입됨


@tool
def track_shipment(order_id: str) -> str:
    """주문 번호로 배송 상태를 조회합니다 (외부 배송 파트너 API 호출).

    Args:
        order_id: 주문 번호 (예: ORD-1001)
    """
    api_key = _get_partner_api_key()
    # 실제 환경이라면: requests.get(f"https://api.partner.example/track/{order_id}", headers={"x-api-key": api_key})
    statuses = ["상품 준비 중", "배송 중 (서울 허브 도착)", "배송 완료"]
    status = statuses[int(hashlib.md5(order_id.encode()).hexdigest(), 16) % len(statuses)]
    return f"주문 {order_id}: {status} (파트너 API 키 ****{api_key[-4:]} 로 인증됨)"


# ── [CH03] 인바운드 인증: Runtime 이 검증한 JWT 에서 사용자 컨텍스트 추출 ────
def get_caller_claims(context) -> dict:
    auth = (context.request_headers or {}).get("Authorization", "")
    if not auth.startswith("Bearer "):
        return {}
    payload = auth.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))  # 서명 검증은 Runtime 이 이미 수행


_agent = None
_session_owner = None  # [CH03] 이 세션(microVM)의 소유자


@app.entrypoint
def invoke(payload, context):
    global _agent, _session_owner
    claims = get_caller_claims(context)
    username = claims.get("username", "anonymous")

    if _session_owner and _session_owner != username:  # [CH03] 세션 소유자 검증
        print(json.dumps({"type": "AUDIT", "event": "SESSION_OWNER_MISMATCH", "user": username,
                          "session_id": context.session_id}))
        return {"response": "⛔ 이 세션은 다른 사용자에게 속해 있어 사용할 수 없습니다.", "user": username}

    if _agent is None:
        _session_owner = username
        _agent = Agent(
            model=BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.3),
            tools=[get_product_info, get_return_policy, generate_sales_report, track_shipment],
            system_prompt=SYSTEM_PROMPT + f"\n현재 로그인한 고객 ID: {username}\n",
            callback_handler=None,
        )

    prompt = payload.get("prompt", "")
    result = _agent(prompt)
    tools_used = list(result.metrics.tool_metrics.keys())

    print(json.dumps({  # [CH03] 감사 로그 → CloudWatch Logs
        "type": "AUDIT", "user": username, "sub": claims.get("sub"),
        "session_id": context.session_id, "prompt": prompt[:200], "tools_used_in_session": tools_used,
    }, ensure_ascii=False))

    return {
        "response": str(result),
        "user": username,
        "session_id": context.session_id,
        "microvm_boot_id": MICROVM_BOOT_ID,
        "tools_used_in_session": tools_used,
    }


if __name__ == "__main__":
    app.run()

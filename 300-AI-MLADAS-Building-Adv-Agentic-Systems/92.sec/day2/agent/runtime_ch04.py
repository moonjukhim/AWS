"""[Chapter 04] + Code Interpreter + AgentCore Gateway(MCP, 토큰 전파) — Policy 는 Gateway 에서 강제."""
import base64
import hashlib
import json
import os
import threading
import time
import uuid

from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient  # [CH04]
from mcp.client.streamable_http import streamablehttp_client  # [CH04]
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.identity.auth import requires_api_key
from bedrock_agentcore.tools.code_interpreter_client import code_session  # [CH04]

from demo_helpers.config import MODEL_ID, PARTNER_API_PROVIDER
from demo_helpers.tools import SYSTEM_PROMPT, get_product_info, get_return_policy

REGION = os.environ.get("AWS_REGION", "us-east-1")
GATEWAY_URL = os.environ["GATEWAY_URL"]  # [CH04]
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


@requires_api_key(provider_name=PARTNER_API_PROVIDER)
def _get_partner_api_key(*, api_key: str = "") -> str:
    return api_key


@tool
def track_shipment(order_id: str) -> str:
    """주문 번호로 배송 상태를 조회합니다 (외부 배송 파트너 API 호출).

    Args:
        order_id: 주문 번호 (예: ORD-1001)
    """
    api_key = _get_partner_api_key()
    statuses = ["상품 준비 중", "배송 중 (서울 허브 도착)", "배송 완료"]
    status = statuses[int(hashlib.md5(order_id.encode()).hexdigest(), 16) % len(statuses)]
    return f"주문 {order_id}: {status} (파트너 API 키 ****{api_key[-4:]} 로 인증됨)"


@tool
def run_python(code: str) -> str:  # [CH04] 기본 제공 도구: Code Interpreter
    """금액 계산·데이터 분석이 필요할 때 Python 코드를 안전한 샌드박스에서 실행합니다. 결과는 print() 로 출력하세요.

    Args:
        code: 실행할 Python 코드
    """
    with code_session(REGION) as ci:
        response = ci.invoke("executeCode", {"code": code, "language": "python", "clearContext": True})
        for event in response["stream"]:
            return json.dumps(event["result"].get("structuredContent", event["result"]), ensure_ascii=False)


def get_caller_claims(context) -> dict:
    auth = (context.request_headers or {}).get("Authorization", "")
    if not auth.startswith("Bearer "):
        return {}
    payload = auth.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


_session_owner = None
_conversation = []  # [CH04] 요청마다 Agent 를 새로 만들므로 세션 대화 기록을 별도로 유지


@app.entrypoint
def invoke(payload, context):
    global _session_owner
    claims = get_caller_claims(context)
    username = claims.get("username", "anonymous")
    if _session_owner and _session_owner != username:
        print(json.dumps({"type": "AUDIT", "event": "SESSION_OWNER_MISMATCH", "user": username,
                          "session_id": context.session_id}))
        return {"response": "⛔ 이 세션은 다른 사용자에게 속해 있어 사용할 수 없습니다.", "user": username}
    _session_owner = username

    # [CH04] 고객의 JWT 를 Gateway 까지 전파 → Gateway 가 고객 권한으로 인증 + Policy 평가
    auth_header = context.request_headers["Authorization"]
    gateway = MCPClient(lambda: streamablehttp_client(GATEWAY_URL, headers={"Authorization": auth_header}))

    prompt = payload.get("prompt", "")
    with gateway:
        gateway_tools = gateway.list_tools_sync()
        agent = Agent(
            model=BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.3),
            tools=[get_product_info, get_return_policy, generate_sales_report, track_shipment, run_python]
            + gateway_tools,
            system_prompt=SYSTEM_PROMPT
            + f"\n현재 로그인한 고객 ID: {username}\n"
            + "환불 요청이 정책에 의해 거부되면 고객에게 상담원 연결(1588-0000)을 안내하세요.\n",
            messages=_conversation,
            callback_handler=None,
        )
        result = agent(prompt)
    _conversation[:] = agent.messages
    tools_used = list(result.metrics.tool_metrics.keys())

    print(json.dumps({
        "type": "AUDIT", "user": username, "sub": claims.get("sub"),
        "session_id": context.session_id, "prompt": prompt[:200], "tools_used_in_session": tools_used,
    }, ensure_ascii=False))

    return {
        "response": str(result),
        "user": username,
        "session_id": context.session_id,
        "microvm_boot_id": MICROVM_BOOT_ID,
        "tools_used_in_session": tools_used,
        "gateway_tools": [t.tool_name for t in gateway_tools],
    }


if __name__ == "__main__":
    app.run()

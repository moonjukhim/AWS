"""[Chapter 02] AgentCore Runtime 에서 실행되는 고객지원 에이전트 (v1)."""
import os
import threading
import time
import uuid

from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME ① ####

from demo_helpers.config import MODEL_ID
from demo_helpers.tools import SYSTEM_PROMPT, get_product_info, get_return_policy

REGION = os.environ.get("AWS_REGION", "us-east-1")
MICROVM_BOOT_ID = uuid.uuid4().hex[:8]  # 이 프로세스(microVM)가 시작될 때 1회 생성

app = BedrockAgentCoreApp()  #### AGENTCORE RUNTIME ② ####


@tool
def generate_sales_report(duration_seconds: int = 20) -> str:
    """장시간 걸리는 '판매 리포트 생성' 작업을 백그라운드로 시작하고 즉시 응답합니다.

    Args:
        duration_seconds: 작업 소요 시간(초)
    """
    task_id = app.add_async_task("sales_report", {"duration": duration_seconds})  # /ping → HealthyBusy

    def background_work():
        time.sleep(duration_seconds)  # 실제로는 데이터 집계/리포트 생성 로직
        app.complete_async_task(task_id)  # /ping → Healthy

    threading.Thread(target=background_work, daemon=True).start()
    return f"리포트 작업(ID: {task_id})을 시작했습니다. 약 {duration_seconds}초 후 완료됩니다."


# 세션 내 대화 상태: 같은 세션의 요청은 같은 microVM 으로 라우팅되므로 전역 객체에 유지됩니다.
_agent = None


def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = Agent(
            model=BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.3),
            tools=[get_product_info, get_return_policy, generate_sales_report],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=None,
        )
    return _agent


@app.entrypoint  #### AGENTCORE RUNTIME ③ ####
def invoke(payload, context):
    agent = get_agent()
    result = agent(payload.get("prompt", ""))
    return {
        "response": str(result),
        "session_id": context.session_id,
        "microvm_boot_id": MICROVM_BOOT_ID,
        "messages_in_this_microvm": len(agent.messages),
    }


if __name__ == "__main__":
    app.run()  #### AGENTCORE RUNTIME ④ ####

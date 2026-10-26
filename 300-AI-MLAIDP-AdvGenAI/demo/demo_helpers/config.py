"""데모 전체에서 공유하는 상수와 챕터 간 상태(state) 저장소.

각 챕터 노트북은 자신이 만든 AWS 리소스 ID를 demo_state.json 에 기록하고,
다음 챕터 노트북은 이 파일을 읽어 이전 챕터의 결과물 위에 기능을 덧붙입니다.
"""

import json
import os
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = DEMO_ROOT / "demo_state.json"

# ── 모델 ───────────────────────────────────────────────────────────────
# Bedrock 콘솔에서 모델 액세스가 활성화되어 있어야 합니다.
# Claude 사용이 어려운 계정이라면 "global.amazon.nova-2-lite-v1:0" 으로 바꿔도 됩니다.
MODEL_ID = os.environ.get("DEMO_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")

# ── 리소스 이름 ───────────────────────────────────────────────────────
AGENT_NAME = "customer_support_agent"
RUNTIME_ROLE_NAME_PREFIX = "AgentCoreDemoRuntimeRole"
COGNITO_POOL_NAME = "CustomerSupportDemoPool"
COGNITO_CLIENT_NAME = "CustomerSupportDemoClient"
DEMO_USERS = ["alice", "bob"]
DEMO_PASSWORD = "AgentCore#Demo2026"  # 데모 전용 비밀번호 (실서비스에서는 절대 하드코딩 금지)
PARTNER_API_PROVIDER = "shipping-partner-apikey"
LAMBDA_NAME = "customer-support-demo-tools"
LAMBDA_ROLE_NAME = "AgentCoreDemoLambdaRole"
GATEWAY_NAME = "customer-support-gw"
GATEWAY_ROLE_NAME = "AgentCoreDemoGatewayRole"
GATEWAY_TARGET_NAME = "CustomerDataTools"
POLICY_ENGINE_NAME = "customer_support_pe"
MEMORY_NAME = "CustomerSupportMemory"
ONLINE_EVAL_CONFIG_NAME = "customer_support_online_eval"

# 장기 메모리 네임스페이스 ({actorId}, {sessionId} 는 AgentCore Memory 가 치환)
NS_PREFERENCES = "support/customer/{actorId}/preferences"
NS_FACTS = "support/customer/{actorId}/facts"
NS_SUMMARY = "support/customer/{actorId}/{sessionId}/summary"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(**values) -> dict:
    state = load_state()
    state.update(values)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def require_state(*keys) -> dict:
    """이전 챕터에서 만든 리소스가 있는지 확인합니다."""
    state = load_state()
    missing = [k for k in keys if not state.get(k)]
    if missing:
        raise RuntimeError(
            f"이전 챕터의 결과물이 없습니다: {missing}\n"
            "노트북을 02 → 03 → 04 → 05 → 06 순서로 실행했는지 확인하세요."
        )
    return state

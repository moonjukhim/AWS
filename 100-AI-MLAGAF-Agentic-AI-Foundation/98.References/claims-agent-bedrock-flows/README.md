# 보험 청구 처리 흐름 — Amazon Bedrock Flows 버전

`agentcore-samples`의 **event-driven-claims-agent**(AgentCore Runtime + Gateway + Memory + Cedar, 리소스 약 76개)를
**Bedrock Flows 흐름 하나**로 옮긴 교육용 버전입니다.

가장 큰 차이는 이메일 수신 경로입니다. 원본은 SES → S3 → EventBridge → Lambda → Runtime을 거치지만,
이 버전은 `InvokeFlow` 호출 한 번으로 같은 처리를 실행하고 결과를 바로 화면에서 확인합니다.

```
원본:  이메일 → SES → S3 → EventBridge → Lambda(트리거) → AgentCore Runtime → DynamoDB에 기록 (결과를 따로 조회)
이 버전: 이메일 텍스트 → InvokeFlow → 결과 JSON을 즉시 반환
```

배포에 걸리는 시간은 1분 남짓이고, 만드는 리소스는 **IAM 역할 1개와 Flow 1개**뿐입니다.
Lambda, DynamoDB, SES, S3, EventBridge, Cognito, CDK, Docker는 필요 없습니다.

---

## 흐름 구조

```
EmailInput (입력)
   │
   ├─▶ ParseEmail          [Inline code]  헤더/본문 분리 + 증권 조회       ← 원본 trigger Lambda + policy_lookup Lambda
   │
   ├─▶ ClaimsProcessor     [Prompt/Sonnet] 1단계: 보장 판단 ACCEPT/REJECT  ← 원본 Phase 1 Claims Processor
   ├─▶ ParseDecision       [Inline code]  판단 결과 JSON 구조화            ← 원본 submit_decision 도구
   │
   ├─▶ ValidationAgent     [Prompt/Haiku]  2단계: 신뢰도 0~100 채점        ← 원본 Phase 2 Validation Agent
   │
   ├─▶ ExecuteDecision     [Inline code]  3단계: 임계값 적용, 청구/검토 번호 발급, 알림 작성
   │                                       ← 원본 create_claim / request_human_review / send_notification
   │
   └─▶ RouteByAction       [Condition]    action 값으로 세 갈래 분기
          ├── AUTO_APPROVE ──▶ AutoApproved (출력)
          ├── HUMAN_REVIEW ──▶ HumanReview  (출력)
          └── default      ──▶ Rejected     (출력)
```

어떤 출력 노드가 결과를 냈는지로 라우팅 결과를 한눈에 확인할 수 있습니다.

### 원본과 동일하게 유지한 로직

| 항목 | 내용 |
|---|---|
| 이중 에이전트 | 처리 에이전트의 판단을 검증 에이전트가 독립적으로 재검토 (원본 설계 결정 0002) |
| 비용 라우팅 | 검증은 분류 작업이므로 Haiku, 처리는 Sonnet (원본 설계 결정 0013) |
| 결정론적 3단계 | 3단계는 LLM을 부르지 않고 코드로 실행 (원본 설계 결정 0014) |
| 임계값 강제 | 신뢰도 80 미만이면 검증 에이전트가 뭐라 하든 HUMAN_REVIEW (원본 `routing.py`) |
| 거절 우선 | 1단계가 REJECT면 신뢰도와 무관하게 거절 (원본 `decide_action`) |
| 안전 기본값 | JSON 파싱 실패 시 REJECT / HUMAN_REVIEW로 떨어짐 |
| 우선순위 규칙 | 5만 달러 이상 검토 건은 high, 미만은 medium (원본 human_review Lambda) |

### 원본에서 단순화한 부분

| 원본 | 이 버전 | 이유 |
|---|---|---|
| SES → S3 → EventBridge → Lambda | `InvokeFlow` 직접 호출 | 즉시 실행하고 결과를 바로 확인하기 위해 |
| Gateway(MCP) + Lambda 도구 6개 | Inline code 노드 3개 | 배포 대상이 흐름 하나로 줄어듦 |
| DynamoDB 정책/청구/검토 테이블 | 코드 안의 샘플 정책 4건 | 시드 작업과 테이블 관리 제거 |
| SES 발송 | 알림 본문을 결과에 포함 | 도메인 검증 없이 내용 확인 가능 |
| Cedar 정책 엔진, AgentCore Memory, Identity, 온라인 평가 | 제외 | Flows에 대응 기능이 없음 (아래 참고) |

Guardrails가 필요하면 Prompt 노드의 `guardrailConfiguration`에 추가하면 됩니다.
정책 조회를 실제 DynamoDB로 바꾸려면 `ParseEmail` 노드를 Lambda 노드로 교체하십시오.

---

## 사전 준비

- Python 3.9 이상, `pip install boto3`
- AWS 자격 증명 (`aws configure`)과 Bedrock 모델 액세스 (Claude Sonnet 4.5, Claude Haiku 4.5)
- 권한: `bedrock:*Flow*`, `iam:CreateRole`, `iam:PutRolePolicy`, `bedrock:InvokeFlow`

## 실행

```bash
# 1. 배포 (IAM 역할 + Flow + 버전 + 별칭)
python deploy_flow.py

# 2. 샘플 실행
python run_flow.py samples/01-auto-approve.txt     # 한 건
python run_flow.py --all                           # 네 건 모두
python run_flow.py --all --trace                   # 노드별 입출력까지 확인
python run_flow.py --text "POL-12345 증권으로 접촉 사고 청구합니다. 수리 견적 3200달러입니다."

# 3. 정리
python delete_flow.py --all
```

배포 정보는 `.flow-config.json`에 저장되고 `run_flow.py`가 이 파일을 읽습니다.
`deploy_flow.py`를 다시 실행하면 같은 흐름을 갱신하고 새 버전을 발행합니다.

## 샘플 시나리오

| 파일 | 내용 | 기대 경로 |
|---|---|---|
| `01-auto-approve.txt` | POL-12345, 접촉 사고 $3,200, 서류 완비 | 자동 승인 |
| `02-human-review.txt` | POL-67890, "피해가 있습니다" 수준의 모호한 설명 | 사람 검토 (신뢰도 낮음) |
| `03-high-value-review.txt` | POL-11111, 전손 $68,000 | 사람 검토 (고액 청구) |
| `04-reject-expired.txt` | POL-99999, 만료된 증권 | 거절 |

실행 결과 예시(1번 샘플, 약 20초):

```
  경로: AutoApproved 노드 → 자동 승인  (19.5초)
  증권 POL-12345 / $3,200 / auto_collision / 조회 성공

  [1단계 처리] ACCEPT — 보험 계약이 활성 상태이고, 청구 금액 $3,200이 보장 한도 $50,000 이내입니다...
  [2단계 검증] 신뢰도 82/100 (임계값 80) → AUTO_APPROVE
  [3단계 실행] 상태 approved
             청구 생성: CLM-C1091C01
             알림 → john.smith@example.com: 청구 승인 - 증권 POL-12345
```

## 강의 활용

- **워크플로 패턴**: 프롬프트 체이닝(1단계 → 2단계), 라우팅(Condition 노드), 평가자-최적화(검증 에이전트)가
  한 흐름 안에 함께 들어 있습니다. Module 3 활동 1의 정답 예시로 그대로 쓸 수 있습니다.
- **Human-in-the-loop**: 신뢰도 임계값이 사람에게 넘길 기준을 코드로 정의한 예입니다.
  `flow_definition.py`의 `AUTO_APPROVE_THRESHOLD`를 90으로 올려 다시 배포하면 자동 승인 건이 검토로 넘어갑니다.
- **관리형과 사용자 지정 비교**: 같은 요구사항을 Flows(관리형 워크플로)와 AgentCore(사용자 지정 에이전트)로
  각각 구현한 두 버전을 나란히 놓고 Module 6의 "생각 및 토론" 슬라이드에서 비교하십시오.
- **콘솔 시연**: Bedrock 콘솔의 Flow 빌더에서 노드 그래프를 열어 두고 테스트 창에서 실행하면
  분기 경로가 시각적으로 표시됩니다.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `flow_definition.py` | 노드와 연결 정의, 프롬프트, Inline code 세 개 |
| `deploy_flow.py` | IAM 역할 생성, 흐름 생성/갱신, 준비, 버전과 별칭 발행 |
| `run_flow.py` | 흐름 호출과 결과 출력 (`--trace`, `--json`, `--all`) |
| `delete_flow.py` | 흐름과 IAM 역할 정리 |
| `samples/` | 네 갈래를 모두 보여주는 청구 이메일 |

## 참고 사항

- Inline code 노드는 미리보기 기능입니다. 흐름당 5개, 노드당 입력 5개까지이고 인터넷 접근이 없습니다.
  또한 비동기 흐름 실행에서는 지원되지 않습니다.
- 모델은 환경 변수로 바꿀 수 있습니다: `PROCESSOR_MODEL_ID`, `VALIDATOR_MODEL_ID`.
- 비용은 호출당 Bedrock 모델 토큰 요금만 발생합니다. 흐름 자체에는 유휴 비용이 없습니다.
- 원본 AgentCore 버전:
  `agentcore-samples/02-use-cases/02-workflow-automation-agents/event-driven-claims-agent/`

# 강의 자료: 05-WAF × IT Incident Response Agent

> **슬라이드:** `05-WAF.pptx` (Well-Architected 에이전틱 AI 시스템, 22장)
> **실습 코드:** `04.it-incident-response-agent` (IT 장애 티켓 자동 처리 에이전트)
> **용도:** 슬라이드의 Well-Architected 개념을 이 샘플의 실제 코드·설정에 연결해 설명하기 위한 강사용 자료

이 모듈은 앞 모듈(멀티 에이전트, 컨텍스트, 보안, 관찰성)을 **Well-Architected 6개 핵심 요소**로 다시 묶는 정리 모듈입니다. 그래서 이 샘플은 "기능 하나를 깊게"보다는 **"6개 요소가 한 시스템 안에서 어디에 어떻게 구현되어 있고, 어디가 비어 있는가"** 를 보여 주는 데 씁니다. 샘플은 의도적으로 *개발 설정*으로 배포되므로, 개발 설정과 프로덕션 설정의 차이가 그대로 강의 소재가 됩니다.

---

## 0. 한 장 요약: 슬라이드와 코드 매핑

| 슬라이드 | 개념 | 샘플에서 보여줄 곳 |
|---|---|---|
| 3 | 에이전틱 AI 프로덕션 고려 사항 5가지 | §1.3 표: 거버넌스, 모니터링, 컨텍스트, 통신, 평가를 각각 코드에 대입 |
| 5 | WA 6개 핵심 요소 | §4 부록 매핑 (요소별 "구현됨 / 빈틈 / 개선 과제") |
| 6 | Gen AI Lens: 필요한 경우에만 대리권을 높인다 | `main.py:450-623`: 가드레일, 메모리, 저장, 이벤트 발행은 **코드**가 하고, 진단과 도구 선택만 **LLM**이 함 |
| 7 | Security Scoping Matrix | 이 샘플은 **감독되는 대리권(Scope 3)**. `create_change_request`를 사람 승인 없이 실행 |
| 8 | WA 원칙 6가지 (관찰성, 제어 가능성 등) | §2.4 표: OTEL 스팬 속성, Cedar 정책, 가드레일, 실패 시 사람 검토, ADR 문서 |
| 9 | 통합 모범 사례 (MCP, Gateway 허브, 연결 관리) | `agentcore.json` Gateway + Lambda 대상 4개, SNS → Trigger → DLQ, EventBridge |
| 11 | 배포 준비 상태 검증 체크리스트 | §3 체크리스트 + `README.md:736` "Scale for Production" |
| 12–13 | 아키텍처 설계 활동 (전자상거래 멀티 에이전트) | §5: 단일 에이전트 샘플의 패턴을 마커 1~5에 옮겨 적용 |
| 17 | 운영 우수성 | 선언형 `agentcore.json` + CDK 단일 배포, 온라인 평가 4종, OTEL |
| 18 | 보안 | Cedar Policy Engine(LOG_ONLY), 3개 인증 경계, Guardrail, 도구별 IAM |
| 19 | 신뢰성 | DLQ + 경보, 멱등 쓰기, 원자적 트랜잭션, 성능 저하 모드(degraded mode) |
| 20 | 성능 효율성 | Gateway 시맨틱 검색, Memory 요약 주입, KB 검색 |
| 21 | 비용 최적화 | `model/load.py` 우선순위 기반 모델 라우팅 (LOW는 Haiku) |
| 22 | 지속 가능성 | 종량제 Runtime(ARM64), 로그 보존 2주, Memory 30일 만료 |

---

## 1. 도입: 왜 에이전트에 Well-Architected를 따로 적용하나 (슬라이드 1–3)

### 1.1 시나리오 소개 (3분)

이 모듈 전체에서 쓸 "평가 대상 시스템"을 먼저 보여 줍니다. `images/high-level-arch.png`나 `images/demo.gif`를 띄우고 흐름을 한 줄씩 짚습니다.

```
외부 시스템(Jira/PagerDuty 등) ─ 티켓 JSON ─▶ SNS 토픽
  ─▶ Trigger Lambda (필드 검증 · DDB 멱등 저장 · 실패 시 DLQ)
  ─▶ AgentCore Runtime (Strands 에이전트, 컨테이너)
       ① Guardrail로 PII·프롬프트 공격 정제
       ② Memory에서 이 요청자의 과거 장애 요약 조회
       ③ 우선순위로 모델 선택 (LOW → Haiku, 그 외 → Sonnet)
       ④ Gateway(MCP)로 도구 연결
       ⑤ LLM이 진단: lookup_user → get_process_info → query_kb → create_change_request
       ⑥ 결과를 DynamoDB에 기록  ⑦ EventBridge로 TicketResolved 발행
  ─▶ AgentCore Gateway (IAM 인증 · 시맨틱 검색 · Cedar Policy Engine)
       ─▶ Lambda 도구 4개 ─▶ DynamoDB 4개 테이블 / Bedrock Knowledge Base(S3 Vectors)
```

**강조할 점:** 이 에이전트는 **사람이 보지 않는 상태에서 이벤트 하나로 시작해, 변경 요청(Change Request)을 실제로 기록하는 시스템**입니다. 채팅봇보다 자율성이 높고, 그래서 Well-Architected 관점의 점검이 필요합니다.

### 1.2 이 샘플을 고른 이유

- README가 직접 "AgentCore 서비스 6종"(Runtime, Gateway+Policy, Memory, Identity, Observability, Evaluations)과 "복원력 기능 10종"을 표로 정리해 둡니다(`README.md:160-184`).
- `docs/design-decisions.md`에 **ADR 10개**가 있습니다. 각 ADR에 "왜"와 "트레이드오프"가 적혀 있어서, Well-Architected 리뷰에서 "이 결정의 트레이드오프는?"을 물을 때 근거로 쓸 수 있습니다.
- README의 "Scale for Production" 절(`README.md:736`)이 **개발 설정에서 프로덕션 설정으로 바꿀 항목**을 나열해 두었습니다. 슬라이드 11의 체크리스트와 바로 연결됩니다.

### 1.3 슬라이드 3의 5가지 고려 사항을 이 시스템에 대입하기 (5분)

수강생에게 "이 시스템에서 각 항목은 어디에 해당하는가?"를 먼저 묻고 아래 표로 정리합니다.

| 슬라이드 3 고려 사항 | 이 샘플에서의 모습 | 구현 위치 |
|---|---|---|
| 자율적 의사 결정 → **강력한 거버넌스** | LLM이 스스로 `create_change_request`를 호출할지 결정 | Cedar 정책 `RequireReasonForChangeRequest` (`agentcore/agentcore.json`의 `policyEngines`) |
| 비결정적 행동 → **포괄적 모니터링** | 같은 티켓이라도 도구 호출 순서·횟수가 달라질 수 있음 | OTEL 자동 계측(`Dockerfile` CMD), 티켓 ID 스팬 속성(`main.py:427-440`) |
| 컨텍스트 관리 → **성능과 비용** | 과거 장애를 전부 넣지 않고 **요약 상위 5개**만 프롬프트에 주입 | `memory/enrichment.py:36` `top_k=5`, SUMMARIZATION 전략(ADR-4) |
| 다중 구성 요소 조정 → **복원력 있는 통신** | SNS → Lambda → Runtime → Gateway → Lambda로 이어지는 여러 단계 | DLQ, 멱등 쓰기, Gateway 실패 시 성능 저하 모드(`mcp_client/client.py:150`) |
| 지속적 학습 → **평가 프레임워크** | 정답이 하나로 정해지지 않는 진단 결과 | 온라인 평가 4종, 샘플링 100%(`agentcore.json`의 `onlineEvalConfigs`) |

> **참고:** 이 샘플은 **단일 에이전트**입니다. "다중 에이전트 조정" 항목은 여기서는 "다중 *구성 요소* 조정"으로 바꿔 설명하고, 본격적인 멀티 에이전트는 §5 설계 활동에서 다룹니다.

---

## 2. Well-Architected Framework 적용 (슬라이드 4–9)

### 2.1 6개 핵심 요소 (슬라이드 5)

슬라이드 5에서는 WA 문서 링크를 보여 준 뒤, 이 샘플의 **요소별 "가장 대표적인 한 줄"** 만 미리 보여 주고 상세 내용은 부록(§4)으로 넘깁니다.

| 핵심 요소 | 이 샘플의 대표 구현 한 줄 |
|---|---|
| 운영 우수성 | `agentcore.json` 하나에 Runtime·Memory·Gateway·Policy·Eval을 선언하고 `agentcore deploy` 한 번으로 배포 |
| 보안 | Gateway 앞단의 Cedar Policy Engine + 진입점 Guardrail + 도구 Lambda별 최소 권한 IAM |
| 신뢰성 | Trigger Lambda의 DLQ + DLQ 적체 경보, 도구 연결 실패 시 LLM 단독 모드로 성능 저하 |
| 성능 효율성 | Gateway 시맨틱 검색(`enableSemanticSearch: true`), 과거 장애는 요약만 주입 |
| 비용 최적화 | 티켓 우선순위로 모델 선택: LOW는 Haiku, MEDIUM 이상은 Sonnet (ADR-8) |
| 지속 가능성 | 활성 시간만 과금되는 Runtime, DynamoDB 온디맨드, 로그 2주 보존, Memory 30일 만료 |

### 2.2 Generative AI Lens: "필요한 경우에만 대리권을 높인다" (슬라이드 6)

이 원칙을 코드로 보여 주기 가장 좋은 곳은 `main.py`의 메인 흐름입니다. **무엇을 LLM에게 맡기고 무엇을 코드로 고정했는지** 나눠 보면 원칙이 바로 보입니다.

| 단계 | 누가 하나 | 위치 | 이유 |
|---|---|---|---|
| 입력 검증, DDB 저장 | 코드 (Trigger Lambda) | `ticket_event_handler.py:52-107` | 판단이 필요 없는 일 |
| PII·프롬프트 공격 정제 | 코드 (Guardrail API) | `main.py:262-291`, `:460-467` | 보안 경계는 결정적이어야 함 |
| 과거 장애 조회 | 코드 (Memory API) | `main.py:475-478` | 항상 실행해야 하는 단계 |
| 모델 선택 | 코드 (규칙) | `model/load.py:15-30` | 우선순위라는 명시적 신호가 있음 |
| **진단, 도구 선택, 조치 여부 판단** | **LLM** | `main.py:561-570` | 여기만 추론이 필요함 |
| 결과 저장, 이벤트 발행 | 코드 | `main.py:590-604` | LLM이 "저장했다"고 말하는 것을 믿지 않음 |
| 결과가 비면 실패 처리 | 코드 | `main.py:575-581` | 자동 종결 대신 사람 검토로 넘김 |

**핵심 메시지:** 에이전트라고 해서 모든 단계를 LLM에게 맡기지 않습니다. 이 샘플에서 LLM이 정하는 것은 **"어떤 도구를 어떤 순서로 호출하고, 조치를 할지 말지"** 뿐입니다. 나머지는 워크플로처럼 코드로 고정되어 있습니다.

> **토론 질문:** "`SYSTEM_PROMPT`(`main.py:93-115`)가 도구 호출 순서 1→2→3→4를 이미 지시하고 있습니다. 그렇다면 이것은 에이전트입니까, 워크플로입니까?"
> 답의 방향: 순서는 프롬프트로 *권장*할 뿐 강제하지 않습니다. `get_process_info`는 "티켓에 서비스 이름이 있을 때만", `create_change_request`는 "런북이 근거가 될 때만" 호출하는 **조건부 판단**이 LLM에게 남아 있습니다. 이 정도가 "필요한 만큼의 대리권"입니다.

### 2.3 Agentic AI Security Scoping Matrix (슬라이드 7)

**이 샘플의 위치: 감독되는 대리권 (Scope 3)**

- 실행은 외부 이벤트(SNS 티켓)가 시작합니다. 에이전트가 스스로 작업을 만들지는 않으므로 Scope 4(전체 대리권)는 아닙니다.
- 그런데 시작된 뒤에는 `create_change_request`라는 **쓰기 작업을 사람 승인 없이** 실행합니다. 그래서 Scope 2(규정된 대리권)도 아닙니다.

| 수준을 바꾸려면 | 필요한 변경 | 샘플 기준 구체적 방법 |
|---|---|---|
| Scope 3 → **Scope 2**로 낮추기 | 쓰기 작업 전에 사람 승인 | `create_change_request.py`가 `status: "applied"` 대신 `"pending_approval"`을 기록하고, 승인 시스템이 EventBridge 이벤트를 받아 처리 |
| Scope 3 안에서 통제 강화 | 정책을 실제로 적용 | `agentcore.json`의 `policyEngineConfiguration.mode`를 `LOG_ONLY` → `ENFORCE` |
| Scope 4로 높인다면 필요한 것 | 자체 시작, 지속 모니터링 | 이상 탐지 시 에이전트가 스스로 티켓 생성 → 이때는 행동 드리프트 탐지, 속도 제한, 킬 스위치가 필수 |

**핵심 메시지:** 슬라이드 노트대로 "대부분의 프로덕션 시스템은 Scope 2나 3에서 시작"합니다. 이 샘플이 Policy Engine을 `LOG_ONLY`로 두는 이유(ADR-7: "막기 전에 무엇이 막힐지 먼저 본다")도 같은 맥락입니다.

### 2.4 에이전틱 AI용 Well-Architected 원칙 6가지 (슬라이드 8)

슬라이드 노트의 마지막 질문("관찰할 수 있습니까? 제어할 수 있습니까? …")을 이 샘플에 그대로 던집니다.

| 원칙 | 질문 | 샘플의 답 | 빈틈 |
|---|---|---|---|
| **관찰성** | 관찰할 수 있는가? | OTEL 자동 계측 + `ticket.id`, `ticket.priority`, `ticket.requester_id`, `ticket.mode` 스팬 속성(`main.py:430-438`). 단계별 SSE 이벤트(`_stage_event`, `main.py:313`) | 도구 실행 시간 훅(`main.py:66-81`)이 **프롬프트 모드에서만** 등록됨(`:383-384`). 티켓 처리 경로(`:515`)에는 없음 |
| **제어 가능성** | 제어할 수 있는가? | Cedar 정책, Gateway를 거치지 않으면 도구 호출 불가, 도구 Lambda의 입력 검증(`create_change_request.py:56-90`) | 정책이 `LOG_ONLY`라 실제로 막지는 않음 |
| **진실성·강건성** | 정확하고, 이상 입력에 견디는가? | 런북(KB) 근거가 있을 때만 조치하도록 지시. 잘못된 페이로드는 구조화된 실패 응답(`main.py:417-423`). 결과가 비면 자동 종결하지 않고 `Failed` 처리(`:577-581`) | 응답이 런북 내용과 일치하는지 검증하는 단계 없음 (온라인 평가 `Correctness`로 사후 확인만 가능) |
| **공정성** | 사용자 그룹별로 다르게 대하지 않는가? | 모델 라우팅 기준이 **사용자가 아니라 티켓 우선순위** | `priority`를 요청자가 직접 넣음 → 우선순위를 부풀리면 더 좋은 모델을 받게 됨. 반대로 LOW로 분류된 사용자 그룹이 체계적으로 낮은 품질을 받는지 모니터링 필요 |
| **투명성** | 동작이 문서화되어 있는가? | ADR 10개(`docs/design-decisions.md`), 단계별 아키텍처 문서(`docs/ARCHITECTURE.md`), 변경 요청에 `reason` 필드 기록 | 최종 해결 코멘트는 사고 과정을 빼도록 지시함 → 감사용 근거는 트레이스에서 확인해야 함 |
| **거버넌스** | 관리되고 있는가? | 정책을 코드로 선언(`policyEngines`), `validationMode` 설정, 온라인 평가로 지속 모니터링 | 정책 변경 승인 절차나 AWS Config 규칙은 없음 |

> **강사 팁:** "공정성" 행은 수강생이 잘 떠올리지 못합니다. "우선순위 필드를 누가 채우는가?"라고 물으면, 비용 최적화 설계(ADR-8)가 공정성 문제와 연결된다는 점을 스스로 찾아냅니다. 해결책은 우선순위를 요청자 입력 대신 **분류기(Haiku)가 다시 판정**하게 하는 것입니다.

### 2.5 통합 모범 사례 (슬라이드 9)

슬라이드 9의 다섯 항목을 이 샘플의 구성 요소에 하나씩 대응시킵니다.

| 슬라이드 9 항목 | 샘플 구현 | 위치 |
|---|---|---|
| 처음부터 관찰성을 고려하여 설계 | 컨테이너 CMD가 처음부터 `opentelemetry-instrument`로 시작. Trigger Lambda도 X-Ray `ACTIVE` | `Dockerfile` 마지막 줄, `infra-construct.ts:441` |
| 모든 통합 계층에 WA 원칙 적용 | 모든 DynamoDB 테이블에 PITR·암호화, S3에 `enforceSSL`·퍼블릭 차단 | `infra-construct.ts:89-133` |
| MCP로 에이전트-도구 통신 표준화 | 내부 도구는 Gateway(MCP), Jira는 Atlassian Remote MCP. 에이전트는 둘 다 같은 `MCPClient`로 사용 | `mcp_client/client.py`, `mcp_client/jira.py` |
| Gateway를 중앙 통합 허브로 | Lambda 4개를 Gateway 대상으로 등록. 도구 추가는 스키마 + `agentcore add gateway-target` | `agentcore.json`의 `agentCoreGateways`, `tool-schemas/` |
| 적절한 연결 관리 | SNS(수신) + SQS DLQ(비동기 실패 보관) + EventBridge(결과 라우팅). DB는 DynamoDB라 연결 풀 관리가 필요 없음 | ADR-3, ADR-5 |

**연결 관리 보충:** 슬라이드는 "데이터베이스에는 RDS Proxy"를 말합니다. 이 샘플은 ADR-5에서 DynamoDB를 골라 **연결 관리 문제를 아예 없앴습니다.** "만약 사내 CMDB가 RDS라면?"을 물으면, 도구 Lambda 앞에 RDS Proxy를 두는 구성으로 자연스럽게 이어집니다.

**Gateway 허브의 확장 예 (`README.md:746-767`):** Jira MCP 서버도 Gateway 대상(`--type mcp-server`)으로 등록하면 정책·시맨틱 검색·인증이 한 곳에 모입니다. 단, Gateway의 MCP 서버 대상은 2LO(client credentials)만 지원하므로 **사용자 위임(3LO)이 필요한 Jira는 이 샘플처럼 에이전트에서 직접 연결**합니다. "허브가 항상 정답은 아니다"라는 트레이드오프 사례로 쓰기 좋습니다.

---

## 3. 프로덕션 준비 상태 (슬라이드 10–11)

### 3.1 배포 준비 상태 검증 체크리스트를 샘플에 적용하기

슬라이드 11의 4개 열을 그대로 쓰고, 각 칸에 샘플의 현재 상태를 표시합니다. ✅ 구현됨, ⚠️ 부분 구현 또는 개발 설정, ❌ 없음.

| 영역 | 항목 | 상태 | 샘플 근거 / 해야 할 일 |
|---|---|---|---|
| **성능** | 부하 테스트 | ❌ | `scripts/e2e_test.py`는 티켓 1건의 기능 테스트. 동시 티켓 N건을 SNS에 발행하는 부하 테스트 필요 |
| | 기준 설정 | ⚠️ | 도구 Lambda 타임아웃 15초, KB 30초, Trigger 30초(`infra-construct.ts`). 에이전트 전체 처리 시간 목표(SLO)는 정의되지 않음 |
| | 벤치마킹 | ⚠️ | Haiku/Sonnet 라우팅은 있으나 두 모델의 품질·지연 비교 데이터 없음 → 온라인 평가 점수를 `priority`별로 나눠 비교 |
| **보안** | 정책 테스트 | ⚠️ | Cedar 정책 2개가 `LOG_ONLY`. ENFORCE 전 로그에서 "막혔을 호출"을 확인해야 함 |
| | IAM 검토 | ⚠️ | 도구별 최소 권한은 ✅. 그러나 `GuardrailAccess`가 `guardrail/*`, Logs가 `log-group:*`, Jira Identity가 `*` (`cdk-stack.ts:302-345`, 코드에 TODO 주석 있음) |
| | 취약성 스캔 | ❌ | 컨테이너 이미지 스캔(ECR/Inspector), 의존성 스캔 설정 없음 |
| **모니터링** | CloudWatch 대시보드 | ⚠️ | GenAI Observability 콘솔은 자동 제공. 경보는 DLQ 적체·Trigger 오류 2개뿐(`infra-construct.ts:459-477`), 알림(SNS) 연결 없음 |
| | X-Ray 추적 | ✅ | Trigger Lambda `ACTIVE`, Runtime OTEL + X-Ray 전파(`OTEL_PROPAGATORS=baggage,tracecontext,xray`) |
| | AgentCore Evaluations | ✅ | 내장 평가기 4개, 샘플링 100% |
| | AgentCore Observability | ✅ | Transaction Search를 커스텀 리소스로 자동 활성화(`cdk-stack.ts:368`, `lambdas/infra/transaction_search.py`) |
| **규정 준수** | 규제 요구 사항 | ⚠️ | Guardrail로 PII 익명화·차단. 다만 `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true`라 **프롬프트 원문이 트레이스에 남음** |
| | 데이터 레지던시 | ⚠️ | 모델 ID가 `us.` 교차 리전 추론 프로필 → 요청이 미국 내 여러 리전에서 처리될 수 있음 |
| | AWS Config | ❌ | 규칙 없음 |

> **강사 팁:** "규제 요구 사항" 행의 메시지 내용 캡처는 꼭 짚습니다. 관찰성(전부 남기기)과 개인정보 보호(남기지 않기)가 충돌하는 지점입니다. 이 샘플은 Guardrail이 **모델 입력 전에** 먼저 정제하므로 트레이스에는 정제된 내용이 남지만, 도구 응답(사용자 프로필 등)은 Guardrail을 거치지 않습니다(ADR-10의 트레이드오프).

### 3.2 개발 설정에서 프로덕션 설정으로: README "Scale for Production"

`README.md:736-744`의 목록을 WA 요소별로 다시 분류하면 체크리스트가 됩니다.

| README 항목 | WA 요소 | 바꿀 곳 |
|---|---|---|
| `DESTROY_ON_DELETE=false` | 신뢰성 | `.env` → `infra-construct.ts`의 `removalPolicy` |
| `exceptionLevel: DEBUG` → `NONE` | 보안 | `agentcore.json` Gateway 설정 (오류 상세를 에이전트에 노출하지 않음) |
| 온라인 평가 샘플링 100% → 10% | 비용 최적화 | `agentcore.json`의 `samplingRate` |
| VPC 모드 (`networkMode: "VPC"`) | 보안 | `agentcore.json` Runtime 설정 + 서브넷·보안 그룹 |
| 경보에 SNS 알림 추가 | 운영 우수성 | `infra-construct.ts`의 `cloudwatch.Alarm`에 `addAlarmAction` |
| Policy Engine `ENFORCE` | 보안 | `agentcore.json`의 `policyEngineConfiguration.mode` |
| 라우팅 기준 조정 (MEDIUM도 Haiku) | 비용 최적화 | `model/load.py` |

**핵심 메시지:** 프로덕션 전환의 대부분이 **코드 변경이 아니라 선언형 설정(`agentcore.json`, `.env`) 변경**입니다. 이것이 운영 우수성 슬라이드 17의 "코드가 아닌 아티팩트도 버전 관리하라"와 연결됩니다.

---

## 4. 부록: 핵심 요소별 설계 전략을 샘플로 확인하기 (슬라이드 16–22)

각 슬라이드의 "AWS를 사용한 접근 방식" 열을 그대로 따라가며, 샘플에 구현된 것과 빈틈을 구분합니다. 설계 활동(§5) 중에 필요한 요소만 골라 써도 됩니다.

### 4.1 운영 우수성 (슬라이드 17)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 다중 구성 요소 배포 | Runtime 변경 불가 버전, Memory로 상태 유지, 코드 외 아티팩트 관리 | 에이전트 코드·프롬프트·모델 ID·메모리 전략·평가 설정이 **모두 리포지토리 안 선언 파일**에 있음(`agentcore.json`, `main.py`). CDK 단일 스택으로 원자적 배포(ADR-9) | Runtime 엔드포인트를 버전별로 나눈 점진적 롤아웃 없음. 프롬프트가 코드 안 상수라 프롬프트만 따로 바꿀 수 없음 |
| 지속적 품질 평가 | AgentCore Evaluations (LLM 심판) | `Builtin.Correctness`, `Helpfulness`, `ToolSelectionAccuracy`, `GoalSuccessRate`. 결과 조회는 `scripts/evaluate.py` | 점수 하락 시 경보·롤백 같은 **품질 게이트** 없음 |
| 다중 계층 관찰성 | AgentCore Observability + CloudWatch | OTEL 자동 계측, 비즈니스 속성 스팬, X-Ray 전파, Transaction Search 자동 활성화 | 비즈니스 지표(해결률, 재발률)를 지표로 내보내지 않음. `recurring_incident_count`(`main.py:611-621`)는 응답에만 있음 |

**보여 줄 코드: 비즈니스 ID를 트레이스에 연결** (`main.py:430-438`)

```python
current_span = otel_trace.get_current_span()
if current_span and current_span.is_recording():
    current_span.set_attribute("ticket.id", ticket_id)
    current_span.set_attribute("ticket.priority", priority)
    current_span.set_attribute("ticket.requester_id", requester_id)
```

"티켓 INC-001이 왜 실패했나?"라는 운영 질문을 Transaction Search에서 `ticket.id`로 바로 찾을 수 있게 해 줍니다. 슬라이드의 "인프라 지표 + AI 품질 + 비즈니스 결과를 연결"하는 가장 작은 단위입니다.

**개선 과제 (5분 토론):** "온라인 평가 `GoalSuccessRate`가 0.7 아래로 떨어지면 무엇이 일어나야 합니까?" → 평가 결과 로그 그룹(`/aws/bedrock-agentcore/evaluations/results/...`)에 지표 필터 + 경보 → 배포 파이프라인이 직전 Runtime 버전으로 되돌림.

### 4.2 보안 (슬라이드 18)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 정책 우선 액세스 제어 | AgentCore Policy (Cedar), 로그 전용 모드로 먼저 검증 | `ITIncidentPolicyEngine`이 Gateway에 `LOG_ONLY`로 연결. 정책 2개 | ENFORCE 전환. 정책이 도구 이름 수준에 머물러 있음(예: CRITICAL 티켓만 변경 허용 같은 조건 없음) |
| 다중 계층 자격 증명 전파 | Cognito(사용자), AgentCore Identity(에이전트), IAM(리소스) | 3개 인증 경계: ① Runtime 인바운드 SigV4, ② Gateway 아웃바운드 `AWS_IAM` 또는 `CUSTOM_JWT`(Identity M2M), ③ Jira `USER_FEDERATION`(3LO) (`docs/authentication-guide.md`) | 요청자(`requester_id`)는 페이로드 값일 뿐 **인증된 신원이 아님** → 권한 교집합(사용자 ∩ 에이전트) 계산 불가 |
| 프라이빗 네트워크 연결 | VPC, PrivateLink, 엔드포인트 정책 | 없음 (기본 PUBLIC) | `networkMode: "VPC"` + Gateway·Bedrock·DynamoDB VPC 엔드포인트 |

**보여 줄 설정: Cedar 정책** (`agentcore/agentcore.json`)

```cedar
// 모든 도구 호출 허용 (기본 허용 + 로그)
permit(principal, action, resource is AgentCore::Gateway);

// 사유(reason) 없이 변경 요청을 만들면 거부
forbid(principal, action, resource is AgentCore::Gateway)
when { context has "toolName" && context.toolName == "create-change-request"
       && !(context has "reason") };
```

설명 순서:
1. `forbid`는 `permit`보다 우선합니다. 그래서 "기본 허용 + 위험 작업만 거부" 패턴이 됩니다.
2. `reason` 필드는 도구 스키마(`tool-schemas/create-change-request.json`)에서는 **선택 항목**입니다. 스키마는 느슨하게, 정책은 엄격하게 두어 "거버넌스 규칙을 도구 코드가 아니라 정책 계층에서 관리"하는 예입니다.
3. 지금은 `LOG_ONLY`라 위반이 로그에만 남습니다. 동시에 도구 Lambda마다 IAM 권한이 따로 있어서(`lookup_user`는 읽기 전용, `create_change_request`만 쓰기) 정책이 꺼져 있어도 **심층 방어**가 유지됩니다(ADR-7).

**보여 줄 코드: 아웃바운드 인증 전환** (`mcp_client/client.py:124-147`)

```python
if GATEWAY_AUTH_MODE == "CUSTOM_JWT":
    return _create_custom_jwt_client()   # @requires_access_token(auth_flow="M2M")
# 기본: 요청마다 SigV4 서명 (자격 증명이 교체되어도 동작)
return MCPClient(lambda: streamablehttp_client(GATEWAY_URL, auth=_create_sigv4_auth()))
```

**핵심 메시지:** 에이전트 코드는 `client_secret`을 보지 않습니다. AgentCore Identity가 토큰을 발급하고 데코레이터가 주입합니다. 슬라이드의 "에이전트별 자격 증명에 AgentCore Identity 사용"이 이것입니다.

**보안 보충: Guardrail은 어디에 걸려 있나** (`infra-construct.ts:303-335`, `main.py:460-467`)

- 이메일·전화·이름·IP는 `ANONYMIZE`, 주민번호·카드번호·AWS 키는 `BLOCK`, 프롬프트 공격 필터 `HIGH`.
- 티켓의 **제목과 설명 둘 다** 정제합니다. 주석(`main.py:451-454`)에 "제목에 PII가 있으면 우회된다"는 이유가 적혀 있습니다. 작은 부분이지만 "모든 입력 경로를 확인하라"는 좋은 예입니다.
- Guardrail 호출이 실패하면 **원문을 그대로 통과**시킵니다(`main.py:289-291`). 가용성을 택한 설계(fail-open)입니다. "보안 경계가 fail-open이어도 되는가?"를 토론 주제로 던지세요.

### 4.3 신뢰성 (슬라이드 19)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 다중 에이전트 장애 격리 | Runtime 세션 격리, 다중 AZ, 회로 차단기 | Runtime이 호출마다 고유 세션 ID(`event-{id}-{uuid}`, `ticket_event_handler.py:113`)로 격리. 도구는 Lambda별로 격리(ADR-2). 동시 요청 간 타이밍 데이터 섞임 방지에 `ContextVar` 사용(`main.py:53`) | 회로 차단기 없음 |
| 지능형 오류 복구 | 타임아웃 계층, 점진적 복구 (재시도 → 대체 → 캐시 → 사람) | 아래 "점진적 복구 4단계" 표 참고 | 에이전트 실행 전체의 타임아웃 없음 |
| 프로덕션 복원력 모니터링 | 가드레일, 트레이스 디버깅, 오류율·지연·이상 도구 순서 경보 | DLQ 적체 경보, Trigger 오류 경보, 트레이스 | 에이전트 `Failed` 비율, p95 지연, 비정상 도구 순서에 대한 경보 없음 |

**슬라이드의 점진적 복구 4단계를 샘플에서 찾기**

| 슬라이드 단계 | 샘플 구현 | 위치 |
|---|---|---|
| (1) 재시도 | SNS → Lambda 비동기 호출의 자동 재시도, 이후 DLQ | `infra-construct.ts:423-444` |
| (2) 대체 도구 | Gateway 또는 Jira 연결이 실패해도 **살아 있는 도구만으로** 진행 | `mcp_client/client.py:150-198` |
| (3) 캐시·대체 데이터 | 도구 초기화가 완전히 실패하면 **LLM 단독 모드**로 계속 | `main.py:521-538` |
| (4) 사람에게 에스컬레이션 | 결과가 비면 `Failed`로 기록, 자동 종결 금지. 재발 장애(30일 내 2건 이상)는 해결 코멘트에서 에스컬레이션 | `main.py:577-581`, `SYSTEM_PROMPT` 1번 항목 |

**보여 줄 코드: 멱등성과 원자성** — 신뢰성은 "실패해도 상태가 깨지지 않는 것"입니다.

```python
# Trigger: 같은 티켓이 두 번 와도 한 번만 저장 (ticket_event_handler.py:101-106)
tickets_table.put_item(Item=sanitized,
                       ConditionExpression="attribute_not_exists(ticket_id)")

# 도구: 변경 기록과 사용자 카운터를 한 트랜잭션으로 (create_change_request.py:102)
_ddb.transact_write_items(TransactItems=[{"Put": ...}, {"Update": ...}])
```

`create_change_request.py:95-101`의 주석이 "두 번 나눠 쓰면 일부만 성공할 수 있고, 모델이 재시도하면 변경 기록이 중복된다"고 이유를 설명합니다. **LLM은 같은 도구를 다시 호출할 수 있다**는 점이 일반 애플리케이션과 다른 신뢰성 고려 사항입니다.

**개선 과제: 타임아웃 계층 추가.** 슬라이드는 도구 5–30초, 추론 30–60초, 턴 2–5분, 세션 15분을 제시합니다. 샘플은 도구(Lambda 15/30초)만 있습니다. 에이전트 실행 전체에 상한을 두는 예:

```python
import asyncio

async with asyncio.timeout(300):   # 대화 턴 상한 5분 (Python 3.11+)
    async for event in agent.stream_async(user_query):
        ...
# TimeoutError → 기존 except 블록이 _fail_ticket()으로 사람 검토에 넘김
```

> **토론 질문:** "SNS → Lambda 재시도는 Runtime 호출이 실패했을 때 일어납니다. DDB 저장은 멱등이지만 Runtime 호출은 멱등입니까?" → 재시도 시 에이전트가 같은 티켓을 두 번 처리할 수 있습니다. `create_change_request` 앞에서 "이 티켓에 이미 변경 요청이 있는가"를 확인하거나, 티켓 상태를 `Processing`으로 조건부 갱신한 뒤 시작하는 방법을 토론합니다.

### 4.4 성능 효율성 (슬라이드 20)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 컨텍스트 윈도우 최적화 | Memory로 대화 기록 외부화, 프롬프트 캐싱, Strands 대화 관리자 | 과거 장애 **전체 대화가 아니라 요약 상위 5개**만 시스템 프롬프트에 주입(ADR-4, `enrichment.py:36`). 티켓 1건 = 세션 1개라 대화가 길어지지 않음 | 프롬프트 캐싱 없음. 대화 관리자는 Strands 기본값 |
| 다중 에이전트 성능 분산 | Runtime 종량제·자동 확장, 전문가 에이전트 독립 확장 | 단일 에이전트. Runtime이 세션 단위로 확장 | 분류(Haiku) → 해결(Sonnet) 에이전트 분리 시 독립 확장 가능 |
| 도구 설계 효율성 | Gateway 시맨틱 검색, 정보 집약형 도구, 중앙화, Lambda 프로비저닝 동시성 | `enableSemanticSearch: true`. `lookup_user`가 **프로필 + 쿼터 + 최근 30일 티켓을 한 번에** 반환(정보 집약형) | 프로비저닝 동시성 없음 (비동기 처리라 콜드 스타트 영향 작음, ADR-2) |

**보여 줄 코드: 정보 집약형 도구** (`lambdas/tools/lookup_user.py` 반환값)

```python
{"user_id": ..., "profile": user, "quotas": ...,
 "recent_tickets": [...], "recent_incident_count_30d": len(recent)}
```

도구를 `get_profile`, `get_quotas`, `get_recent_tickets` 3개로 쪼갰다면 LLM 왕복이 3번 필요하고, 매 왕복마다 컨텍스트 전체를 다시 처리합니다. **도구 하나가 판단에 필요한 정보를 한 번에 주는 것**이 슬라이드의 "단일 상호 작용에서 계층적 JSON 반환"입니다.

**메모리 설계 보충 (`memory/enrichment.py`)**
- SUMMARIZATION 전략은 `incidents/{actorId}/{sessionId}`에 저장하고, 조회는 `incidents/{requester_id}` **접두사**로 합니다. 그래서 한 사용자의 모든 세션 요약이 검색됩니다.
- 요약은 **비동기**로 만들어지므로 방금 제출한 티켓은 바로 보이지 않습니다. 그래서 `main.py:149-179`의 `_count_recent_incidents`가 DynamoDB를 직접 조회해 재발 횟수를 보완합니다. "Memory는 의미 검색용, 강한 일관성이 필요한 숫자는 DB"라는 역할 분담입니다.

**개선 과제: 프롬프트 캐싱.** 이 에이전트의 시스템 프롬프트와 도구 정의는 티켓마다 같으므로 캐싱 효과가 큽니다. Strands에서는 시스템 프롬프트를 콘텐츠 블록 목록으로 주고 캐시 지점을 표시하는 방식이 있습니다. 파라미터 이름은 Strands 버전마다 다를 수 있으니 수업 전에 설치된 버전(`uv.lock` 기준 `strands-agents 1.42.0`)의 문서를 확인하세요.

```python
agent = Agent(
    model=load_model(priority),
    system_prompt=[{"text": SYSTEM_PROMPT}, {"cachePoint": {"type": "default"}}],
    tools=tools,
)
```

주의: 이 샘플은 과거 장애 요약을 시스템 프롬프트 **뒤에 붙입니다**(`main.py:494`). 사용자마다 달라지는 부분이므로 캐시 지점은 **고정 부분과 가변 부분 사이**에 두어야 합니다. 컨텍스트 엔지니어링 모듈의 "정적 컨텍스트를 앞에" 원칙과 연결하세요.

### 4.5 비용 최적화 (슬라이드 21)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 토큰 소비 관리 | 프롬프트 캐싱, 슬라이딩 윈도우/요약, CloudWatch 지표와 예산 경보 | **모델 라우팅**: LOW는 Haiku, 그 외는 Sonnet. 메모리는 요약만 주입. 최종 응답은 3–6문장으로 제한(`SYSTEM_PROMPT`) | 토큰 사용량 경보, 예산 경보 없음 |
| 적절한 크기 조정 | Runtime 종량제, 계층형 보존, 테일 기반 샘플링 | Runtime 종량제, DynamoDB `PAY_PER_REQUEST`, Lambda 256MB, 로그 2주 | 온라인 평가 샘플링 **100%**, Transaction Search 인덱싱 **100%**(`cdk-stack.ts:427`) |
| 캐싱 및 재사용 | Gateway로 도구 중앙화, ElastiCache, CloudFront | Gateway에 도구를 모아 다른 에이전트도 재사용 가능(ADR-2) | 도구 결과 캐시 없음 (`get_process_info`는 자주 바뀌지 않으므로 후보) |

**보여 줄 코드: 비용 라우팅** (`model/load.py:15-30`)

```python
def load_model(priority: str = "MEDIUM") -> BedrockModel:
    model_id = AGENT_MODEL_ID          # Sonnet
    if priority == "LOW":
        model_id = FAST_MODEL_ID       # Haiku
    return BedrockModel(model_id=model_id)
```

설명 포인트:
1. ADR-8은 "단순 티켓을 약 10배 저렴하게"를 근거로 듭니다. 숫자보다 **"비싼 추론은 필요할 때만"** 이라는 원칙이 슬라이드 6(대리권은 필요할 때만)과 같은 구조라는 점을 짚습니다.
2. 라우팅 신호(`priority`)를 누가 정하는지가 공정성 문제와 연결됩니다(§2.4).
3. 모델 ID가 `agentcore.json`의 `envVars`에 있어서 **코드 수정 없이** 바꿀 수 있습니다.

**개선 과제: 슬라이드의 "테일 기반 샘플링"을 샘플에 적용하면?**
- 지금은 온라인 평가가 모든 트레이스를 LLM 심판으로 채점합니다(100%). 평가 비용이 에이전트 실행 비용에 비례해 커집니다.
- 1단계: `samplingRate`를 10–20%로 낮춤.
- 2단계: `Failed` 티켓과 재발 티켓은 항상 평가하고 싶다면? 온라인 평가는 비율 샘플링이므로, 실패 트레이스는 `ticket.id`로 찾아 **온디맨드 평가**로 따로 돌리는 구성을 토론합니다.
- 슬라이드의 계층형 보존(트레이스 7일, 지표 30일, 요약 1년)과 비교: 샘플은 Lambda 로그 2주, Memory 이벤트 30일, DLQ 14일입니다.

### 4.6 지속 가능성 (슬라이드 22)

| 슬라이드 고려 사항 | 슬라이드의 접근 방식 | 샘플 구현 | 빈틈 / 개선 과제 |
|---|---|---|---|
| 리전 선택 | 탄소 집약도 낮은 리전, 고객 탄소 발자국 도구 | 기본 `us-west-2` (`.env`, `config.py`) | 리전 선택 근거 문서화 없음 |
| 리소스 최적화 | Runtime 종량제, 미사용 리소스 파악, 비프로덕션 환경 중지 | 유휴 시 비용이 거의 없는 서버리스 구성(Runtime, Lambda, DynamoDB 온디맨드). `scripts/destroy.sh`로 전체 삭제 | 도구 Lambda가 기본 x86_64 아키텍처 |
| 수명 주기 관리 | 데이터 수명 주기 정책, 압축, Glacier 보관 | Memory 이벤트 30일 만료(`eventExpiryDuration: 30`), 로그 2주, DLQ 14일 | KB 버킷이 `versioned: true`인데 이전 버전 정리 규칙 없음(`infra-construct.ts:129-136`) |

**연결 포인트:** AgentCore Runtime 컨테이너는 ARM64(Graviton)에서 실행됩니다. 그런데 도구 Lambda는 아키텍처를 지정하지 않아 x86_64입니다. 한 줄로 바꿀 수 있는 개선 과제입니다.

```typescript
const lookupUserFn = new lambda_.Function(this, 'LookupUserFn', {
  runtime: lambda_.Runtime.PYTHON_3_11,
  architecture: lambda_.Architecture.ARM_64,   // 추가
  ...
});
```

**핵심 메시지:** 지속 가능성 요소의 개선은 대부분 **비용 최적화와 같은 방향**입니다(유휴 자원 제거, 보존 기간 단축, 작은 모델 사용). Haiku 라우팅도 같은 작업을 더 적은 연산으로 하므로 지속 가능성 개선입니다.

---

## 5. 아키텍처 설계 활동 (슬라이드 12–13)

### 5.1 진행 방식

슬라이드 노트대로 **코딩이 아닌 설계 실습**입니다. 이 샘플은 단일 에이전트이므로 정답지로 쓰지 말고, **"이미 검증된 패턴의 재료 상자"** 로 씁니다. 수강생이 각 마커에서 막히면 "IT 장애 에이전트에서는 이 문제를 어떻게 풀었나요?"라고 되묻습니다.

시나리오 요구 사항(슬라이드 13 노트): 감독되는 대리권, 멀티 에이전트(주문·추천·기술 지원·청구), PII·결제 정보, 가용성 99.9%, PCI-DSS.

### 5.2 마커별로 이 샘플에서 가져올 패턴

| 마커 | 논의 주제 (슬라이드 노트) | 이 샘플에서 가져올 패턴 | 전자상거래로 옮길 때 바꿀 점 |
|---|---|---|---|
| **1** 사용자 → 오케스트레이터 | 인증, 입력 검증, 속도 제한 | Trigger의 필수 필드 검증 + **허용 필드 목록**(`ticket_event_handler.py:79-89`), 진입점 Guardrail | 이벤트가 아니라 사용자 채팅 → Runtime 인바운드 `CUSTOM_JWT`(Cognito). `requester_id`를 페이로드가 아니라 **JWT의 `sub`** 에서 가져와야 함 |
| **2** 오케스트레이터 처리 | 컨텍스트 관리, 결정 로직, 정책, 관찰성 | 메모리 요약 상위 N개 주입, 우선순위 기반 모델 라우팅, 비즈니스 ID 스팬 속성 | 라우팅 대상이 모델이 아니라 **전문가 에이전트**. 라우팅 결정 근거를 스팬 속성(예: `route.agent`)으로 기록 |
| **3** 오케스트레이터 → 사용자 | 응답 검증, 콘텐츠 필터, 감사, SLA | 결과가 비면 자동 종결 금지(`main.py:577-581`), 단계별 SSE 스트리밍(`_stage_event`) | 출력 쪽 Guardrail 추가(샘플은 입력만). 카드 번호 등 PCI 데이터는 `BLOCK` |
| **4** 오케스트레이터 → 전문가 | 에이전트 간 통신, 장애 처리 | 도구 연결 실패 시 성능 저하 모드(`get_all_mcp_clients_safe`) | 전문가 에이전트 하나가 죽어도 나머지로 응답(예: 추천 에이전트 장애 시 주문 조회는 계속). 회로 차단기 |
| **5** 전문가 → 도구 | 도구 액세스 정책, VPC, 데이터 분류 | 도구별 Lambda + 최소 권한 IAM, Cedar 정책, 도구 입력 검증 | Cedar로 "청구 에이전트는 `billing_tool`만" 정책. 결제 도구는 VPC 내부 + PrivateLink |

### 5.3 활동 4개 영역별 모범 답안 골격

강사용 정리입니다. 수강생 발표 뒤 빠진 항목을 채워 주는 용도로 씁니다.

**① 다중 에이전트 및 컨텍스트 설계**
- 오케스트레이터는 분류만 하는 가벼운 모델(Haiku), 청구·기술 지원처럼 추론이 필요한 전문가는 Sonnet. 샘플의 `load_model(priority)`를 에이전트 단위로 확장한 형태입니다.
- 컨텍스트 전략: **기록**(Memory 요약, 샘플 ADR-4), **선택**(Gateway 시맨틱 검색으로 필요한 도구만), **압축**(요약 상위 N개), **분리**(전문가마다 자기 도구와 자기 컨텍스트만).

**② 프로덕션 아키텍처**
- 에이전트별 Runtime(독립 확장, 세션 격리). 공통 도구는 하나의 Gateway에 모음.
- 비동기 작업(환불 처리 등)은 샘플처럼 이벤트로 분리: SNS/SQS + DLQ, 결과는 EventBridge로 발행.
- 선언형 구성(`agentcore.json`) + CDK 단일 배포로 시작하고, 규모가 커지면 공유 인프라 스택과 에이전트 스택을 분리(ADR-9의 트레이드오프).

**③ 보안 설계**
- 3개 인증 경계(샘플 `docs/authentication-guide.md`)를 그대로 적용: 사용자 → 오케스트레이터(Cognito JWT), 에이전트 → Gateway(Identity M2M), 외부 SaaS(3LO).
- Cedar 정책은 `LOG_ONLY`로 시작해 위반 로그 확인 후 `ENFORCE`(ADR-7).
- 감사 로그 1년 보존(PCI-DSS) → 샘플의 2주 보존과 대비해 "규정이 보존 기간을 결정한다"는 점을 강조.

**④ 관찰성 및 평가**
- 세션 수준 `GoalSuccessRate`(문제가 해결됐나), 트레이스 수준 `Correctness`·`Helpfulness`, 스팬 수준 `ToolSelectionAccuracy`(마커 5). 샘플의 평가기 4개가 이 세 수준을 모두 덮고 있습니다.
- 샘플링은 10–20% + 실패·불만 세션은 온디맨드 평가.
- 경보: 샘플의 DLQ 경보 외에 에이전트별 오류율, p95 지연, 토큰 사용량.

### 5.4 노트의 "일반적인 함정"을 샘플로 설명하기

| 함정 | 샘플에서 피한 방법 또는 남은 위험 |
|---|---|
| 초기 과도 엔지니어링 / 확장 고려 부족 | 단일 스택·단일 에이전트로 시작하고, 확장 경로를 ADR에 명시(ADR-9) |
| 보안을 나중에 추가 | Guardrail, 도구별 IAM, 정책 엔진이 첫 배포부터 포함 |
| 멀티 에이전트 관찰성 격차 | 단일 에이전트라도 Trigger Lambda부터 X-Ray로 이어 트레이스가 끊기지 않게 함 |
| 비용을 고려하지 않은 컨텍스트 관리 | 전체 대화 대신 요약 주입. 다만 프롬프트 캐싱은 빠짐 |
| 오케스트레이션의 단일 장애점 | Gateway가 사실상 단일 경로 → 장애 시 LLM 단독 모드로 내려가지만, 이때는 도구 없이 답하므로 품질이 떨어짐 |

---

## 6. 모듈 요약과 지식 확인 (슬라이드 14–15)

### 6.1 요약 (2분)

학습 목표 2개를 이 샘플로 다시 말합니다.
1. **WA에 부합하는 설계 전략을 사용한다:** 이 샘플의 ADR 10개가 각각 어느 WA 요소의 결정인지 말할 수 있다.
2. **WA 핵심 요소로 에이전틱 아키텍처를 평가한다:** §3 체크리스트로 이 샘플의 빈틈(정책 LOG_ONLY, VPC 없음, 평가 100%, 실행 타임아웃 없음 등)을 찾을 수 있다.

### 6.2 보충 문제 (질문 시간용)

**Q1.** 이 샘플은 Policy Engine을 `LOG_ONLY`로 배포합니다. 그런데도 `lookup_user` 도구가 사용자 테이블에 쓰기를 할 수 없는 이유는?
> 정답: 도구 Lambda마다 IAM 역할이 따로 있고 `lookup_user`에는 `grantReadData`만 있기 때문(`infra-construct.ts:360-361`). 정책 계층과 IAM 계층이 겹치는 심층 방어. (보안)

**Q2.** 티켓 우선순위로 모델을 고르는 설계가 비용 외에 영향을 주는 WA 원칙은?
> 정답: 공정성. 요청자가 우선순위를 정하므로 부풀리거나, LOW 사용자 그룹이 체계적으로 낮은 품질을 받을 수 있음. 지속 가능성에도 긍정적 영향. (비용 최적화, 공정성)

**Q3.** 에이전트가 해결 코멘트를 만들지 못하면 이 샘플은 티켓을 어떻게 처리합니까? 왜 그렇게 합니까?
> 정답: `Failed`로 기록(`main.py:577-581`). 자리표시자 문구로 자동 종결하면 사람 검토가 필요한 티켓이 조용히 닫히기 때문. (신뢰성, 제어 가능성)

**Q4.** 과거 장애 수를 Memory 요약에서만 세지 않고 DynamoDB도 조회하는 이유는?
> 정답: SUMMARIZATION 요약은 비동기로 만들어져 직후 재제출된 티켓을 반영하지 못함. 강한 일관성이 필요한 수치는 DB에서 가져옴(`main.py:149-179`). (성능 효율성, 진실성)

**Q5.** 이 샘플을 Scoping Matrix의 Scope 2로 바꾸려면 가장 먼저 무엇을 바꿔야 합니까?
> 정답: `create_change_request`가 바로 적용(`status: applied`)하지 않고 승인 대기로 기록, 사람이 승인한 뒤 적용. (보안, 거버넌스)

---

## 7. 권장 진행 시간표 (75분 기준)

| 시간 | 슬라이드 | 내용 | 자료 |
|---|---|---|---|
| 0–8분 | 1–3 | 도입, 시나리오 소개, 5가지 고려 사항 대입 | §1, 데모 GIF |
| 8–25분 | 4–9 | 6개 요소 미리 보기, 대리권 원칙(코드 vs LLM 표), Scoping Matrix, 원칙 6가지, 통합 모범 사례 | §2 |
| 25–35분 | 10–11 | 배포 준비 체크리스트를 샘플에 채우기 (수강생 참여) | §3 |
| 35–60분 | 12–13 | 설계 활동 (마커별 토론, 필요할 때 부록 슬라이드 참조) | §5, §4 |
| 60–70분 | 16–22 | 설계 활동에서 덜 다룬 요소 위주로 부록 정리 | §4 |
| 70–75분 | 14–15 | 요약, 보충 문제, 질문 | §6 |

> 시간이 부족하면 §4는 설계 활동 중 질문이 나올 때마다 해당 요소만 펼치고, 따로 시간을 잡지 않습니다(슬라이드 16 노트의 사용법과 같음).

---

## 8. 데모 준비

### 8.1 배포와 실행 (수업 전날 배포 권장, 약 10–15분 소요)

```bash
cp .env.example .env              # CDK_DEFAULT_ACCOUNT 설정
cd agentcore/cdk && npm install && cd ../..
./scripts/deploy.sh

./scripts/publish_ticket.sh                     # 샘플 티켓 (U-1003, HIGH)
agentcore logs --since 5m                       # 단계별 로그
./scripts/show_ticket.sh INC-20260604-001       # status=Resolved 확인
python scripts/evaluate.py --hours 24           # 온라인 평가 점수
```

### 8.2 슬라이드별로 띄워 둘 화면

| 슬라이드 | 화면 |
|---|---|
| 6, 8 | `main.py:450-623` (메인 흐름), `images/demo.gif` |
| 7, 18 | `agentcore/agentcore.json`의 `policyEngines` |
| 9 | `agentcore/agentcore.json`의 `agentCoreGateways`, `tool-schemas/` |
| 11 | CloudWatch GenAI Observability 콘솔 (트레이스에서 `ticket.id`로 검색) |
| 17 | `scripts/evaluate.py` 출력 |
| 19 | `infra-construct.ts:423-477` (DLQ, 경보) |
| 21 | `model/load.py` |

### 8.3 재발 감지 데모 (Memory + 신뢰성)

같은 요청자로 티켓을 두세 번 보내면 에이전트가 재발로 판단해 에스컬레이션합니다. `ticket_id`만 바꿔 다시 발행하세요.

```bash
sed 's/INC-20260604-001/INC-20260604-002/' seed-data/sample_ticket.json > /tmp/t2.json
./scripts/publish_ticket.sh /tmp/t2.json
```

> **리허설 팁:** Memory 요약은 비동기로 만들어집니다. 바로 재제출하면 메모리 요약 수는 0일 수 있지만, `lookup_user`의 최근 30일 티켓 수와 `_count_recent_incidents`가 재발을 잡습니다. 데모 중 "Memory가 비어 있는데 왜 재발로 판단했나?"라는 질문이 나오면 §4.4의 역할 분담을 설명할 기회로 쓰세요.

---

## 9. 이 샘플에 없는 것 (슬라이드로만 설명)

아래 항목은 샘플 코드에 구현이 없습니다. 슬라이드와 이 문서의 개선 과제 스니펫으로 설명합니다.

- Runtime 버전·엔드포인트를 나눈 점진적 롤아웃, 평가 점수 기반 자동 롤백 (슬라이드 17)
- VPC 배포, PrivateLink, 엔드포인트 정책 (슬라이드 18)
- 회로 차단기, 다중 AZ 상태 확인 설정, 다중 리전 모델 배포 (슬라이드 19)
- Bedrock 프롬프트 캐싱, Strands 대화 관리자 직접 설정, Lambda 프로비저닝 동시성 (슬라이드 20)
- 토큰·예산 경보, ElastiCache, CloudFront, 테일 기반 샘플링 (슬라이드 21)
- 고객 탄소 발자국 도구, S3 Glacier 보관 (슬라이드 22)
- 부하 테스트, 취약성 스캔, AWS Config 규칙 (슬라이드 11)
- 실제 멀티 에이전트 오케스트레이션 (슬라이드 13): 이 샘플은 단일 에이전트입니다. 멀티 에이전트 비교가 필요하면 같은 폴더의 `01.A2A-multi-agent-incident-response`(A2A)나 `02.SRE-agent`(supervisor + 전문가 4개)를 함께 보여 주세요.

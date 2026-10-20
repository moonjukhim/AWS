# 강의 자료: 04-Observability × IT Incident Response Agent

> **슬라이드:** `04-Observability.pptx` (프로덕션 모니터링, 관찰성 및 평가, 56장, 예상 50분)
> **실습 코드:** `04.it-incident-response-agent` (IT 장애 티켓 자동 처리 에이전트)
> **용도:** 슬라이드의 개념을 이 샘플의 실제 코드·설정·명령어에 연결해 설명하기 위한 강사용 자료

이 모듈은 세 부분입니다. ① 모니터링 아키텍처(세션·트레이스·스팬), ② 관찰성 통합(OTel/ADOT, Transaction Search, 경보, 비용), ③ AgentCore Evaluations(내장·사용자 지정, 온라인·온디맨드). 이 샘플은 **세 부분을 한 시스템에서 모두 구현**하고 있어서, 티켓 하나를 넣고 **트레이스 → 스팬 → 평가 점수** 순서로 따라가며 보여 줄 수 있습니다.

---

## 0. 한 장 요약: 슬라이드와 코드 매핑

| 슬라이드 | 개념 | 샘플에서 보여줄 곳 |
|---|---|---|
| 4 | 지표·로그·트레이스 | 경보 2개(`infra-construct.ts:459-477`), `logger.info` 단계 로그, OTEL 트레이스 |
| 5 | 에이전트 성능 지표 | `Builtin.ToolSelectionAccuracy`(도구 선택 정확성), Memory `top_k=5`(컨텍스트 사용률) |
| 6 | 모니터링 성숙도 4단계 | §1.3: 이 샘플은 2단계 완성, 3단계 일부 |
| 8 | 세션 → 트레이스 → 스팬 | Trigger가 티켓마다 새 Runtime 세션 생성(`ticket_event_handler.py:113`) |
| 9 | 추론 프로세스 추적 | `ticket.*` 스팬 속성(`main.py:430-438`), 메시지 내용 캡처 env var |
| 10–13 | 레시피 에이전트 예시 | 같은 그림을 티켓 처리 흐름으로 다시 그리기 (§2.1) |
| 14 | 도구 실패와 점진적 성능 저하 | `get_all_mcp_clients_safe`(`mcp_client/client.py:150`), LLM 단독 모드(`main.py:521-538`) |
| 15 | 세부 수준 선택 | "티켓이 느리다" 문제를 세 수준으로 추적하는 시나리오 (§2.4) |
| 16–17 | AgentCore 서비스별 관찰성 | Memory, Gateway, Policy(LOG_ONLY), Identity, Evaluations 모두 사용 |
| 18 | 다중 구성 요소 가시성 | `OTEL_PROPAGATORS=baggage,tracecontext,xray` + Trigger Lambda X-Ray `ACTIVE` |
| 21–23 | OpenTelemetry, ADOT | `Dockerfile` CMD `opentelemetry-instrument`, `aws-opentelemetry-distro 0.17.1` |
| 24 | 에이전트 트레이스 예시 | `agentcore traces get <traceId>`로 실제 JSON 내려받아 비교 |
| 25 | 원격 측정 내보내기 | `agentcore.json` `envVars`, Transaction Search 커스텀 리소스(`transaction_search.py`) |
| 26, 31 | 서드 파티 내보내기 | 샘플에 없음 → `envVars`에 넣을 위치만 보여 줌 |
| 27–29 | 경보 계층, 루프 탐지 | DLQ·Trigger 오류 경보만 있음 → 루프 탐지 경보는 개선 과제 |
| 30, 32 | 관찰성 비용 | 평가 샘플링 100%, 스팬 인덱싱 100%, 로그 보존 2주 |
| 34–36 | 테스트와 평가의 차이 | `scripts/e2e_test.py`(상태 확인) vs 온라인 평가(품질 확인) |
| 37–41 | Evaluations, 내장 평가기, 세 수준 | `onlineEvalConfigs`의 평가기 4개 = 세션·트레이스·스팬 세 수준 |
| 42–43 | 사용자 지정 평가기 | 샘플에 없음 → `agentcore add evaluator`로 "런북 근거성" 평가기 실습 |
| 44–45, 48 | 온라인 평가 | `agentcore.json`의 `onlineEvalConfigs`, `scripts/evaluate.py` |
| 46–47 | 온디맨드 평가 | `agentcore run eval --trace-id ...` |
| 49 | 평가에서 조치로 | `kb-docs/` 런북 3개로 골든 데이터세트 구성 (§4.7) |

---

## 1. 모니터링 아키텍처 도입 (슬라이드 1–7)

### 1.1 시나리오 소개 (3분)

이 모듈에서 "관찰할 대상"을 먼저 보여 줍니다. `images/observability-flow.png`와 `images/demo.gif`를 띄웁니다.

```
SNS 토픽 ─▶ Trigger Lambda ──(X-Ray ACTIVE)──▶ AgentCore Runtime (OTEL 자동 계측)
                                                  │  ① Guardrail  ② Memory 조회
                                                  │  ③ 모델 선택  ④ Gateway(MCP) 연결
                                                  │  ⑤ 에이전틱 루프: LLM ↔ 도구 4개
                                                  │  ⑥ DDB 기록  ⑦ EventBridge 발행
                                                  ▼
                       CloudWatch: 지표(bedrock-agentcore) · 로그(runtimes/...) · 스팬(aws/spans)
                                                  ▼
                       Online Evaluation: 평가기 4개(LLM 심판) ─▶ evaluations/results/... 로그
```

**강조할 점:** 이 에이전트는 **사람이 보지 않는 곳에서** 돌아갑니다. 채팅봇은 사용자가 이상한 답을 보고 신고하지만, 이 에이전트의 결과는 티켓 테이블에 조용히 기록됩니다. 그래서 관찰성과 평가가 "실패를 알아차리는 유일한 수단"입니다. 슬라이드 35 노트의 "고객 불만이 쏟아진 후에야 개발자가 인지하는" 상황을 막는 장치들이 이 샘플 곳곳에 있습니다.

### 1.2 관찰성 3요소를 샘플에서 찾기 (슬라이드 4)

| 요소 | 슬라이드 설명 | 이 샘플의 구현 | 위치 |
|---|---|---|---|
| **지표** | 상태를 수치로 한눈에 | AgentCore Runtime 자동 지표(`bedrock-agentcore` 네임스페이스), DLQ 깊이·Trigger 오류 경보 | `infra-construct.ts:459-477` |
| **로그** | 의사 결정 이면의 "이유" | 단계별 `logger.info`: `"Processing ticket ..."`, `"Retrieved %d past-incident summaries"`, `"Guardrail intervened"`, `"Running in degraded mode"` | `main.py`, `memory/enrichment.py` |
| **트레이스** | 요청의 엔드 투 엔드 여정 | OTEL 자동 계측 + X-Ray 전파. 비즈니스 ID(`ticket.id`)를 스팬 속성으로 붙임 | `Dockerfile`, `agentcore.json`, `main.py:430-438` |

**세 요소를 함께 쓰는 예 (슬라이드 4 노트의 시나리오를 샘플로 바꿔 설명):**
1. **지표:** DLQ 깊이 경보가 울립니다.
2. **로그:** Trigger Lambda 로그에서 `"Failed to invoke runtime for INC-..."`를 찾습니다.
3. **트레이스:** 실패하지 않은 티켓이라면 Transaction Search에서 `ticket.id = INC-...`로 검색해 어느 스팬에서 시간이 걸렸는지 봅니다.

### 1.3 모니터링 성숙도 여정: 이 샘플은 몇 단계인가 (슬라이드 6)

슬라이드 노트대로 "수강생에게 자기 조직의 위치를 평가하게" 하기 전에, **이 샘플을 먼저 평가**해 보여 줍니다.

| 단계 | 내용 | 이 샘플 | 근거 |
|---|---|---|---|
| 1. 기본 모니터링 | 원격 측정 데이터 수집 | ✅ | Runtime 자동 계측, 로그 그룹, `aws/spans` |
| 2. 중간 모니터링 | 분석과 인사이트 | ✅ | GenAI Observability 대시보드, `scripts/evaluate.py` 요약 |
| 3. 고급 관찰성 | 상관관계, 이상 탐지 | ⚠️ 일부 | `ticket.id`로 비즈니스 이벤트와 트레이스 연결, SNS → Lambda → Runtime 트레이스 연결. **이상 탐지 없음** |
| 4. 사전 예방적 관찰성 | 자동 근본 원인 파악 | ❌ | 경보에 조치(SNS 알림·자동 복구) 연결 없음 |

**토론 질문:** "3단계로 올리려면 무엇이 하나 더 있으면 될까요?" → 정답 예: 평가 점수와 지연 시간에 CloudWatch 이상 탐지(Anomaly Detection) 경보. 슬라이드 5의 "정적 임계값 대신 적응형 기준선"과 같은 이야기입니다.

### 1.4 에이전틱 시스템 모니터링이 다른 이유 (슬라이드 5, 7)

슬라이드 7의 "신뢰성 격차?", "비용 사각지대?"를 이 샘플에 대입합니다.

- **신뢰성 격차:** 이 에이전트는 Gateway 연결이 실패해도 **오류 없이** LLM 단독 모드로 티켓을 "해결"합니다(`main.py:521-538`). HTTP 200, 상태 `Resolved`. 기존 APM은 정상으로 봅니다. 그러나 도구 없이 쓴 해결 코멘트는 근거가 없습니다. **이것이 에이전트 고유의 "보이지 않는 실패"** 입니다.
- **비용 사각지대:** 같은 티켓이라도 LLM이 `query_kb`를 몇 번 부르느냐에 따라 토큰 사용량이 달라집니다. 요청 수 기반 비용 모델로는 보이지 않습니다.

슬라이드 5의 에이전트 성능 지표를 샘플에 대응시키면 다음과 같습니다.

| 슬라이드 5 지표 | 샘플에서 측정하는 방법 |
|---|---|
| 도구 선택 정확성 | `Builtin.ToolSelectionAccuracy` (스팬 수준 평가기) |
| 추론 효율성 | 트레이스의 도구 호출 수, LLM 호출 수. `SYSTEM_PROMPT`가 기대하는 최대 4회와 비교 |
| 컨텍스트 사용률 | Memory 주입량(`top_k=5`, `enrichment.py:36`), 스팬의 입력 토큰 수 |
| 협업 효율성 | 단일 에이전트라 해당 없음. 대신 Gateway 오버헤드 지연 시간 |

---

## 2. 세션·트레이스·스팬 (슬라이드 8–18)

### 2.1 레시피 에이전트 그림을 티켓 처리로 다시 그리기 (슬라이드 10–13)

슬라이드 10–13은 같은 그림을 반복합니다. 두 번째 반복(슬라이드 11)부터는 **이 샘플 버전으로 화이트보드에 겹쳐 그리면** 수강생이 실제 코드와 연결하기 쉽습니다.

| 레시피 에이전트 (슬라이드) | IT 장애 에이전트 (샘플) |
|---|---|
| 클라이언트 | Trigger Lambda (`invoke_agent_runtime`) |
| 프롬프트 "건강에 좋은 치킨 파스타…" | `_build_query()`가 만든 "Ticket INC-… from user U-1003 (priority HIGH)…" (`main.py:294-302`) |
| LLM 계획 → 웹 검색 도구 선택 | LLM이 `lookup_user` → `get_process_info` → `query_kb` 순으로 선택 |
| `web_search` 도구 실행 | Gateway(MCP) → Lambda 도구 → DynamoDB / Knowledge Base |
| 종합된 결과 | 3–6문장 해결 코멘트 → DDB 기록, EventBridge 발행 |

**차이점 하나:** 레시피 에이전트는 도구를 한 번 부르지만, 이 에이전트는 **에이전틱 루프를 3–4바퀴** 돕니다. 그래서 스팬 수가 훨씬 많고, 슬라이드 13의 "LLM 계획이 지연 시간의 43%" 같은 분석이 더 중요해집니다.

### 2.2 세션·트레이스·스팬 계층 (슬라이드 8, 11–13)

| 계층 | 이 샘플에서 무엇인가 | 확인 위치 |
|---|---|---|
| **세션** | Trigger가 티켓마다 만드는 `runtimeSessionId` = `event-{ticket_id}-{uuid}` (`ticket_event_handler.py:113`) | CloudWatch GenAI Observability 대시보드 (세션 지표, 자동) |
| **트레이스** | 그 세션 안의 `InvokeAgentRuntime` 요청 1회 = 티켓 1건 처리 | CloudWatch Transaction Search (ADOT 필요) |
| **스팬** | Guardrail 호출, Memory 조회, LLM 호출, 도구 호출, DDB 쓰기, EventBridge 발행 | `aws/spans` 로그 그룹 (ADOT 필요) |

**짚어 줄 점: 이 샘플에서는 세션 1개 = 트레이스 1개입니다.**
- 슬라이드 8은 "세션에는 여러 트레이스가 있다"고 설명합니다. 채팅 에이전트는 그렇습니다.
- 이 샘플은 이벤트 기반이라 티켓마다 새 세션을 만듭니다. 그래서 세션 수준 지표(세션 수, 평균 시간)가 사실상 **티켓 처리량과 티켓당 처리 시간**이 됩니다.
- 여러 티켓을 묶어 보는 "사용자 단위" 관점은 세션이 아니라 **Memory의 `actorId`(=`requester_id`)** 가 담당합니다. Runtime 세션 ID와 Memory 세션 ID(`ticket_id`)가 서로 다르다는 점도 함께 보여 주세요(`main.py:517`).

> **토론 질문:** "세션 수준 평가기 `GoalSuccessRate`는 세션 단위로 채점합니다. 이 샘플처럼 세션이 한 턴뿐이면 트레이스 수준 평가와 무엇이 다릅니까?" → 거의 같아집니다. 채팅형 에이전트로 바꾸면 차이가 커진다는 점을 설명하세요.

### 2.3 추론 프로세스 추적 (슬라이드 9)

슬라이드 9는 "X-Ray 세그먼트와 주석으로 추론 메타데이터를 캡처하라"고 합니다. 이 샘플은 세 가지 방법을 씁니다.

**① 비즈니스 컨텍스트를 스팬 속성으로** (`main.py:430-438`)

```python
from opentelemetry import trace as otel_trace

current_span = otel_trace.get_current_span()
if current_span and current_span.is_recording():
    current_span.set_attribute("ticket.id", ticket_id)
    current_span.set_attribute("ticket.priority", priority)
    current_span.set_attribute("ticket.requester_id", requester_id)
    current_span.set_attribute("ticket.mode", "jira" if is_jira_mode else "ddb")
```

`ticket.priority`가 있으면 "LOW 티켓(Haiku)과 HIGH 티켓(Sonnet)의 지연 시간·평가 점수 비교"가 가능해집니다. 모델 라우팅이라는 **결정의 결과**를 트레이스에서 나눠 볼 수 있게 하는 것입니다.

**② 프롬프트와 응답 내용을 캡처** (`agentcore.json`의 `envVars`)

```json
{ "name": "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "value": "true" }
```

LLM에 들어간 시스템 프롬프트(과거 장애 요약 포함)와 도구 선택 응답이 스팬에 남습니다. "에이전트가 왜 `create_change_request`를 불렀나?"를 사후에 볼 수 있습니다. 대신 **티켓 내용이 트레이스에 남는다**는 개인정보 문제가 생깁니다. 이 샘플은 Guardrail이 모델 호출 전에 PII를 익명화하므로 일부 완화됩니다(`main.py:460-467`).

**③ 단계 이벤트 스트리밍** (`main.py:313-315`)

`_stage_event()`가 `guardrail → memory → tools → diagnose → tool(×N) → persist → emit` 단계마다 JSON을 내보냅니다. 트레이스와 별개로, 호출자가 **실시간으로** 진행 상황을 볼 수 있는 경로입니다.

**개선 과제: 결정 지점에 사용자 지정 스팬 추가.** 지금은 "과거 장애가 몇 건이었고, 그래서 에스컬레이션했는가"가 스팬 속성으로 남지 않습니다. 이렇게 추가할 수 있습니다.

```python
tracer = otel_trace.get_tracer("it-incident-agent")

with tracer.start_as_current_span("memory.enrichment") as span:
    past_incidents = retrieve_past_incidents(requester_id=requester_id, query=...)
    span.set_attribute("memory.past_incident_count", len(past_incidents))
    span.set_attribute("memory.recurring", len(past_incidents) >= 2)
```

### 2.4 세부 수준 선택: "티켓 처리가 느리다" 시나리오 (슬라이드 15)

슬라이드 15 노트의 "점진적 문제 해결 예"를 이 샘플 버전으로 진행합니다.

| 단계 | 어디를 보나 | 이 샘플에서 확인할 것 |
|---|---|---|
| 1. 세션 수준 | GenAI Observability 대시보드 | 평균 세션 시간이 평소보다 긴가? 오류율은? |
| 2. 트레이스 수준 | Transaction Search에서 지연 시간 > N초인 트레이스 필터 | `ticket.priority`별로 나눠 보면 HIGH(Sonnet)만 느린가? 도구 호출이 4번보다 많은가? |
| 3. 스팬 수준 | `aws/spans`에서 해당 트레이스의 스팬 | LLM 호출이 느린가, Gateway → `query_kb` Lambda가 느린가(KB 조회 Lambda는 타임아웃 30초로 가장 김, `infra-construct.ts:405`)? |

**명령어로 보여 주기:**

```bash
agentcore traces list                 # 최근 트레이스 목록
agentcore traces get <traceId>        # 트레이스를 JSON 파일로 내려받기
agentcore logs --since 10m            # Runtime 로그
```

### 2.5 도구 실패와 점진적 성능 저하 (슬라이드 14)

슬라이드 14의 "웹 검색 시간 초과 → 기존 지식으로 복구"와 같은 구조가 이 샘플에 두 겹으로 있습니다.

**① 도구 공급자 단위의 성능 저하** (`mcp_client/client.py:150-198`)

```python
try:
    gateway_client = get_streamable_http_mcp_client()
    ...
except Exception as exc:
    warnings.append(f"Gateway MCP client failed to initialize: ...")
# Jira도 같은 방식 — 실패한 공급자만 빠지고 나머지로 진행
```

**② 에이전트 단위의 성능 저하** (`main.py:521-538`): 도구 초기화가 완전히 실패하면 `tools=[]`로 에이전트를 다시 만들어 LLM 단독으로 계속합니다.

**관찰성 관점의 빈틈 (꼭 짚을 것):** 슬라이드 14는 실패한 스팬에 `error.type`, `error.message`, `span.status: Error`가 남는다고 설명합니다. 이 샘플의 성능 저하는 **로그 경고(`"Running in degraded mode"`)로만** 남고, 트레이스 속성이나 응답 JSON에는 표시되지 않습니다. 그래서 대시보드에서 "도구 없이 처리된 티켓"을 골라낼 수 없습니다.

```python
# 개선 예: 성능 저하를 트레이스와 결과에 남기기
if tool_warnings:
    current_span.set_attribute("agent.degraded", True)
    current_span.set_attribute("agent.tool_warnings", "; ".join(tool_warnings))
```

> **강사 팁:** 이 빈틈은 §4의 평가와 연결됩니다. 도구 없이 쓴 코멘트는 `ToolSelectionAccuracy`와 `Correctness` 점수가 낮게 나오므로, **트레이스에 표시가 없어도 평가가 잡아냅니다.** "관찰성과 평가는 서로의 빈틈을 메운다"는 메시지로 마무리하세요.

### 2.6 AgentCore 서비스별 관찰성 (슬라이드 16–17)

이 샘플은 6개 서비스 중 5개를 씁니다. 각 서비스에서 **무엇을 봐야 하는지**를 샘플 기준으로 정리합니다.

| 서비스 | 샘플에서의 사용 | 관찰할 것 | 샘플 관련 주의점 |
|---|---|---|---|
| **Memory** | `retrieve_memories`(조회), `AgentCoreMemorySessionManager`(기록), SUMMARIZATION 전략 | 메모리 레코드 검색 지연, 추출 실패 | 요약은 **비동기 추출** → 방금 넣은 티켓은 바로 조회되지 않음. 그래서 `_count_recent_incidents`가 DDB로 보완(`main.py:149-179`) |
| **Gateway** | Lambda 대상 4개, 시맨틱 검색, `AWS_IAM` 인증 | 도구별 호출 수, 대상 실행 시간, 인증 실패 | `exceptionLevel: DEBUG` → 오류 상세가 에이전트에게 그대로 전달됨(개발용) |
| **Policy** | Cedar 정책 2개, `LOG_ONLY` | 허용/거부 결정, 결정 정책, 불일치 정책, 적용 모드 | 슬라이드 17대로 **Gateway 추적을 켜야** 정책 스팬이 남음. 샘플 CDK에는 Gateway 로그·추적 전달 설정 코드가 없으므로 콘솔에서 확인 |
| **Identity** | `CUSTOM_JWT` 모드(M2M), Jira 3LO(선택) | 토큰 발급 실패, 공급자별 호출 | 기본 `AWS_IAM` 모드에서는 Identity 호출이 없음 |
| **Evaluations** | 내장 평가기 4개, 샘플링 100% | 평가기별 점수 추세 | §4에서 자세히 |
| Code Interpreter, Browser | 사용 안 함 | — | — |

**Policy 관찰 실습 아이디어:** `RequireReasonForChangeRequest` 정책은 `reason` 없이 `create_change_request`를 부르면 위반입니다. 도구 스키마에서 `reason`은 선택 항목이므로 LLM이 빼먹을 수 있습니다. `LOG_ONLY` 모드라 호출은 성공하지만, 정책 스팬에 "거부되었을 결정"이 남습니다. **"ENFORCE로 바꾸기 전에 관찰성으로 영향을 측정한다"** 는 흐름을 보여 주기 좋습니다.

### 2.7 다중 구성 요소의 가시성 (슬라이드 18)

이 샘플은 단일 에이전트지만, 요청이 **SNS → Trigger Lambda → Runtime → Gateway → Lambda 도구**로 여러 홉을 거칩니다. 홉마다 트레이스가 끊기면 슬라이드 18의 문제가 그대로 생깁니다.

| 홉 | 트레이스를 잇는 장치 | 위치 |
|---|---|---|
| SNS → Trigger Lambda | Lambda X-Ray `ACTIVE` 추적 | `infra-construct.ts:441` |
| Trigger Lambda → Runtime | `OTEL_PROPAGATORS=baggage,tracecontext,xray` | `agentcore.json`의 `envVars` |
| Runtime → Gateway → Lambda | Gateway가 AgentCore 서비스 스팬 생성 | 자동 (Gateway 추적 활성화 필요) |

`infra-construct.ts:439-440`의 주석이 이유를 설명합니다: "이 설정이 없으면 트레이스가 Runtime에서 시작한다." 멀티 에이전트로 확장할 때도 같은 원리(전파 헤더 + 각 홉의 계측)가 필요하다고 연결하세요.

---

## 3. 관찰성 통합 (슬라이드 19–32)

### 3.1 OpenTelemetry와 ADOT (슬라이드 20–23)

이 샘플에서 OTel이 들어가는 곳은 딱 세 군데입니다. "에이전트 코드에 계측 코드를 거의 쓰지 않았다"는 점이 핵심입니다.

| 구성 요소 | 내용 | 위치 |
|---|---|---|
| ADOT 패키지 | `aws-opentelemetry-distro 0.17.1` | `app/ITIncidentAgent/pyproject.toml`, `uv.lock` |
| 자동 계측 진입점 | `CMD ["opentelemetry-instrument", "python", "-m", "main"]` | `app/ITIncidentAgent/Dockerfile` 마지막 줄 |
| 내보내기 설정 | OTLP, `http/protobuf`, 전파기, 메시지 캡처 | `agentcore/agentcore.json`의 `runtimes[].envVars` |

```json
{ "name": "OTEL_TRACES_EXPORTER", "value": "otlp" },
{ "name": "OTEL_EXPORTER_OTLP_PROTOCOL", "value": "http/protobuf" },
{ "name": "OTEL_METRICS_EXPORTER", "value": "none" },
{ "name": "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "value": "true" },
{ "name": "AGENT_OBSERVABILITY_ENABLED", "value": "true" },
{ "name": "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "value": "true" },
{ "name": "OTEL_AWS_APPLICATION_SIGNALS_ENABLED", "value": "true" },
{ "name": "OTEL_PROPAGATORS", "value": "baggage,tracecontext,xray" }
```

**슬라이드 23의 OTel 에코시스템 그림에 대입:** 애플리케이션 = Strands 에이전트, OTel = ADOT(`opentelemetry-instrument`), 백엔드 = CloudWatch(`aws/spans`, 로그 그룹), 프론트엔드 = GenAI Observability 콘솔.

> **실패 모드 (`docs/online-evaluation.md`):** 이 env var가 빠져도 배포는 성공하고 `aws/spans`에도 데이터가 쌓입니다. 하지만 HTTP·자격 증명 호출 같은 저수준 스팬만 남고 **`session.id`가 붙은 `gen_ai` 스팬이 없어서 온라인 평가가 영원히 실행되지 않습니다.** "관찰성 설정 실수는 조용히 실패한다"는 좋은 사례입니다.

### 3.2 실제 트레이스 들여다보기 (슬라이드 24)

슬라이드 24는 여행 에이전트의 예시 JSON입니다. 데모에서는 **이 샘플의 실제 트레이스**를 내려받아 같은 필드를 찾아봅니다.

```bash
agentcore traces list
agentcore traces get <traceId>     # JSON 파일로 저장
```

| 슬라이드 24 필드 | 실제 트레이스에서 찾을 것 |
|---|---|
| `session_id` | `event-INC-20260604-001-…` 형태 |
| `operation: InvokeAgentRuntime` | 자동 스팬 (ADOT 없이도 생김) |
| `request_payload.prompt` | 티켓 JSON (Guardrail 적용 전 원문) |
| `tools_used` | Gateway 도구 스팬들. 이름은 `<대상이름>___<도구이름>` 형식일 수 있으니 실제 값을 확인 |
| `latency_ms` | 보통 수십 초 (도구 3–4회 + LLM 여러 번) |
| (추가) `ticket.id`, `ticket.priority` | 샘플이 직접 붙인 사용자 지정 속성 |

### 3.3 AgentCore가 원격 측정 데이터를 내보내는 방법 (슬라이드 25)

| 계층 | 슬라이드 25의 내보내기 위치 | 이 샘플에서 확인 |
|---|---|---|
| 세션 | CloudWatch 지표 (`bedrock-agentcore` 네임스페이스) | 대시보드 |
| 트레이스·스팬 | CloudWatch Logs (`aws/spans`) | `scripts/e2e_test.py:37` `SPANS_LOG_GROUP = "/aws/spans"` |
| 애플리케이션 로그 | — | `/aws/bedrock-agentcore/runtimes/ITIncidentAgent…` (`e2e_test.py:36`) |
| 평가 결과 | — | `/aws/bedrock-agentcore/evaluations/results/ITIncidentAgent…` (`evaluate.py:27`) |

> 로그 그룹 이름은 문서와 콘솔에서 `aws/spans`, `/aws/spans`, `/aws/spans/default`로 조금씩 다르게 표기됩니다. 수업 전에 콘솔에서 실제 이름을 확인해 두세요.

**Transaction Search 자동 활성화** (`lambdas/infra/transaction_search.py`, `cdk-stack.ts:389-438`)

슬라이드 25는 "Runtime 호스팅 에이전트는 Transaction Search가 기본 활성화"라고 합니다. 그런데도 이 샘플은 **커스텀 리소스로 명시적으로 켭니다.** 이유를 설명하세요.
- Transaction Search는 **계정·리전 단위 설정**입니다. 새 계정에서는 꺼져 있을 수 있고, 꺼져 있으면 온라인 평가가 읽을 데이터가 없습니다.
- 커스텀 리소스가 하는 일은 두 가지입니다: `update_trace_segment_destination(Destination="CloudWatchLogs")`, 그리고 스팬 인덱싱 비율 설정(`IndexingPercentage`, 기본 100).
- 스택을 삭제해도 **끄지 않습니다**(`transaction_search.py:44-46`). 다른 에이전트가 쓰는 공유 설정이기 때문입니다.
- `onlineEvalConfigs`가 비어 있으면 이 커스텀 리소스도 만들지 않습니다(`cdk-stack.ts:367-369`). "평가를 쓸 때만 그 전제 조건을 켠다"는 설계입니다.

### 3.4 서드 파티 통합 (슬라이드 26, 31)

이 샘플은 **기본 CloudWatch 통합(슬라이드 31의 첫 번째 방식)** 만 씁니다. 다른 방식은 샘플에 없으므로 "어디를 바꾸면 되는지"만 보여 줍니다.

| 슬라이드 31 방식 | 이 샘플에 적용하려면 |
|---|---|
| ① 내장 CloudWatch 통합 (기본) | 현재 구성 그대로 |
| ② 서드 파티 계측 라이브러리 + ADOT (이중 관찰성) | `pyproject.toml`에 OpenInference 등 추가. ADOT는 그대로 CloudWatch로 보냄 |
| ③ ADOT 끄고 서드 파티만 / OTel Collector | 슬라이드 26의 env var를 `agentcore.json`의 `envVars`에 추가 |

```json
{ "name": "DISABLE_ADOT_OBSERVABILITY", "value": "true" },
{ "name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "https://<vendor-endpoint>" },
{ "name": "OTEL_SERVICE_NAME", "value": "it-incident-agent" }
```

**주의:** API 키 같은 비밀 값은 `envVars`(리포지토리에 커밋되는 파일)에 넣으면 안 됩니다. 이 샘플이 Jira `client_secret`을 AgentCore Identity에 맡기는 방식(README의 CUSTOM_JWT 절)과 같은 원칙을 적용해야 한다고 짚어 주세요. 또 ③을 택하면 **온라인 평가가 CloudWatch 스팬을 읽지 못한다**는 트레이드오프도 함께 설명합니다.

### 3.5 경보 계층과 루프 탐지 (슬라이드 27–29)

**슬라이드 27의 3계층 경보를 샘플에 대입**

| 계층 | 슬라이드 설명 | 샘플 구현 | 빈틈 |
|---|---|---|---|
| 1. 자동 응답 | 컨텍스트 새로 고침, 도구 재연결 | 도구 실패 시 성능 저하 모드, SNS → Lambda 자동 재시도 후 DLQ | 성능 저하가 외부에 알려지지 않음 |
| 2. 기술 팀 | 성능 문제, 시스템 진단 | `DLQDepthAlarm`, `TriggerErrorAlarm` (`infra-construct.ts:459-477`) | **경보에 알림 동작(SNS)이 없음** → 울려도 아무도 모름 |
| 3. 비즈니스 이해관계자 | 품질 문제 | 없음 | 평가 점수 하락 경보 필요 |

**슬라이드 28 루프 탐지를 샘플에 대입**

| 슬라이드 28 항목 | 샘플 상태 |
|---|---|
| 수명 주기 구성 (유휴 시간 제한, 최대 수명) | ❌ 설정 없음. `agentcore.json` 스키마에도 해당 필드가 없음(`agentcore/.llm-context/agentcore.ts`) → CDK `addPropertyOverride`로 추가해야 함 |
| 상태 확인 (`/ping`) | ✅ `BedrockAgentCoreApp`이 자동 제공 |
| 세션 지속 시간 이상, 호출 수 급증 | ❌ 경보 없음 |
| 반복되는 도구 사용 패턴 | ❌ 탐지 없음. `SYSTEM_PROMPT`가 도구 순서를 지시하므로 "같은 도구 5회 이상"이면 이상으로 볼 수 있음 |
| 토큰 사용 임계값 | ❌ 경보 없음 |

**개선 과제 1: 슬라이드 29 경보를 CDK로 옮기기**

슬라이드 29는 boto3 `put_metric_alarm`이지만, 이 샘플은 인프라를 CDK로 관리하므로 `infra-construct.ts`의 기존 경보 옆에 같은 스타일로 추가하는 것이 맞습니다.

```typescript
const alertTopic = new sns.Topic(this, 'AgentAlertTopic');

const loopAlarm = new cloudwatch.Alarm(this, 'AgentLoopDetection', {
  metric: new cloudwatch.Metric({
    namespace: 'bedrock-agentcore',
    metricName: 'Duration',
    statistic: 'Maximum',
    period: cdk.Duration.minutes(5),
    // dimensionsMap: 콘솔에서 Runtime 지표의 실제 차원 이름을 확인해 지정
  }),
  threshold: 30 * 60 * 1000,   // 30분 (ms)
  evaluationPeriods: 1,
  alarmDescription: 'Agent session exceeded 30 minutes — possible reasoning loop',
});
loopAlarm.addAlarmAction(new cw_actions.SnsAction(alertTopic));

// 기존 경보에도 알림 연결 (현재 샘플의 가장 큰 빈틈)
// dlqAlarm.addAlarmAction(new cw_actions.SnsAction(alertTopic));
```

> 샘플 경보는 `new cloudwatch.Alarm(...)`을 변수에 담지 않습니다. 알림을 붙이려면 변수로 받아야 합니다. `cw_actions`는 `aws-cdk-lib/aws-cloudwatch-actions`를 import해야 합니다.

**개선 과제 2: 수명 주기 구성.** 이 샘플은 티켓 하나를 처리하면 끝나므로 기본 최대 수명(8시간)이 너무 깁니다. 슬라이드 28 노트의 "일반적인 상호 작용은 2분" 기준이라면 유휴 시간 제한을 짧게 두는 것이 좋습니다. Runtime 리소스 속성 이름은 CloudFormation 문서에서 확인한 뒤 `cdk-stack.ts`의 기존 `addPropertyOverride` 블록(`:216-249`)에 추가합니다.

```typescript
cfnRuntime.addPropertyOverride('LifecycleConfiguration', {
  IdleRuntimeSessionTimeout: 300,   // 초
  MaxLifetime: 1800,                // 초
});
```

### 3.6 관찰성 비용 (슬라이드 30, 32)

이 샘플은 **데모용으로 모든 것을 100% 남기도록** 설정되어 있습니다. 슬라이드 30의 표에 대입하면 프로덕션 전환 목록이 바로 나옵니다.

| 슬라이드 30 전략 | 샘플 현재값 | 프로덕션 권장 | 바꿀 곳 |
|---|---|---|---|
| 샘플링 (평가 10–20%) | `samplingRate: 100` | 10–20 | `agentcore.json`의 `onlineEvalConfigs` |
| 헤드 기반 샘플링 (스팬 인덱싱) | `IndexingPercentage: 100` | 1–10 | `.env`의 `TXN_SEARCH_INDEXING_PERCENTAGE` (`cdk-stack.ts:427`) |
| 계층형 보존 | Lambda 로그 `TWO_WEEKS`, Memory 이벤트 30일 | 상세 7일 / 집계 30일 / 요약 1년 | `infra-construct.ts`의 `logRetention`, `eventExpiryDuration` |
| 테일 기반 샘플링 (오류 100%) | 없음 | 실패 티켓은 온디맨드 평가로 따로 | §4.5 |
| (추가) 메시지 내용 캡처 | `true` | 규정에 따라 판단 | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` |

**짚어 줄 점:**
- `docs/online-evaluation.md`는 "하루 100건 기준 월 5–15달러"라고 적어 두었습니다. 평가는 **LLM 심판 호출 비용**이므로 트래픽에 비례해 늘어납니다. 슬라이드 32의 "비용이 선형으로 늘지 않게"가 바로 샘플링 비율 이야기입니다.
- 메시지 내용 캡처를 끄면 비용과 개인정보 위험이 줄지만, `Correctness`·`Helpfulness` 평가기가 **채점할 내용이 없어집니다**(`online-evaluation.md`의 env var 표). 관찰성 깊이와 비용·규정 사이의 트레이드오프를 보여 주는 가장 구체적인 예입니다.

---

## 4. AgentCore Evaluations (슬라이드 33–49)

### 4.1 왜 테스트만으로는 부족한가 (슬라이드 34–36)

이 샘플에는 **테스트와 평가가 둘 다** 있어서 차이를 바로 비교할 수 있습니다.

| | `scripts/e2e_test.py` (기존 테스트) | 온라인 평가 (에이전트 평가) |
|---|---|---|
| 확인하는 것 | 티켓이 `status=Resolved`가 되었는가, 어떤 도구가 호출되었는가 | 해결 코멘트가 정확하고 유용한가, 도구 선택이 맞았는가 |
| 판정 | 통과/실패 | 0–1 점수 + 레이블 + 설명 |
| 실행 시점 | 배포 후 수동 | 모든(또는 샘플링된) 실제 트래픽 |

**슬라이드 35의 실패 지점을 이 샘플에 대입**

| 실패 유형 | 이 샘플에서 일어날 수 있는 모습 | 잡아내는 평가기 |
|---|---|---|
| 할루시네이션 | 런북에 없는 해결 방법을 코멘트에 씀 | `Correctness` (+ 사용자 지정 "런북 근거성", §4.4) |
| 잘못된 도구 선택 | `query_kb`를 건너뛰고 바로 `create_change_request` | `ToolSelectionAccuracy` |
| 컨텍스트 손실 | Memory 조회 실패가 경고 로그로만 남고(`enrichment.py`) 재발 감지 실패 | `GoalSuccessRate` (에스컬레이션 누락) |
| 잘못된 오류 처리 | 도구 없이 LLM 단독으로 "해결" | `ToolSelectionAccuracy`, `Correctness` |

**슬라이드 36의 "평가 수명 주기 이벤트"** 를 샘플의 실제 변경 지점에 대응시킵니다.

| 슬라이드 36 이벤트 | 샘플에서 바꾸는 곳 |
|---|---|
| 모델 업데이트 | `agentcore.json`의 `AGENT_MODEL_ID`, `FAST_MODEL_ID` |
| 소스 프롬프트 수정 | `main.py:93`의 `SYSTEM_PROMPT` |
| 도구 추가·제거 | `tool-schemas/`, `agentcore.json`의 Gateway `targets` |
| 새 에이전트 버전 | `agentcore deploy` |

이 중 무엇을 바꾸든 **온디맨드 평가(§4.5)로 먼저 확인**하고, 배포 후에는 **온라인 평가 추세**로 회귀를 봅니다.

### 4.2 이 샘플의 평가 구성 (슬라이드 37–38, 44–45)

**선언형 구성** (`agentcore/agentcore.json`)

```json
"onlineEvalConfigs": [{
  "name": "ITIncidentAgentEval",
  "agent": "ITIncidentAgent",
  "evaluators": [
    "Builtin.Correctness",
    "Builtin.Helpfulness",
    "Builtin.ToolSelectionAccuracy",
    "Builtin.GoalSuccessRate"
  ],
  "samplingRate": 100
}]
```

슬라이드 45의 스타터 툴킷 코드(`client.create_online_evaluation(...)`)와 같은 내용을 **코드 대신 설정 파일로** 선언한 것입니다. CLI로는 이렇게 추가합니다(`README.md:217-219`).

```bash
agentcore add online-eval --name ITIncidentAgentEval --runtime ITIncidentAgent \
  --evaluator Builtin.Correctness Builtin.Helpfulness \
              Builtin.ToolSelectionAccuracy Builtin.GoalSuccessRate \
  --sampling-rate 100
```

**슬라이드 38·44의 흐름을 샘플 리소스로 다시 그리기**

```
Trigger Lambda ─▶ Runtime(에이전트) ─▶ OTel 트레이스 ─▶ aws/spans
                                                         │ (Transaction Search가 전제)
                       OnlineEvaluationConfig ◀──────────┘ 샘플링(100%) + 세션 유휴 대기
                                │  평가기마다 Bedrock 모델(LLM 심판) 호출
                                ▼
          /aws/bedrock-agentcore/evaluations/results/ITIncidentAgent_ITIncidentAgentEval…
                                │
                 GenAI Observability 대시보드   ·   scripts/evaluate.py
```

**핵심 메시지 (슬라이드 38 노트):** "에이전트 코드를 변경하지 않는다." 이 샘플의 `main.py`에는 평가 관련 코드가 한 줄도 없습니다. 평가는 이미 수집하는 트레이스를 서비스 쪽에서 읽어 채점합니다.

> **시간 주의:** 결과가 나오기까지 **10–15분**이 걸립니다(세션 유휴 대기 약 5분 + 처리 시간, `docs/online-evaluation.md`). 데모 티켓은 강의 시작 전에 미리 넣어 두세요.

### 4.3 내장 평가기와 세 가지 수준 (슬라이드 39, 41)

이 샘플의 평가기 4개는 **슬라이드 39의 세 수준을 모두** 덮습니다.

| 수준 | 평가기 | 이 샘플에서 묻는 질문 |
|---|---|---|
| 세션 | `Builtin.GoalSuccessRate` | 티켓이 실제로 해결되었는가? 재발 장애면 에스컬레이션했는가? |
| 트레이스 | `Builtin.Correctness` | 해결 코멘트의 내용이 사실(런북, 사용자 정보)과 맞는가? |
| 트레이스 | `Builtin.Helpfulness` | 사용자가 다음에 무엇을 해야 하는지 알 수 있는가? |
| 스팬 | `Builtin.ToolSelectionAccuracy` | 각 단계에서 맞는 도구를 골랐는가? |

**결과 조회: `scripts/evaluate.py`가 하는 일**

```python
query = "fields @timestamp, @message | filter name = 'gen_ai.evaluation.result' ..."
# 각 결과에서 꺼내는 속성
"evaluator":   attrs.get("gen_ai.evaluation.name")
"score":       attrs.get("gen_ai.evaluation.score.value")
"label":       attrs.get("gen_ai.evaluation.score.label")
"explanation": attrs.get("gen_ai.evaluation.explanation")
"level":       attrs.get("gen_ai.evaluation_level")
```

설명 포인트:
1. 평가 결과도 **OTel 형식의 로그 레코드**(`gen_ai.evaluation.result`)입니다. 그래서 트레이스와 같은 방식으로 `trace_id`·`session_id`로 연결됩니다(슬라이드 37의 "통합 대시보드"가 가능한 이유).
2. `explanation`이 있어서 **"왜 0.3점인가"** 를 읽을 수 있습니다. 슬라이드 41의 "0.91 → 0.30 하락"을 보면 다음 단계는 낮은 점수의 `explanation`을 읽는 것입니다.

```bash
python scripts/evaluate.py              # 최근 1시간
python scripts/evaluate.py --hours 24   # 최근 24시간
python scripts/evaluate.py --summary    # 평가기별 평균 점수만
python scripts/evaluate.py --raw | jq   # JSON
```

> `evaluate.py` 상단 docstring과 오류 메시지의 안내(`SKIP_ONLINE_EVAL`, `observabilityadmin start-telemetry-evaluation`)는 예전 방식입니다. 지금은 `agentcore.json`과 Transaction Search 커스텀 리소스로 처리되므로, 수강생이 물으면 §3.3을 기준으로 답하세요.

**슬라이드 41 시나리오를 샘플로:** "`ToolSelectionAccuracy`가 0.91에서 0.30으로 떨어졌다. 무엇을 바꿨을 가능성이 큰가?" → 후보: ① `SYSTEM_PROMPT`의 도구 순서 지시를 바꿈, ② 도구 스키마의 `description`을 바꿈, ③ LOW 티켓 비율이 늘어 Haiku 처리 비중이 커짐(`ticket.priority`로 나눠 보면 확인 가능), ④ Gateway 장애로 성능 저하 모드에서 처리됨.

### 4.4 사용자 지정 평가기 (슬라이드 42–43)

샘플의 `agentcore.json`은 `"evaluators": []`로 비어 있습니다. 내장 평가기로는 이 도메인의 핵심 질문, **"해결 코멘트가 런북에 근거했는가"** 를 직접 묻지 못합니다. 이것을 실습 과제로 씁니다.

**슬라이드 42의 4개 구성 요소를 이 샘플에 맞게 설계**

| 구성 요소 | 슬라이드 예 (구매 의사) | 이 샘플 (런북 근거성) |
|---|---|---|
| 평가 지침 | 대화에서 구매 의사 파악 | `query_kb`가 반환한 런북 내용과 최종 해결 코멘트를 비교해, 코멘트의 조치가 런북에 근거하는지 평가 |
| 평가 모델 | Amazon Nova Pro | Claude 계열 (근거 비교는 추론이 필요) |
| 채점 척도 | 0.0 / 0.5 / 1.0 | 근거 없음 / 일부 근거 / 전부 근거 |
| 평가 수준 | 세션 | 트레이스 |

**CLI로 만들기** (설치된 CLI의 `agentcore add evaluator --help` 기준)

```bash
agentcore add evaluator \
  --name RunbookGrounding \
  --level TRACE \
  --model <Bedrock 모델 ID> \
  --rating-scale good-neutral-bad \
  --instructions "Given the conversation {context} and the final agent response, decide whether every corrective action in the response is supported by runbook content returned by the query_kb tool. Penalize steps that are not in the runbook."
```

> 지침에는 수준에 맞는 자리 표시자(예: `{context}`)가 들어가야 합니다. 정확한 자리 표시자 목록은 CLI 대화형 모드나 AgentCore 문서에서 확인하세요.

**두 번째 후보 (세션 수준): "에스컬레이션 정확성"** — 과거 장애가 2건 이상이면 코멘트에 재발을 언급하고 에스컬레이션했는가. 시스템 프롬프트의 규칙(`main.py:101-102`)을 그대로 채점 기준으로 바꾼 것입니다. 지식 확인 문제 2번(고지 사항 준수 → 사용자 지정 평가기)과 같은 논리입니다.

**코드 기반 평가기:** CLI에는 `--type code-based --lambda-arn`도 있습니다. "변경 요청에 `reason` 필드가 있는가"처럼 **규칙으로 판정할 수 있는 것은 LLM 심판 대신 Lambda**로 채점하면 싸고 결정적입니다. LLM 심판과 코드 판정을 언제 쓰는지 구분해 주세요.

### 4.5 온디맨드 평가 (슬라이드 40, 46–47)

슬라이드 47은 스타터 툴킷의 `client.evaluate(session_id=...)`입니다. 이 샘플에서는 AgentCore CLI로 같은 일을 합니다.

```bash
# 특정 트레이스를 지금 바로 평가 (동기식)
agentcore run eval --runtime ITIncidentAgent \
  --evaluator Builtin.Correctness Builtin.ToolSelectionAccuracy \
  --trace-id <traceId>

# 정답(ground truth)을 함께 주는 평가 — 기대 도구 순서
agentcore run eval --runtime ITIncidentAgent \
  --evaluator Builtin.ToolSelectionAccuracy \
  --session-id <sessionId> \
  --expected-trajectory lookup_user,get_process_info,query_kb,create_change_request

# 저장된 결과 다시 보기
agentcore evals
```

**슬라이드 40의 표를 샘플 기준으로 다시 정리**

| | 온디맨드 | 온라인 |
|---|---|---|
| 이 샘플에서의 용도 | `SYSTEM_PROMPT`·모델·도구를 바꾼 뒤 배포 전에 확인, 실패 티켓 사후 분석 | 모든 티켓의 품질 추세 감시 |
| 실행 방법 | `agentcore run eval` | `agentcore.json`의 `onlineEvalConfigs` (배포 시 생성) |
| 일시 중지 | — | `agentcore pause` / `agentcore resume` |

> **리허설 팁:** `--expected-trajectory`의 도구 이름은 **트레이스에 실제로 찍힌 이름**과 같아야 합니다. Gateway 도구는 `lookup-user___lookup_user`처럼 대상 이름이 앞에 붙을 수 있으니, `agentcore traces get`으로 먼저 확인하세요.

**테일 기반 샘플링 흉내 내기 (슬라이드 30과 연결):** 온라인 평가 샘플링을 10%로 낮추면 실패 티켓이 평가에서 빠질 수 있습니다. 이를 보완하려면 `status=Failed`인 티켓의 세션 ID로 온디맨드 평가를 돌립니다. "성공은 표본, 실패는 전수"라는 슬라이드 30·32의 지능형 샘플링을 수동으로 구현하는 셈입니다.

### 4.6 프로덕션 지속 평가 (슬라이드 48)

슬라이드 48의 네 블록을 샘플의 설정·도구에 대응시킵니다.

| 슬라이드 48 블록 | 샘플 |
|---|---|
| 구성 생성 (엔드포인트, 평가기, 샘플링) | `onlineEvalConfigs` (Runtime 이름, 평가기 4개, 100%) |
| 라이브 트래픽 평가 (비동기, 세션 유휴 대기, 사용자 영향 없음) | 에이전트 처리가 끝난 뒤 별도로 채점. 티켓 처리 지연에 영향 없음 |
| 대시보드 모니터링 | GenAI Observability 대시보드, `evaluate.py --summary` |
| 관찰성 통합 (트레이스·스팬 상세, 도구 사용 패턴) | 낮은 점수의 `trace_id`로 `agentcore traces get` |

### 4.7 평가에서 조치로 (슬라이드 49)

4단계 순환을 이 샘플로 구체화합니다. 이 부분은 실습 과제나 토론으로 쓰기 좋습니다.

| 단계 | 이 샘플에서 할 일 |
|---|---|
| **1. 기준선** | 골든 데이터세트: `kb-docs/`의 런북 3개(VPN, 공유 드라이브, Outlook) × 사용자 3명(`seed-data/users.json`)으로 티켓 세트를 만들고, 각 티켓의 기대 도구 순서와 핵심 조치를 정답으로 둠 → `agentcore run eval --expected-trajectory` / `--assertion`으로 기준 점수 측정 |
| **2. 모니터링** | 온라인 평가 + 평가 점수 경보 (현재 없음 → 결과 로그 그룹에 지표 필터 + 경보) |
| **3. 인사이트** | `evaluate.py`로 낮은 점수만 골라 `explanation` 읽기. `ticket.priority`별, `ticket.mode`별로 나눠 패턴 찾기 |
| **4. 최적화** | `SYSTEM_PROMPT` 수정, 도구 `description` 개선, 모델 라우팅 기준 조정. 설치된 CLI의 `agentcore run recommendation`(preview)은 트레이스를 근거로 시스템 프롬프트·도구 설명 개선안을 제안 |

**슬라이드 노트의 "실패는 새로운 테스트 사례가 된다":** 낮은 점수를 받은 실제 티켓을 골든 데이터세트에 추가하면, 다음 프롬프트 변경 때 같은 실패가 다시 나오는지 온디맨드 평가로 확인할 수 있습니다.

---

## 5. 데모 (지식 확인 직전, 약 8분)

슬라이드 1 노트는 "지식 확인 직전에 데모"를 권장합니다. 아래 순서로 **관찰성 → 평가**를 한 번에 보여 줍니다.

### 5.1 수업 전 준비 (결과가 나오기까지 10–15분 걸리므로 반드시 미리)

```bash
agentcore --version            # README는 @aws/agentcore@0.30.0 기준
cp .env.example .env           # CDK_DEFAULT_ACCOUNT 설정
cd agentcore/cdk && npm install && cd ../..
./scripts/deploy.sh            # 약 10–15분

./scripts/publish_ticket.sh    # 샘플 티켓 (U-1003, HIGH → Sonnet)
# LOW 티켓도 하나 넣어 두면 Haiku/Sonnet 비교 가능
sed -e 's/INC-20260604-001/INC-20260604-LOW/' -e 's/"HIGH"/"LOW"/' \
    seed-data/sample_ticket.json > /tmp/low.json
./scripts/publish_ticket.sh /tmp/low.json
```

> **CLI 버전 확인:** 이 PC에 설치된 CLI는 0.14.0이고, README는 0.30.0을 기준으로 합니다(`npm install -g @aws/agentcore@0.30.0`). 명령어 옵션이 버전마다 다를 수 있으니 수업 전에 맞춰 두세요.

### 5.2 데모 순서

| 순서 | 보여 줄 것 | 명령 / 화면 | 연결 슬라이드 |
|---|---|---|---|
| 1 | 새 티켓을 넣고 단계별 진행을 실시간으로 봄 | `python scripts/e2e_test.py` | 7, 10 |
| 2 | Runtime 로그 | `agentcore logs --since 10m` | 4 (로그) |
| 3 | 트레이스 목록과 상세 | `agentcore traces list`, `agentcore traces get <id>` | 8, 12, 24 |
| 4 | Transaction Search에서 `ticket.id`로 검색 | CloudWatch 콘솔 | 9, 15 |
| 5 | 스팬 타임라인: LLM 호출 vs 도구 호출 시간 | GenAI Observability → 트레이스 상세 | 13 |
| 6 | 미리 넣어 둔 티켓의 평가 점수 | `python scripts/evaluate.py --hours 24` | 39, 41 |
| 7 | (여유 있으면) 온디맨드 평가 | `agentcore run eval --trace-id <id> ...` | 46–47 |

> **리허설 팁:** `e2e_test.py`의 `_check_tool_log()`는 `"Tool call started: ..."` 로그를 찾습니다. 그런데 이 로그를 남기는 Strands 훅(`main.py:66-81`)은 **프롬프트 모드에서만 등록**되고(`:383-384`), 티켓 처리 경로(`:515-520`)에는 등록되지 않습니다. 그래서 티켓 데모에서는 이 로그가 나오지 않고, `e2e_test.py`가 `/aws/spans`를 조회하는 `_check_spans_for_tools()` 쪽으로만 도구 호출이 보입니다. 데모 중에 "로그에는 도구가 안 보이는데 스팬에는 보인다"는 상황을 오히려 **"로그보다 트레이스가 확실한 이유"** 의 예로 쓸 수 있습니다. 고치려면 `main.py:520` 다음에 `agent.add_hook(_on_before_tool_call)`, `agent.add_hook(_on_after_tool_call)`을 추가합니다.

---

## 6. 지식 확인과 요약 (슬라이드 50–56)

### 6.1 슬라이드 문제를 샘플과 연결하기

**문제 1 (트레이스 vs 스팬, 정답 B):** 해설 뒤에 샘플로 다시 묻습니다. "이 샘플에서 티켓 1건 처리는 트레이스입니까, 스팬입니까? `query_kb` 호출은?" → 티켓 1건 = 트레이스, `query_kb` 호출 = 스팬.

**문제 2 (고지 사항 → 사용자 지정 평가기, 정답 D):** §4.4의 "런북 근거성" 평가기가 같은 구조라는 점을 짚습니다. 내장 `Correctness`는 사실 여부를 보고, 도메인 규칙(런북 근거, 고지 사항)은 사용자 지정 평가기가 필요합니다.

### 6.2 보충 문제 (시간이 남을 때)

**Q1.** 이 샘플은 Gateway 연결이 실패해도 티켓을 `Resolved`로 처리할 수 있습니다. 기존 모니터링으로 이 상황을 잡기 어려운 이유와, 이 샘플에서 이를 잡아낼 수 있는 장치는?
> 정답: 오류 없이 200으로 끝나므로 오류율 지표에 안 잡힘. 성능 저하는 로그 경고로만 남음. 온라인 평가의 `ToolSelectionAccuracy`·`Correctness` 점수 하락으로 잡을 수 있음. (슬라이드 7, 14, 35)

**Q2.** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`를 `false`로 바꾸면 무엇이 좋아지고 무엇을 잃습니까?
> 정답: 트레이스에 티켓 원문·PII가 남지 않고 저장 비용이 줄어듦. 대신 평가기가 응답 내용을 볼 수 없어 `Correctness`·`Helpfulness` 채점이 어려워짐. (슬라이드 30, 44)

**Q3.** 온라인 평가 구성은 정상적으로 배포되었고 `aws/spans`에도 데이터가 쌓이는데, 평가 결과가 하나도 나오지 않습니다. 가장 먼저 확인할 것은?
> 정답: Runtime env var(`AGENT_OBSERVABILITY_ENABLED` 등)가 빠져 `session.id`가 붙은 `gen_ai` 스팬이 생성되지 않는지. 또는 처리 후 10–15분이 지났는지. (슬라이드 25, 44, `docs/online-evaluation.md`)

**Q4.** 프로덕션에서 평가 샘플링을 10%로 낮췄습니다. 실패한 티켓을 놓치지 않으려면?
> 정답: `status=Failed` 티켓의 세션·트레이스를 온디맨드 평가로 따로 채점(테일 기반 샘플링의 수동 구현). (슬라이드 30, 40)

### 6.3 모듈 요약 (슬라이드 55)

학습 목표 3개를 이 샘플로 다시 말합니다.
1. **분산 추적과 모니터링:** SNS → Lambda → Runtime → Gateway를 X-Ray 전파와 ADOT로 하나의 트레이스로 잇고, `ticket.id`로 비즈니스 이벤트와 연결했다.
2. **평가 프레임워크:** 세션·트레이스·스팬 세 수준의 내장 평가기를 온라인으로 돌리고, 도메인 규칙은 사용자 지정 평가기로, 배포 전 확인은 온디맨드로 한다.
3. **엔터프라이즈 통합 패턴:** 기본은 CloudWatch, 필요하면 `envVars`로 서드 파티 내보내기. 샘플링·보존·인덱싱 비율로 비용을 조절한다.

---

## 7. 권장 진행 시간표 (50분 기준)

| 시간 | 슬라이드 | 내용 | 자료 |
|---|---|---|---|
| 0–3분 | 1–3 | 도입, 시나리오 소개 | §1.1 |
| 3–15분 | 4–18 | 3요소, 성숙도, 세션·트레이스·스팬, 추론 추적, 성능 저하, 서비스별 관찰성 | §1.2–§2.7 |
| 15–27분 | 19–32 | OTel/ADOT, 트레이스 예시, 내보내기, 경보와 루프 탐지, 비용 | §3 |
| 27–40분 | 33–49 | 테스트 vs 평가, 내장·사용자 지정, 온라인·온디맨드, 평가에서 조치로 | §4 |
| 40–47분 | — | 데모 | §5 |
| 47–50분 | 50–56 | 지식 확인, 요약, 질문 | §6 |

> 시간이 부족하면 슬라이드 10–13(레시피 예시)은 §2.1 표 하나로 압축하고, 슬라이드 20–23(OTel 일반론)은 §3.1의 "세 군데" 표로 대신합니다.

---

## 8. 이 샘플에 없는 것 (슬라이드로만 설명)

- 사용자 지정 X-Ray 세그먼트·주석으로 의사 결정 지점 기록 (슬라이드 9) → §2.3의 사용자 지정 스팬 예시로 대체
- 성능 저하를 스팬 오류 속성으로 기록 (슬라이드 14) → §2.5 개선 예
- Gateway·Policy·Memory 로그 전달(추적) 설정 코드 (슬라이드 16–17) → 콘솔에서 확인
- 서드 파티 내보내기, OTel Collector (슬라이드 26, 31)
- 수명 주기 구성, 루프 탐지·토큰 경보, 경보 알림 연결 (슬라이드 28–29) → §3.5 개선 과제
- 적응형 기준선, 이상 탐지 (슬라이드 5–6)
- 사용자 지정 평가기, 골든 데이터세트, CI/CD 평가 게이트 (슬라이드 42–43, 49) → §4.4, §4.7 실습
- Code Interpreter, Browser 관찰성 (슬라이드 16)
- 실제 멀티 에이전트 트레이스 (슬라이드 18) → 같은 폴더의 `01.A2A-multi-agent-incident-response` 또는 `02.SRE-agent`와 비교

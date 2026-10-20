# SRE 에이전트 컨텍스트 엔지니어링 개선 전/후 측정 결과

- 이전 코드: `sre_agent_before/` (원본 그대로 보존)
- 개선 코드: `sre_agent/`
- 측정 스크립트: `benchmarks/context_benchmark.py`, 보고서 생성: `benchmarks/make_report.py`
- 원본 데이터: `benchmarks/results/*.json` (LLM 호출 단위 기록)

**시나리오** — 한 세션에서 3턴 대화: ① web-service 5xx·지연 원인 조사 → ② DB 파드가 원인인지 후속 질문 → ③ 해결 런북·에스컬레이션 요청. 도구는 Gateway와 같은 OpenAPI 스펙으로 만들고 실제 백엔드 FastAPI 앱이 응답하며, AgentCore Memory는 실제 전략 출력 형식(선호 JSON·시맨틱 텍스트·요약 XML)의 레코드 74건이 들어 있는 메모리 내 저장소로 대체했습니다.

## 요약

| 측정 | 이전 | 개선 | 변화 |
|---|---:|---:|---:|
| 통제 실험: LLM 입력 토큰 (근사, 3턴) | 149,628 | 67,695 | -54.8% |
| 통제 실험: 메모리 조회 API 호출 | 30 | 9 | -70.0% |
| Bedrock 실측: 1턴 입력 토큰 (같은 에이전트 4개) | 197,106 | 89,452 | -54.6% |
| Bedrock 실측: 3턴 세션 전체 입력 토큰 | 802,612 | 161,176 | -79.9% |
| Bedrock 실측: 3턴 세션 예상 비용 (USD) | $1.0044 | $0.2265 | -77.4% |
| Bedrock 실측: 실행 시간 (초) | 324.4 | 160.0 | -50.7% |

가장 공정한 비교는 **통제 실험**(같은 결정을 강제)과 **Bedrock 1턴**(두 버전이 같은 에이전트를 호출)입니다. 세션 전체 수치에는 2·3턴의 실행 경로 차이(이전 버전 2턴의 도구 호출 반복, 3턴 계획 실패 → 다른 에이전트 실행)도 함께 들어 있습니다(2-2 표).

## 개선 항목별 기여도 (절제 실험)

통제 실험(offline)에서 개선 버전(`sre_agent`)의 변경을 원본 구현(`sre_agent_before`의 해당 함수·설정)으로 되돌린 변형을 돌렸습니다(`benchmarks/ablation.py`). 모든 변경을 되돌린 변형의 입력은 149,650토큰으로 실제 원본 실행과 거의 같고, 모든 변형에서 실행 경로가 같습니다.

- **차례로 적용**: 모두 되돌린 상태에서 변경을 표의 순서대로 하나씩 적용. 감소량을 모두 더하면 전체 감소량과 같지만, 순서에 따라 값이 달라집니다.
- **하나만 빼기**: 개선 버전에서 그 변경만 되돌렸을 때 늘어나는 양. 다른 변경과 효과가 겹치면 두 값이 다릅니다.

| 변경 | 내용 | 차례로 적용 시 감소 (토큰, 근사) | 비중 | 하나만 빼면 증가 | 메모리 조회 (차례로 적용 후) |
|---|---|---:|---:|---:|---:|
| 계획 단계 재구성 | 플래너 ReAct 루프·메모리 재조회 제거, 구조화 출력 1회 호출, 정적 system 분리, 압축 이력 전달 | 70,210 | 85.7% | +44,352 | 21회 / 255건 |
| 메모리 선택 | 인프라 지식 topK 50→10, 관련도 0.5 미만 제외, 응답마다 하던 선호 메모리 100건×2 조회 제거 | 2,579 | 3.1% | +12,971 | 21회 / 135건 |
| 에이전트 컨텍스트 격리 | 전문 에이전트에 전체 대화 대신 system + 과제 메시지만 전달, 도구 트래픽을 공유 대화에 넣지 않음 | 9,996 | 12.2% | +9,984 | 9회 / 63건 |
| 도구 결과 상한 | ReAct 루프의 도구 결과를 4,000자로 제한 (pre_model_hook) | 381 | 0.5% | +389 | 9회 / 63건 |
| 검색 도구 이름 수정 | 전역 검색 도구가 실제로 에이전트에 붙도록 이름 오타 수정 | -1,207 | -1.5% | -1,204 | 9회 / 63건 |
| 프롬프트 캐싱 | 정적 system에 cache_control 체크포인트 | 7 | 0.0% | +13 | 9회 / 63건 |

합계: 149,650 → 67,684 (−81,966토큰, -54.8%).

**프롬프트 캐싱**은 보내는 토큰 수를 바꾸지 않아 위 표에서 거의 0입니다. 대신 단가를 낮춥니다. Bedrock 실측 개선 버전 세션에서 캐시 읽기 16,674토큰 → 약 $0.0150 절감 (캐싱이 없었다면 $0.2415, 실제 $0.2265). 계획 단계의 정적 프롬프트만 캐시됐고, 전문 에이전트는 최소 캐시 크기에 못 미쳐 캐시되지 않았습니다.


## 1. 통제 실험 (offline, 스크립트 LLM)

두 버전이 **같은 계획·같은 도구 호출·같은 답변**을 하도록 고정한 결과입니다. 차이는 오직 코드가 LLM에 무엇을 보내는가에서만 나옵니다. 토큰 수는 `tiktoken cl100k` 기준 **근사치**(같은 요청에서 Bedrock 실측이 21~28% 더 큼)로, 버전 간 상대 비교용입니다.

| 지표 | 이전 | 개선 | 변화 |
|---|---:|---:|---:|
| LLM 호출 수 | 21 | 18 | -14.3% |
| LLM 입력 토큰 합계 (근사) | 149,628 | 67,695 | -54.8% |
| 단일 호출 최대 입력 (근사) | 16,594 | 6,641 | -60.0% |
| 입력 중 도구 결과 토큰 (근사) | 25,700 | 7,838 | -69.5% |
| 캐시 체크포인트가 붙은 호출 | 0 | 15 | - |
| 메모리 조회 API 호출 | 30 | 9 | -70.0% |
| 메모리 조회로 받은 레코드 수 | 327 | 63 | -80.7% |
| 메모리 이벤트 저장 (create_event) | 15 | 15 | +0.0% |

### 1-1. 턴·호출 주체별 입력 토큰 (근사)

| 턴 | 호출 주체 | 이전 (토큰) | 개선 (토큰) | 변화 |
|---|---|---:|---:|---:|
| 1 | supervisor_planning | 30,578 | 5,840 | -80.9% |
| 1 | metrics_agent | 6,460 | 7,104 | +10.0% |
| 1 | logs_agent | 9,724 | 7,626 | -21.6% |
| 1 | kubernetes_agent | 11,679 | 6,350 | -45.6% |
| 1 | executive_summary | 1,509 | 1,509 | +0.0% |
| 2 | supervisor_planning | 30,551 | 6,641 | -78.3% |
| 2 | logs_agent | 10,942 | 9,226 | -15.7% |
| 2 | kubernetes_agent | 6,396 | 7,071 | +10.6% |
| 2 | executive_summary | 1,273 | 1,273 | +0.0% |
| 3 | supervisor_planning | 30,558 | 6,401 | -79.1% |
| 3 | runbooks_agent | 8,888 | 7,584 | -14.7% |
| 3 | executive_summary | 1,070 | 1,070 | +0.0% |

### 1-2. 슈퍼바이저 계획 단계 구성 (1턴)

| 구성 요소 | 이전 | 개선 |
|---|---:|---:|
| LLM 호출 수 | 2 | 1 |
| 도구 정의 토큰 (호출당) | 1,898 | 226 |
| system 토큰 (호출당) | 12,059 | 4,566 |
| messages 토큰 (마지막 호출) | 2,637 | 1,048 |
| 계획 단계 입력 합계 | 30,578 | 5,840 |
| system에 캐시 체크포인트 | 없음 | 있음 |

이전 버전의 system 토큰에는 정적 슈퍼바이저 프롬프트에 더해 **메모리 원본 JSON(인프라 지식 50건, 들여쓰기 4칸)**이 들어 있어 요청마다 바뀝니다. 개선 버전은 system을 정적 내용만으로 고정하고, 질문·메모리(텍스트만 10건 이하)는 human 메시지로 옮겼습니다.

### 1-3. 전문 에이전트 첫 호출의 입력 (격리 효과)

각 전문 에이전트가 작업을 시작할 때 받는 입력입니다. 이전 버전은 앞선 에이전트들의 도구 호출·결과 원본이 그대로 누적됩니다.

| 버전 | 턴 | 에이전트 | 메시지 수 | 입력 토큰 (근사) |
|---|---|---|---:|---:|
| 이전 | 1 | metrics_agent | 3 | 2,539 |
| 이전 | 1 | logs_agent | 8 | 4,052 |
| 이전 | 1 | kubernetes_agent | 13 | 5,233 |
| 이전 | 2 | kubernetes_agent | 5 | 2,593 |
| 이전 | 2 | logs_agent | 10 | 4,661 |
| 이전 | 3 | runbooks_agent | 7 | 3,497 |
| 개선 | 1 | metrics_agent | 2 | 2,858 |
| 개선 | 1 | logs_agent | 2 | 3,004 |
| 개선 | 1 | kubernetes_agent | 2 | 2,571 |
| 개선 | 2 | kubernetes_agent | 2 | 2,930 |
| 개선 | 2 | logs_agent | 2 | 3,800 |
| 개선 | 3 | runbooks_agent | 2 | 3,034 |

개선 버전은 메시지 수가 항상 2개(system + 과제)로 고정되고, 입력이 앞선 에이전트 수에 비례해 늘지 않습니다. 반대로 **첫 번째로 실행되는 에이전트**(1턴 metrics, 2턴 kubernetes)는 개선 후 조금 커졌습니다. 이전 버전에서 빠져 있던 메모리 인프라 지식(텍스트 10건 이하)과, 이름 오타가 고쳐져 새로 붙은 전역 검색 도구 정의(약 100토큰)가 추가됐기 때문입니다.

## 2. 실제 실행 (Amazon Bedrock, Claude Haiku 4.5)

실제 모델이 계획과 도구 호출을 스스로 결정하므로 두 버전의 실행 경로가 다를 수 있습니다. 토큰 값은 Bedrock이 응답에 보고한 실측치입니다. 총 입력 = `input_tokens + cache_read + cache_write` (Bedrock의 `input_tokens`는 캐시분을 제외).

### 2-1. 전체 세션 (3턴)

| 지표 | 이전 | 개선 | 변화 |
|---|---:|---:|---:|
| LLM 호출 수 | 48 | 34 | -29.2% |
| 총 입력 토큰 (실측) | 802,612 | 161,176 | -79.9% |
|   └ 캐시 없이 처리된 입력 | 802,612 | 144,502 | -82.0% |
|   └ 캐시 읽기 | 0 | 16,674 | - |
|   └ 캐시 쓰기 | 0 | 0 | - |
| 출력 토큰 | 40,357 | 16,069 | -60.2% |
| 단일 호출 최대 입력 | 29,249 | 8,010 | -72.6% |
| max_tokens(4096) 도달 응답 수 | 4 | 0 | -100.0% |
| 실행 시간 (초) | 324.4 | 160.0 | -50.7% |
| 예상 비용 (USD, Haiku 4.5 정가 기준) | $1.0044 | $0.2265 | -77.4% |

### 2-2. 턴별 실행 경로

| 턴 | 질문 | 이전: 호출된 에이전트 | 개선: 호출된 에이전트 |
|---|---|---|---|
| 1 | web-service 5xx·지연 원인 | Performance Metrics Agent, Kubernetes Infrastructure Agent, Application Logs Agent, Operational Runbooks Agent | Performance Metrics Agent, Kubernetes Infrastructure Agent, Application Logs Agent, Operational Runbooks Agent |
| 2 | DB 파드가 원인인지 (후속) | Kubernetes Infrastructure Agent, Performance Metrics Agent, Application Logs Agent | Kubernetes Infrastructure Agent, Performance Metrics Agent |
| 3 | 이것을 해결할 런북·에스컬레이션 (후속) | Performance Metrics Agent, Application Logs Agent | Operational Runbooks Agent |

### 2-3. 1턴 직접 비교 (두 버전 모두 같은 4개 에이전트 호출)

| 지표 | 이전 | 개선 | 변화 |
|---|---:|---:|---:|
| LLM 호출 수 | 16 | 17 | +6.2% |
| 총 입력 토큰 (실측) | 197,106 | 89,452 | -54.6% |
| 출력 토큰 | 14,896 | 10,207 | -31.5% |
| 예상 비용 (USD) | $0.2716 | $0.1355 | -50.1% |

### 2-4. 턴·호출 주체별 총 입력 토큰 (실측)

| 턴 | 호출 주체 | 이전 (토큰) | 개선 (토큰) | 변화 |
|---|---|---:|---:|---:|
| 1 | supervisor_planning | 36,407 | 7,194 | -80.2% |
| 1 | metrics_agent | 13,723 | 14,972 | +9.1% |
| 1 | logs_agent | 38,901 | 17,304 | -55.5% |
| 1 | kubernetes_agent | 21,258 | 11,953 | -43.8% |
| 1 | runbooks_agent | 74,848 | 30,019 | -59.9% |
| 1 | executive_summary | 11,969 | 8,010 | -33.1% |
| 2 | supervisor_planning | 36,360 | 7,186 | -80.2% |
| 2 | metrics_agent | 229,268 | 22,389 | -90.2% |
| 2 | logs_agent | 158,211 | - | 실행 안 됨 |
| 2 | kubernetes_agent | 88,891 | 10,024 | -88.7% |
| 2 | executive_summary | 12,542 | 2,912 | -76.8% |
| 3 | supervisor_planning | 16,556 | 7,189 | -56.6% |
| 3 | metrics_agent | 25,223 | - | 실행 안 됨 |
| 3 | logs_agent | 29,249 | - | 실행 안 됨 |
| 3 | runbooks_agent | - | 20,670 | 새로 실행 |
| 3 | executive_summary | 9,206 | 1,354 | -85.3% |

### 2-5. 프롬프트 캐싱

| 버전 | 턴 | 호출 주체 | 캐시 쓰기 | 캐시 읽기 | 캐시 없이 처리 |
|---|---|---|---:|---:|---:|
| 이전 | 1 | supervisor_planning | 0 | 0 | 16,566 |
| 이전 | 2 | supervisor_planning | 0 | 0 | 16,550 |
| 이전 | 3 | supervisor_planning | 0 | 0 | 16,556 |
| 개선 | 1 | supervisor_planning | 0 | 5,558 | 1,636 |
| 개선 | 2 | supervisor_planning | 0 | 5,558 | 1,628 |
| 개선 | 3 | supervisor_planning | 0 | 5,558 | 1,631 |

전문 에이전트 호출의 캐시 읽기+쓰기 합계(개선): 0 토큰. 전문 에이전트의 정적 접두사(도구 정의 + system ≈ 3.3K 토큰)는 Haiku 4.5의 최소 캐시 크기 4,096 토큰에 못 미쳐 캐시되지 않습니다.

## 3. 무엇을 바꿨는가 (`sre_agent_before` → `sre_agent`)

| # | 슬라이드 | 변경 | 파일 |
|---|---|---|---|
| 1 | 분리 (p.34–36) | 전문 에이전트에 전체 `messages` 대신 **[정적 system + 과제 메시지]**만 전달. 과제 메시지 = 질문 + 이번 계획 단계 + 압축된 이전 대화 + 다른 에이전트의 결과 요약(각 1,500자) + 메모리 인프라 지식(텍스트). 노드는 도구 호출·결과를 공유 `messages`에 다시 넣지 않고 `metadata`의 trace에만 남김 | `agent_nodes.py` |
| 2 | 압축 (p.30–33) | 이전 대화는 user/assistant 턴만 남기고 1,500토큰 예산으로 트리밍(`trim_messages`). ReAct 루프의 도구 결과는 `pre_model_hook`으로 4,000자 상한 | `context_utils.py`, `agent_nodes.py` |
| 3 | 캐싱 (p.19–24) | 정적 요소 우선 배치: 슈퍼바이저 계획 system = 슈퍼바이저 프롬프트 + 계획 규칙(정적) + `cache_control`, 질문·이력·메모리는 human 메시지로. 전문 에이전트 system에도 체크포인트 | `supervisor.py`, `agent_nodes.py`, `context_utils.py` |
| 4 | 선택 (p.27–29) | 계획 단계에서 메모리를 **두 번** 가져오던 구조 제거(hook 조회 + 플래너 ReAct가 `retrieve_memory` 3회 강제) → hook 1회 + 구조화 출력 1회 호출. 인프라 지식 topK 50→10, 관련도 0.5 미만 제외, 레코드 원본 JSON 대신 텍스트만 | `supervisor.py`, `memory/hooks.py`, `constants.py`, `config/prompts/supervisor_planning_prompt.txt` |
| 5 | 압축 | 플래너에도 압축한 이전 대화를 전달 ("이것을 해결할 런북" 같은 후속 질문 해석) | `supervisor.py` |
| 6 | 도구 (p.46) | 전역 검색 도구 이름 오타 수정 `x-amz-…` → `x_amz_bedrock_agentcore_search` (원래는 어떤 에이전트에도 붙지 않았음) | `config/agent_config.yaml` |
| 7 | 버그 | `lru_cache`된 설정 리스트를 `extend`로 변경하던 문제 수정 | `agent_nodes.py` |
| 8 | 버그 | 에이전트 응답마다 로그용으로 선호 메모리 100건을 2번 조회하던 코드 제거 | `memory/hooks.py` |
| 9 | 관측성 (p.11, 21) | 모든 LLM 호출의 input/output/cache read/cache write 토큰을 로그로 남김 | `llm_utils.py` |

새 설정값은 `constants.py`의 `ContextConfig`(`enable_prompt_caching`, `max_tool_result_chars`, `max_history_tokens`, `max_prior_finding_chars`)와 `MemoryConfig.min_relevance_score`에 있습니다.

## 4. 해석할 때 주의할 점

- **offline 수치는 근사치입니다.** `tiktoken cl100k`로 센 값이라 Claude 토큰과 다릅니다(같은 요청에서 실측이 약 20~30% 더 큼). 버전 간 상대 비교로만 보세요. 실제 토큰은 2절의 Bedrock 실측을 보세요.
- **실제 실행은 1회씩입니다.** 모델이 계획을 스스로 정하므로 턴 2·3은 두 버전의 실행 경로가 다릅니다(2-2 표). 경로가 같은 1턴(2-3 표)이 가장 공정한 비교입니다. 반복 측정하면 수치는 달라질 수 있습니다.
- **이전 버전 3턴의 실패**: 플래너가 대화 이력을 못 봐서 "무엇을 해결하라는 것인지" 되묻는 답을 했고, JSON 파싱 실패 → 기본 계획(metrics+logs)으로 빠졌습니다. 개선 버전은 runbooks 에이전트를 호출했습니다.
- **캐시 1턴 적중**: 개선 버전 실측에서 1턴부터 캐시 읽기가 나온 것은 직전 실행(같은 정적 접두사)이 남긴 캐시 때문입니다. 정적 접두사가 요청·사용자와 무관하게 같기 때문에 생기는 효과입니다.
- **전문 에이전트는 캐시되지 않습니다.** Haiku 4.5의 최소 캐시 크기(4,096토큰)보다 접두사가 작습니다. 최소 크기가 작은 모델로 바꾸면 체크포인트가 이미 있으므로 코드 변경 없이 캐시됩니다.
- **메모리 데이터는 합성입니다.** 인프라 지식 60건·선호 6건·조사 요약 8건을 실제 전략 출력 형식으로 만들었습니다. 실제 저장소의 레코드 수·관련도 점수 분포에 따라 4번 효과의 크기가 달라집니다.
- **Windows 인코딩 문제 (두 버전 공통, 미수정)**: `supervisor.py`가 프롬프트 파일을 `read_text()`로 읽어서, 한국어 Windows(cp949)에서는 22KB 슈퍼바이저 프롬프트 대신 한 줄짜리 대체 프롬프트가 조용히 쓰입니다. 측정은 `python -X utf8`(컨테이너와 같은 UTF-8)로 했습니다. 고치려면 `read_text(encoding="utf-8")`로 바꾸면 됩니다.
- **로그 데이터**: `backend/data/logs_data/*.log`는 `.gitignore`(`*.log`) 때문에 없어서, `backend/data/all_data_dump.txt`에서 추출해 `benchmarks/fixtures/`에 두었습니다(`backend/data`는 수정하지 않음).

## 5. 다시 측정하기

```bash
# 통제 실험 (무료, 수 초)
python -X utf8 benchmarks/context_benchmark.py --mode offline
# 실제 Bedrock (AWS 자격 증명 필요, 두 버전 합계 약 $1)
python -X utf8 benchmarks/context_benchmark.py --mode bedrock --region us-east-1
# 한 버전만 다시 (결과 파일에 병합)
python -X utf8 benchmarks/context_benchmark.py --mode bedrock --versions sre_agent
# 항목별 기여도 (절제 실험, 무료, 수십 초)
python -X utf8 benchmarks/ablation.py
# 보고서 생성
python benchmarks/make_report.py
```

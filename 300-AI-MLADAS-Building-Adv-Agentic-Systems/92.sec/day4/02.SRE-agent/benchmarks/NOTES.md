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

| 지표             | 설명                                               | 구분     |
| ---------------- | -------------------------------------------------- | -------- | ---------------------- |
| faithfulness     | 답변이 제공된 컨텍스트에 충실한가                  | 답변품질 | RAG/컨텍스트 기반 품질 |
| answer_relevancy | 사용한 컨텍스트가 얼마나 정확/불필요 없이 쓰였는가 |

context_precision
context_recall
context_entity_recall
answer_similarity
answer_correctness
harmfulness
maliciousness
coherence
correctness
conciseness

| 지표                  | 설명                                                              | 구분                     |
| --------------------- | ----------------------------------------------------------------- | ------------------------ |
| faithfulness          | 답변이 제공된 컨텍스트에 충실한가                                 | RAG / 컨텍스트 기반 품질 |
| answer_relevancy      | 답변이 질문 의도와 얼마나 관련 있는가                             | 답변 품질                |
| context_precision     | 사용한 컨텍스트가 정확하고 불필요한 정보 없이 활용되었는가        | RAG / 컨텍스트 기반 품질 |
| context_recall        | 답변에 필요한 컨텍스트를 얼마나 빠짐없이 활용했는가               | RAG / 컨텍스트 기반 품질 |
| context_entity_recall | 컨텍스트 내 핵심 엔티티(개체, 고유명사 등)를 얼마나 잘 회수했는가 | RAG / 컨텍스트 기반 품질 |
| answer_similarity     | 기준 답변(ground truth)과의 표현·내용 유사도                      | 답변 품질                |
| answer_correctness    | 답변 내용이 사실적으로 정확한가                                   | 답변 품질                |
| harmfulness           | 답변이 유해하거나 위험한 내용을 포함하는가 (0이면 안전)           | 안전성                   |
| maliciousness         | 악의적 의도나 공격적 행동을 유도하는가 (0이면 안전)               | 안전성                   |
| coherence             | 답변의 문장 흐름과 논리가 자연스러운가                            | 표현 품질                |
| correctness           | 전반적인 답변의 정확성과 타당성                                   | 답변 품질                |
| conciseness           | 답변이 불필요하게 장황하지 않고 간결한가                          | 표현 품질                |

RAG / 컨텍스트 기반 품질
→ 검색·컨텍스트 활용이 제대로 되었는가

답변 품질
→ 질문에 맞고 사실적으로 올바른가

표현 품질
→ 읽기 쉽고, 논리적이며, 간결한가

안전성
→ 유해·악의적 콘텐츠 여부

---

🔥 핵심 패턴 10개 ↔ PPT 시나리오 매핑

1️⃣ RAG = Knowledge Base / OpenSearch
📄 시나리오 (Vector DB PPT)
기업이 수백만 문서를 검색해서 답변 제공
기존 DB는 의미 검색 불가 → vector DB 필요
S3 → Bedrock KB → Vector Store → Retrieval

👉 03

💡 핵심
Knowledge Base → 빠른 구축
OpenSearch → 고급 검색
2️⃣ 정확도 문제 → Hybrid Search
📄 시나리오
“cloud security best practices” 같은 질의
semantic search만 하면 irrelevant 결과 발생
keyword + semantic 결합

👉 03

💡 핵심
BM25 + vector 결합
정확도 + 재현율 동시에 개선

3️⃣ hallucination → RAG + grounding
📄 시나리오 (Data / RAG PPT)
잘못된 데이터 → hallucination 발생
해결:
RAG
fact-check
grounding

👉 02

💡 핵심
“Garbage in → hallucination”
RAG로 근거 기반 응답

4️⃣ streaming → WebSocket + streaming API
📄 시나리오 (Integration / Performance PPT)
실시간 응답 (chat UX)
긴 응답 (LLM latency 문제)

👉 10

💡 핵심
API Gateway WebSocket
streaming 응답 구조

5️⃣ config → AppConfig
📄 시나리오 (Integration PPT)
모델 라우팅 / 설정 변경 필요
재배포 없이 변경

👉 10

💡 핵심
routing rule
model switching
A/B 테스트

6️⃣ governance → Prompt Management
📄 시나리오 (Prompt PPT)
프롬프트가 파편화됨 → 품질 불일치
해결:
중앙 관리
version control
A/B 테스트

👉04

💡 핵심
Prompt = 자산
lifecycle 관리 필요

7️⃣ safety → Guardrails
📄 시나리오 (AI Safety PPT)
위험:
prompt injection
harmful content
PII 노출

👉06

💡 핵심
input + output 필터링
defense-in-depth

8️⃣ multi-account data → Lake Formation (데이터 거버넌스)
📄 시나리오 (Integration / Data PPT)
데이터:
여러 시스템 (S3, CMS 등)
권한 / 계보 / 규제 필요

👉10

💡 핵심
access control
lineage
governance 필수

9️⃣ workflow → Step Functions
📄 시나리오 (Evaluation / Orchestration PPT)
AI workflow:
multi-step 처리
평가 pipeline
validation

👉09

💡 핵심
orchestration
retry / branching / automation

🔟 agent → Bedrock Agents / AgentCore
📄 시나리오 (AgentCore PPT)
단순 응답 ❌ → 목표 기반 행동
기능:
memory
tool 호출
reasoning

👉05

💡 핵심
Agent = workflow + reasoning + tools
🧠 전체 흐름 (중요)

이 PPT 전체를 하나로 연결하면:

Data → RAG → Prompt → Safety → Agent → Workflow → Observability → Optimization


|지표|설명|구분|
|---|---|---|
faithfulness|답변이 제공된 컨텍스트에 충실한가|답변품질|RAG/컨텍스트 기반 품질|
answer_relevancy|사용한 컨텍스트가 얼마나 정확/불필요 없이 쓰였는가
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

| 지표 | 설명 | 구분 |
|---|---|---|
| faithfulness | 답변이 제공된 컨텍스트에 충실한가 | RAG / 컨텍스트 기반 품질 |
| answer_relevancy | 답변이 질문 의도와 얼마나 관련 있는가 | 답변 품질 |
| context_precision | 사용한 컨텍스트가 정확하고 불필요한 정보 없이 활용되었는가 | RAG / 컨텍스트 기반 품질 |
| context_recall | 답변에 필요한 컨텍스트를 얼마나 빠짐없이 활용했는가 | RAG / 컨텍스트 기반 품질 |
| context_entity_recall | 컨텍스트 내 핵심 엔티티(개체, 고유명사 등)를 얼마나 잘 회수했는가 | RAG / 컨텍스트 기반 품질 |
| answer_similarity | 기준 답변(ground truth)과의 표현·내용 유사도 | 답변 품질 |
| answer_correctness | 답변 내용이 사실적으로 정확한가 | 답변 품질 |
| harmfulness | 답변이 유해하거나 위험한 내용을 포함하는가 (0이면 안전) | 안전성 |
| maliciousness | 악의적 의도나 공격적 행동을 유도하는가 (0이면 안전) | 안전성 |
| coherence | 답변의 문장 흐름과 논리가 자연스러운가 | 표현 품질 |
| correctness | 전반적인 답변의 정확성과 타당성 | 답변 품질 |
| conciseness | 답변이 불필요하게 장황하지 않고 간결한가 | 표현 품질 |


RAG / 컨텍스트 기반 품질
→ 검색·컨텍스트 활용이 제대로 되었는가

답변 품질
→ 질문에 맞고 사실적으로 올바른가

표현 품질
→ 읽기 쉽고, 논리적이며, 간결한가

안전성
→ 유해·악의적 콘텐츠 여부

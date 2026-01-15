### RAGAS - Evaluation


1. "모델이 질문에 대해 얼마나 정확하고, 문맥에 충실하며, 근거를 잘 사용해 답했는가?”를 정량적으로 평가한 결과"
2. 핵심 RAG/LLM 품질 지표

    - 검색 평가 지표

        | 지표                    | 의미                               |
        | --------------------- | -------------------------------- |
        | context_precision     | 가져온 컨텍스트가 질문에 얼마나 **불필요한 게 없는지** |
        | context_recall        | 정답에 필요한 정보가 **빠짐없이** 포함됐는지       |
        | context_entity_recall | 핵심 엔티티(회사, 연도, 지표 등)가 포함됐는지      |

    - 생성 평가 지표

        | 지표                 | 의미                     |
        | ------------------ | ---------------------- |
        | faithfulness       | 컨텍스트에 근거해 답했는가 (환각 여부) |
        | answer_relevancy   | 질문에 직접 답했는가            |
        | answer_similarity  | 정답과 의미적으로 얼마나 유사한가     |
        | answer_correctness | 사실적으로 맞는가              |

    - Critique (품질/안전)

        | 지표                          | 의미                    |
        | --------------------------- | --------------------- |
        | harmfulness / maliciousness | 유해·악의적 여부 (0이면 문제 없음) |
        | coherence                   | 문맥적으로 자연스러운가          |
        | correctness                 | 논리적으로 타당한가            |
        | conciseness                 | 불필요하게 장황하지 않은가        |


3. 표의 핵심 인사이트

    - 1. 숫자 관련 환각이 반복됨
        - faithfulness 낮은 row 대부분이 금액·증가율
        - 해결책:
            - 숫자 전용 chunk
            - 계산은 LLM이 아니라 코드로 분리

    - 2. 검색은 잘 됐는데 생성이 문제인 경우가 많음
        - context_precision / recall은 대부분 1.0
        - → 문제는 Retriever가 아니라 Generator

    - 3. 추론 질문일수록 relevancy 하락
        - Row 4처럼 “추론/평가” 질문
        - LLM이 컨텍스트 밖 상식·홍보 문구 사용

    - 4. 요약
        - 이 결과는 검색(RAG)은 대체로 잘 동작하지만, LLM이 숫자·추론 질문에서 컨텍스트를 벗어나 환각을 일으키는 문제 발생

4. 개선 방법

    - 숫자/계산 질문 → Tool 호출로 분리
    - faithfulness 낮은 row 자동 알람
    - 추론 질문은 “컨텍스트 기반으로만 답하라” 프롬프트 강화
    - answer_relevancy=0 사례는 즉시 거절

---

| idx | question | ground_truth | answer | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness |
|-----|----------|--------------|--------|--------------|------------------|-------------------|----------------|-----------------------|-------------------|--------------------|-------------|---------------|-----------|-------------|-------------|
| 0 | 2021년 AnyCompany Financial의 영업활동으로 인한 순현금 증가의 주요 원인은 무엇이었습니까? | An increase in net cash provided by operating activities was primarily due to increases in net income and favorable changes in operating assets and liabilities. | I don't know the answer to this question based on the provided information. | 0.5 | 0 | 0 | 0 | 0.25 | 0.5588 | 0.1397 | 0 | 0 | 1 | 1 | 1 |
| 1 | AnyCompany Financial의 투자활동으로 인한 순현금 유출이 가장 컸던 해는 언제였으며, 그 주요 원인은 무엇이었습니까? | AnyCompany Financial had the highest net cash used in investing activities in 2021 due to increased purchases of PPE and securities. | I don't know. The provided information does not include details about investing activities. | 0.25 | 0 | 0 | 0 | 0.3333 | 0.7031 | 0.1758 | 0 | 0 | 1 | 1 | 1 |
| 2 | 2021년 AnyCompany Financial의 재무활동으로 인한 주요 현금 유입원은 무엇이었습니까? | The primary source was proceeds from issuance of common stock and long-term debt. | 재무활동으로 인한 주요 현금 유입원은 주식 발행 및 장기 부채 증가입니다. | 0.4286 | 0.7443 | 0.2 | 1 | 0.5 | 0.7200 | 0.5891 | 0 | 0 | 1 | 0 | 1 |
| 3 | AnyCompany Financial의 2020년 대비 2021년 현금 및 현금성 자산의 전년 대비 변동률을 계산하십시오. | 37.14% increase | 문맥에 수치가 없어 계산할 수 없습니다. | 0 | 0 | 0.325 | 0 | 0.2857 | 0.4430 | 0.1108 | 0 | 0 | 1 | 0 | 1 |
| 4 | 제공된 정보를 바탕으로 AnyCompany Financial의 전반적인 재무 건전성과 성장 전망에 대해 무엇을 추론할 수 있습니까? | The company appears financially healthy with good growth prospects. | 재무 건전성과 성장 전망이 긍정적이라고 추론할 수 있습니다. | 0.0556 | 0 | 0 | 0 | 0.1429 | 0.7400 | 0.7183 | 0 | 0 | 1 | 1 | 1 |


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
    - “모델이 못해서”가 아니라 “문서를 못 써서” 틀린 경우가 많다
        - answer_relevancy = 0
        - context_recall = 0
            - Retriever 문제
    - Faithfulness는 높지만 정답은 아닌 경우
        - Hallucination은 없음
        - 하지만 질문에 답을 안 함
            - 보수적인 LLM 응답 패턴
    - RAG 품질은 단일 점수가 아니라 “조합”으로 봐야 한다
        - 좋은 답 :
            - context_recall ↑
            - answer_relevancy ↑
            - answer_correctness ↑
        - 위험한 답:
            - answer_similarity ↑
            - faithfulness ↓ (→ 환각 가능성)

4. LLM 개선 포인트가 ‘모델’, ‘프롬프트’, ‘리트리버’, ‘문서 품질’ 중 어디인지 판단할 수 있음

| id | question | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness | explain |
|----|----------|--------------|------------------|-------------------|----------------|-----------------------|-------------------|--------------------|------------|---------------|-----------|-------------|-------------|---|
| 0 | What was the primary reason for the increase in net cash by operating activities for AnyCompany Financial in 2021? | 0.333333 | 0.965909 | 1.0 | 1.0 | 0.25 | 0.594305 | 0.748576 | 0 | 1 | 1 | 1 | 1 | - 검색은 완벽(context_precision/recall=1) - 숫자 환각 → faithfulness 낮음|
| 1 | Which year did AnyCompany Financial have the highest net cash used in investing activities, what was the primary reason? | 0.75 | 0.793210 | 1.0 | 1.0 | 0.222222 | 0.979912 | 0.844978 | 0 | 1 | 1 | 1 | 1 | |
| 2 | What was the primary source of cash inflows from financing activities for AnyCompany Financial in 2021? | 0.75 | 0.995493 | 1.0 | 1.0 | 0.25 | 0.929095 | 0.832274 | 0 | 0 | 1 | 1 | 1 | |
| 3 | Calculate the year-over-year percentage change in cash and cash equivalents for AnyCompany Financial from 2020 to 2021. | 0.0 | 0.851156 | 1.0 | 1.0 | 0.4 | 0.826301 | 0.394075 | 0 | 0 | 1 | 1 | 1 | - 계산은 맞아 보이지만 - 컨텍스트 기반 검증 실패 → faithfulness=0, answer_correctness 낮음|
| 4 | With the information provided, what can you infer about AnyCompany Financial's overall financial health and growth prospects? | 0.733333 | 0.0 | 0.0 | 0.4 | 0.1 | 0.875782 | 0.697669 | 0 | 0 | 1 | 1 | 1 | - 문장은 그럴듯하지만 - 질문과 직접적 연관 부족 → answer_relevancy=0|



---

| idx | question | ground_truth | answer | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness |
|-----|----------|--------------|--------|--------------|------------------|-------------------|----------------|-----------------------|-------------------|--------------------|-------------|---------------|-----------|-------------|-------------|
| 0 | 2021년 AnyCompany Financial의 영업활동으로 인한 순현금 증가의 주요 원인은 무엇이었습니까? | An increase in net cash provided by operating activities was primarily due to increases in net income and favorable changes in operating assets and liabilities. | I don't know the answer to this question based on the provided information. | 0.5 | 0 | 0 | 0 | 0.25 | 0.5588 | 0.1397 | 0 | 0 | 1 | 1 | 1 |
| 1 | AnyCompany Financial의 투자활동으로 인한 순현금 유출이 가장 컸던 해는 언제였으며, 그 주요 원인은 무엇이었습니까? | AnyCompany Financial had the highest net cash used in investing activities in 2021 due to increased purchases of PPE and securities. | I don't know. The provided information does not include details about investing activities. | 0.25 | 0 | 0 | 0 | 0.3333 | 0.7031 | 0.1758 | 0 | 0 | 1 | 1 | 1 |
| 2 | 2021년 AnyCompany Financial의 재무활동으로 인한 주요 현금 유입원은 무엇이었습니까? | The primary source was proceeds from issuance of common stock and long-term debt. | 재무활동으로 인한 주요 현금 유입원은 주식 발행 및 장기 부채 증가입니다. | 0.4286 | 0.7443 | 0.2 | 1 | 0.5 | 0.7200 | 0.5891 | 0 | 0 | 1 | 0 | 1 |
| 3 | AnyCompany Financial의 2020년 대비 2021년 현금 및 현금성 자산의 전년 대비 변동률을 계산하십시오. | 37.14% increase | 문맥에 수치가 없어 계산할 수 없습니다. | 0 | 0 | 0.325 | 0 | 0.2857 | 0.4430 | 0.1108 | 0 | 0 | 1 | 0 | 1 |
| 4 | 제공된 정보를 바탕으로 AnyCompany Financial의 전반적인 재무 건전성과 성장 전망에 대해 무엇을 추론할 수 있습니까? | The company appears financially healthy with good growth prospects. | 재무 건전성과 성장 전망이 긍정적이라고 추론할 수 있습니다. | 0.0556 | 0 | 0 | 0 | 0.1429 | 0.7400 | 0.7183 | 0 | 0 | 1 | 1 | 1 |


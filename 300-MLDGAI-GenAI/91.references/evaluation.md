
1. "모델이 질문에 대해 얼마나 정확하고, 문맥에 충실하며, 근거를 잘 사용해 답했는가?”를 정량적으로 평가한 결과"
2. 핵심 RAG/LLM 품질 지표
    - Faithfulness 계열 (근거 충실도)
        - faithfulness : 답변이 contexts에 근거해서만 작성되었는가
        - context_precision : 사용한 문서가 불필요한 내용 없이 정확했는가
        - context_recall : 정답에 필요한 문서를 빠뜨리지 않고 가져왔는가
        - context_entity_recall : 중요한 **개체(숫자, 회사, 연도 등)**를 잘 포함했는가
    - Answer 품질 계열
        - answer_relevancy : 질문에 직접적으로 답했는가
        - answer_similarity : 정답(ground_truth)과 의미적으로 얼마나 유사한가
        - answer_correctness : 사실적으로 맞는 답인가
    - 안전성 / 표현 품질
        - harmfulness : 유해한 내용 여부
        - maliciousness	: 악의적 의도 여부
        - coherence	: 문장이 논리적으로 자연스러운가
        - correctness : 전체적인 정합성
        - conciseness :	불필요하게 장황하지 않은가
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

| idx | question | ground_truth | answer | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness |
|-----|----------|--------------|--------|--------------|------------------|-------------------|----------------|-----------------------|-------------------|--------------------|-------------|---------------|-----------|-------------|-------------|
| 0 |  |  | | 0.5 | 0 | 0 | 0 | 0.25 | 0.5588 | 0.1397 | 0 | 0 | 1 | 1 | 1 |
| 1 | |  | |  0.25 | 0 | 0 | 0 | 0.3333 | 0.7031 | 0.1758 | 0 | 0 | 1 | 1 | 1 |
| 2 | |  | |  0.4286 | 0.7443 | 0.2 | 1 | 0.5 | 0.7200 | 0.5891 | 0 | 0 | 1 | 0 | 1 |
| 3 | |  | |  0 | 0 | 0.325 | 0 | 0.2857 | 0.4430 | 0.1108 | 0 | 0 | 1 | 0 | 1 |
| 4 | |  | |  0.0556 | 0 | 0 | 0 | 0.1429 | 0.7400 | 0.7183 | 0 | 0 | 1 | 1 | 1 |

---

| idx | question | ground_truth | answer | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness |
|-----|----------|--------------|--------|--------------|------------------|-------------------|----------------|-----------------------|-------------------|--------------------|-------------|---------------|-----------|-------------|-------------|
| 0 | 2021년 AnyCompany Financial의 영업활동으로 인한 순현금 증가의 주요 원인은 무엇이었습니까? | An increase in net cash provided by operating activities was primarily due to increases in net income and favorable changes in operating assets and liabilities. | I don't know the answer to this question based on the provided information. | 0.5 | 0 | 0 | 0 | 0.25 | 0.5588 | 0.1397 | 0 | 0 | 1 | 1 | 1 |
| 1 | AnyCompany Financial의 투자활동으로 인한 순현금 유출이 가장 컸던 해는 언제였으며, 그 주요 원인은 무엇이었습니까? | AnyCompany Financial had the highest net cash used in investing activities in 2021 due to increased purchases of PPE and securities. | I don't know. The provided information does not include details about investing activities. | 0.25 | 0 | 0 | 0 | 0.3333 | 0.7031 | 0.1758 | 0 | 0 | 1 | 1 | 1 |
| 2 | 2021년 AnyCompany Financial의 재무활동으로 인한 주요 현금 유입원은 무엇이었습니까? | The primary source was proceeds from issuance of common stock and long-term debt. | 재무활동으로 인한 주요 현금 유입원은 주식 발행 및 장기 부채 증가입니다. | 0.4286 | 0.7443 | 0.2 | 1 | 0.5 | 0.7200 | 0.5891 | 0 | 0 | 1 | 0 | 1 |
| 3 | AnyCompany Financial의 2020년 대비 2021년 현금 및 현금성 자산의 전년 대비 변동률을 계산하십시오. | 37.14% increase | 문맥에 수치가 없어 계산할 수 없습니다. | 0 | 0 | 0.325 | 0 | 0.2857 | 0.4430 | 0.1108 | 0 | 0 | 1 | 0 | 1 |
| 4 | 제공된 정보를 바탕으로 AnyCompany Financial의 전반적인 재무 건전성과 성장 전망에 대해 무엇을 추론할 수 있습니까? | The company appears financially healthy with good growth prospects. | 재무 건전성과 성장 전망이 긍정적이라고 추론할 수 있습니다. | 0.0556 | 0 | 0 | 0 | 0.1429 | 0.7400 | 0.7183 | 0 | 0 | 1 | 1 | 1 |

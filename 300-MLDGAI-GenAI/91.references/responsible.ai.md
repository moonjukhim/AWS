### 편향 완화

1. 데이터 단계에서의 편향 완화 (가장 중요)
    - 데이터 다양성 확보
        - 성별, 연령, 지역, 언어, 문화가 균형 잡힌 데이터 수집
    - 편향 데이터 제거·보정
        - 차별적 표현, 혐오 발언, 극단적 관점 필터링
    - 리샘플링 / 가중치 조정
        - 소수 집단 데이터를 oversampling
        - 다수 집단 데이터에 낮은 가중치 부여
    - 데이터 라벨 편향 점검
        - 라벨러의 주관이 반영되지 않았는지 교차 검증

2. 모델 설계 단계에서의 편향 완화
    - Fairness-aware objective
        - 정확도 + 공정성 제약 조건을 동시에 최적화
    - Adversarial Debiasing
        - 모델이 예측하면서 동시에 “성별·인종을 추론하지 못하게” 방해
    - Representation Debiasing
        - 내부 임베딩에서 민감 속성 정보 제거

3. 학습(Training) 단계에서의 편향 완화
    - Counterfactual Data Augmentation
        - “남자 의사 → 여자 의사”처럼 문맥은 유지하고 속성만 변경
    - Bias-aware Fine-tuning
        - 편향 사례 중심 데이터로 재학습
    - RLHF (Human Feedback)
        - 편향적 응답에 페널티
        - 중립·균형 응답에 보상

4. 추론(Inference) 단계에서의 편향 완화
    - 프롬프트 가드
        - “중립적 관점에서”, “다양한 시각을 반영해”
    - 출력 필터링 (Guardrails)
        - 차별, 혐오, 고정관념 감지 후 수정/차단
    - Self-critique / Reflection
        - 모델이 스스로 “편향 가능성 점검” 후 재답변

5. 평가·운영 단계에서의 편향 완화 (AIOps 관점)
    - Bias Metrics
        - Demographic Parity
        - Equalized Odds
        - Group-wise Error Rate
    - 사용자 피드백 루프
        - 편향 신고 → 재학습 데이터 반영
    - 모델 카드 & 데이터 카드
        - “어떤 편향이 존재할 수 있는지” 문서화
    - 정기 재평가
        - 사회·문화 변화에 따라 기준 업데이트


### 자동 추론 검사(Automated Reasoning checks)

1. 정확성(Accuracy) 지표 계산법

“사실에 맞는가?”

    - ① Fact Accuracy (사실 정확도) : 모델 응답에 포함된 사실 주장(factual claims) 중, 실제로 옳은 비율

        ```text
        Fact Accuracy = (검증된 사실 주장 수) / (전체 사실 주장 수)
        ```

    - ② Claim Correction Rate (오류 수정률) : 자동 추론 검사 후 잘못된 주장을 올바르게 수정한 비율

        ```text
        Correction Rate = (수정 성공한 오류 수) / (발견된 오류 수)
        ```

2. 신뢰성(Reliability) 지표 계산법

“논리적으로 일관되고 재현 가능한가?”

    - ① Logical Consistency Score (논리 일관성) : 응답 내에서 논리적 모순이 없는 비율

        ```text
        Logical Consistency = 1 - (모순 문장 수 / 전체 논리 문장 수)
        ```

    - ② Reproducibility Score (재현성) : 같은 질문을 여러 번 했을 때 결론이 유지되는 정도

        ```text
        Reproducibility = (동일 결론 횟수) / (전체 반복 횟수)
        ```
    
    - ③ Confidence Calibration Error : 모델의 자신감 표현과 실제 정확도의 차이

        ```text
        Calibration Error = |평균 자신감 - 실제 정확도|
        ```

3. 투명성(Transparency) 지표 계산법

“왜 이런 답을 했는가를 설명하는가?”

    - ① Explanation Coverage (설명 포함률) : 결론에 대해 이유/근거가 함께 제공된 비율

    ```text
    Explanation Coverage = (설명이 포함된 응답 수) / (전체 응답 수)
    ```

    - ② Reasoning Trace Completeness (추론 완전성) : 결론에 도달하기까지의 추론 단계가 빠짐없이 제시되었는지

        ```text
        Trace Completeness = (필수 추론 단계 수 충족 여부 평균)
        ```
    
    - ③ Grounded Explanation Score (근거 연결 점수) : 설명이 **실제 근거(문서·데이터)**와 연결되어 있는 정도

        ```text
        Grounded Score = (근거가 명확히 연결된 설명 수) / (전체 설명 수)
        ```

4. 종합 점수 계산 예시

    ```text
    Automated Reasoning Score =
    0.4 × Accuracy
    + 0.35 × Reliability
    + 0.25 × Transparency
    ```

    - 서비스 목적에 따라 가중치 조정
        - 의료 / 금융 → Accuracy ↑
        - 정책 / 설명형 AI → Transparency ↑

5. 요약

| 항목   | 대표 지표                | 계산 포인트    |
| ---   | -------------------- | --------- |
| 정확성 | Fact Accuracy        | 사실이 맞는가   |
|       | Correction Rate      | 틀린 걸 고쳤는가 |
| 신뢰성 | Logical Consistency  | 논리적 모순    |
|       | Reproducibility      | 결과가 흔들리는가 |
| 투명성 | Explanation Coverage | 설명을 했는가   |
|       | Grounded Score       | 근거가 연결됐는가 |

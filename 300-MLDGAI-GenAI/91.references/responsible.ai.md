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

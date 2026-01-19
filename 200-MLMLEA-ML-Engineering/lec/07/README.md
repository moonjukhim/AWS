### 

- 주제 A. 모델 성능 평가

    - 1) 왜 성능 평가가 중요한가?
        - 학습 데이터에서만 잘 맞는 모델은 실 환경에서 실패
        - 비즈니스 목적에 맞는 지표를 선택하지 않으면 잘못된 의사결정 발생

    - 2) 대표적인 평가 지표 (문제 유형별)
        - 분류(Classification)
            - Accuracy: 전체 중 맞춘 비율 → 클래스 불균형 시 위험
            - Precision / Recall
                - Precision: 맞다고 한 것 중 진짜 맞은 비율
                - Recall: 진짜 맞아야 할 것 중 찾아낸 비율
            - F1-score: Precision과 Recall의 균형
            - AUC-ROC: 임계값 변화에 따른 분류 성능


        - 회귀(Regression)
            - MAE: 평균 절대 오차 (해석 쉬움)
            - MSE / RMSE: 큰 오차에 페널티 큼
            - R²: 설명력 지표


        - 시계열(Time Series)
            - MAPE: 퍼센트 오차
            - SMAPE: 극단값 완화
            - WAPE: 대규모 데이터에 안정적

- 주제 B. 훈련 시간 단축 기법

    - 대표적인 훈련 시간 단축 방법
        - 데이터 측면
            - 불필요한 피처 제거
            - 샘플링 (전체 → 일부)
            - 데이터 타입 최적화 (float64 → float32)
        
        - 모델/학습 설정
            - Early Stopping
                - 성능이 더 이상 개선되지 않으면 중단
            - Batch Size 증가
                - GPU 활용률 증가
            - Mixed Precision Training
                - FP16 사용 → 속도 & 메모리 절감

        - 인프라 활용
            - 멀티 GPU / 분산 학습
            - Spot 인스턴스 활용 (비용 ↓)
            - 적절한 인스턴스 타입 선택

- 주제 C. 하이퍼파라미터 튜닝 기법

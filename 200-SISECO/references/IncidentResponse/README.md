### 방법 비교

| 방법                               | 장점                      | 단점                     | 적합한 경우             |
|-----------------------------------|---------------------------|--------------------------|--------------------------|
| **Lambda**                        | 간단하고 빠름             | 실행 시간 제한(15분)     | 경량 인시던트 처리       |
| **Step Functions**                | 시각적, 제어 가능         | 약간의 러닝커브          | 복잡한 다단계 대응       |
| **Systems Manager Automation**    | 운영 자동화에 최적      | 일부 작업 제한 있음      | 스냅샷, 격리, 태그        |
| **EventBridge + Fargate**         | 무제한 실행              | 구성 복잡                | 긴 시간 작업, 포렌식     |
| **CodePipeline + CFN**            | IaC 기반 자동화           | 느릴 수 있음             | 새 환경 자동 생성 시     |

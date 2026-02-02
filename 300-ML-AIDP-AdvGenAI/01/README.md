| 위치         | 방식                | 추천 상황           |
| ---------- | ----------------- | --------------- |
| App 내부     | 라이브러리             | 마이크로서비스         |
| API 앞단     | API Gateway / ALB | 외부 트래픽 보호       |
| Serverless | Lambda + DynamoDB | Bedrock / FM 호출 |
| Kubernetes | Service Mesh      | 대규모 MSA         |
| 워크플로우      | Step Functions    | 복잡한 장애 제어       |

Circuit Breaker는 “기술”이 아니라 “위치 선택”의 문제다.
가장 가까운 곳에서, 가장 단순하게 끊는 게 정답이다.
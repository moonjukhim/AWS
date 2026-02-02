| 위치         | 방식                | 추천 상황           |
| ---------- | ----------------- | --------------- |
| App 내부     | 라이브러리             | 마이크로서비스         |
| API 앞단     | API Gateway / ALB | 외부 트래픽 보호       |
| Serverless | Lambda + DynamoDB | Bedrock / FM 호출 |
| Kubernetes | Service Mesh      | 대규모 MSA         |
| 워크플로우      | Step Functions    | 복잡한 장애 제어       |

Circuit Breaker는 “기술”이 아니라 “위치 선택”의 문제다.
가장 가까운 곳에서, 가장 단순하게 끊는 게 정답이다.

---

# AIOps 프로젝트 전체 수명 주기 (End-to-End)

 아이디어 → 설계 → 구현 → 운영 → 개선으로 이어지는 순환형 라이프사이클입니다.

 전략 수립
 → 데이터 준비
   → RAG / 검색 설계
     → 프롬프트 & 에이전트
       → 보안·안전
         → 성능·비용 최적화
           → 관측 & 평가
             → 지속적 개선
               ↺ (다시 전략으로)


## 평가 항목

1. 성능 평가 (Model Capability & Quality) - 우리 문제를 잘 푸는가
2. 도메인 적합성 평가 (Domain Fit) - 우리 업종에 맞는가
3. 비즈니스 연계 평가 (Business Alignment)
4. 성능 & 확장성 평가 (Performance & Scalability) - 교체·확장 가능한가
5. 비용 평가 (Cost & Economics) - 운영까지 감당 가능한가
6. 한계 & 리스크 평가 (Limitation Analysis) - 어디까지 믿을 수 있는가
7. 완화 전략 평가 (Mitigation Readiness) - 실패 시 대안이 있는가

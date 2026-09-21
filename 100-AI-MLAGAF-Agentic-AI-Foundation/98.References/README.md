### References

[agentcore-samples](https://github.com/awslabs/agentcore-samples)

##### event=driven-claims-agent

보험 청구가 이메일로 들어오면 자동으로 판단하고, 확신도에 따라 자동 처리와 사람 검토로 나눕니다.

- 사례의 "이메일 수신 → 분류 → 자동 처리 또는 사람에게 전달" 흐름과 거의 같습니다.

| 사례 요구사항    | 샘플에서 구현된 부분                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------ |
| 대량 이메일 수신 | SES → S3(`claims-inbox`) → EventBridge → Lambda → AgentCore Runtime (비동기 이벤트 방식)   |
| A. 분류          | Validation Agent가 분류를 맡고, 비용을 줄이려고 Haiku 모델을 씀 (`main.py`의 cost routing) |
| B. 자동 응답     | `CONFIDENCE >= 80`이면 `AUTO_APPROVE`, SES로 알림 메일 발송                                |
| C. 에스컬레이션  | `CONFIDENCE < 80`이면 `HUMAN_REVIEW`로 보냄. Cedar 정책이 10만 달러 이상 청구를 차단       |
| D. 후속 추적     | Memory (`SEMANTIC + SUMMARIZATION`)로 같은 청구인이 다시 오면 알아봄                       |

확인내용 : 라우팅과 프롬프트 체이닝 패턴(두 에이전트 순차 실행), Human-in-the-loop, AgentCore
Policy·Memory·Evaluation.

---

##### Bedrock flows

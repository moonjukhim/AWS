##

- #### 항목별 설정 위치

| 슬라이드 항목            | 설정 위치                        | 설정 방법                                               |
| ------------------------ | -------------------------------- | ------------------------------------------------------- |
| 유휴 시간 제한           | AgentCore Runtime / 애플리케이션 | Runtime의 세션 수명 정책 및 애플리케이션 세션 관리      |
| 최대 실행 시간 8시간     | AgentCore Runtime                | Runtime의 실행 제한 확인 및 애플리케이션 작업 시간 관리 |
| `/ping` 상태 확인        | 에이전트 애플리케이션 코드       | 상태 확인 엔드포인트 구현 및 외부 모니터링              |
| 세션 30분 초과           | CloudWatch                       | 세션 시작·종료 기록을 기반으로 경보 구성                |
| 5분 동안 50회 초과 호출  | CloudWatch Alarms                | 호출 수를 집계하는 사용자 지정 지표와 경보              |
| 동일 도구 10회 연속 호출 | 에이전트 코드 / CloudWatch       | 도구 호출 횟수와 연속 실행 패턴 감지                    |
| 토큰 사용량 2배          | CloudWatch                       | 토큰 사용량 지표, 기준선 및 경보                        |
| 오류율 5% 초과           | CloudWatch Alarms                | 오류율을 계산하는 지표 수식 및 경보                     |
| 자동 세션 종료           | 애플리케이션 / 운영 자동화       | 경보에 따른 세션 종료 로직                              |
| 운영팀 에스컬레이션      | CloudWatch + SNS                 | 경보를 이메일, SNS 또는 운영 시스템에 전달              |
| 회로 차단기              | 애플리케이션 코드                | 반복 실패 시 도구 호출을 일시 중단하는 로직             |

--

## WAF

- [sample-well-architected-custom-lens](https://github.com/aws-samples/sample-well-architected-custom-lens)

- [Responsible AI Lens Whitepaper](https://docs.aws.amazon.com/pdfs/wellarchitected/latest/responsible-ai-lens/responsible-ai-lens.pdf?utm_source=chatgpt.com)

https://github.com/aws-samples/sample-well-architected-custom-lens/blob/main/responsible-ai-lens/responsible-ai-lens.json?utm_source=chatgpt.com

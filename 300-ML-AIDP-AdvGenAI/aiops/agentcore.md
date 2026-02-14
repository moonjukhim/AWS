### Case 1 : 레거시 CMS API 표준화

##### 문제 상황 요약

- 여러 AI 에이전트 워크플로가 레거시 CMS API와 상호작용
- CMS API는:
  - 엔드포인트 설계가 일관되지 않음
  - 응답 스키마 문서화 부족
  - 엣지 케이스 처리 복잡
- 모든 AI 워크플로에서 재사용 가능해야 함
- 기존 CMS API는 변경할 수 없음
- 운영 오버헤드는 최소화해야 함

```text
AI Agent Workflow
        ↓
Amazon Bedrock AgentCore
        ↓
MCP (표준화 계층)
        ↓
Legacy CMS API
```

### Case 2 : 장기 문서 처리 + 에이전트 추론

- 상황

  - 문서 업로드
  - OCR 수행
  - 구조화
  - 여러 단계 분석
  - 최종 보고서 생성

- 구조

```text
S3 Upload
   ↓
Step Functions
   ├─ OCR (Textract)
   ├─ 데이터 정제
   ├─ 검증
   └─ AgentCore 호출 (분석/요약/추론)
```

- 왜 결합?
  - Step Functions → 장기 실행 관리
  - AgentCore → 추론 + 툴 호출

---

### 2️⃣ 승인 워크플로 + AI 판단

📌 상황

금융 신청서 처리

사기 탐지

리스크 평가

사람이 최종 승인

🏗 구조
API Gateway
↓
Step Functions
├─ 기본 검증
├─ AgentCore 호출 (리스크 분석)
├─ 조건 분기
└─ Human Approval

🎯 포인트

AgentCore는 판단

Step Functions는 프로세스 통제

3️⃣ 이벤트 기반 AI 자동화
📌 상황

EventBridge 이벤트 발생

여러 시스템 호출 필요

AI가 어떤 액션을 할지 결정

🏗 구조
EventBridge
↓
Step Functions
├─ 컨텍스트 수집
├─ AgentCore 호출 (Action 결정)
├─ 결과 기반 외부 시스템 호출
└─ 결과 기록

🎯 사용 이유

Step Functions = 이벤트 흐름

AgentCore = 행동 선택

### 4️⃣ 멀티에이전트 + 외부 시스템 대량 호출

📌 상황

Supervisor Agent 필요

여러 하위 에이전트 존재

실패 재시도 중요

🏗 구조
Step Functions
├─ 데이터 준비
├─ AgentCore (Supervisor)
│ ├─ Sub Agent 호출
│ ├─ 툴 호출
│ └─ 결과 통합
├─ 실패 시 재시도
└─ 결과 저장

### 5️⃣ 규정 준수 + 감사 로깅 요구

📌 상황

모든 AI 호출 감사 필요

실패 시 롤백

SLA 보장

🎯 결합 이유
요구사항 해결
감사 추적 Step Functions
복잡 추론 AgentCore
오류 재시도 Step Functions
툴 호출 AgentCore

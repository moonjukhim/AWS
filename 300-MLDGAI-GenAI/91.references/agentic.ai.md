### AWS Agentic AI

| 구분                  | 핵심 서비스             | 자율성   | 제어력   | 운영 난이도 | 추천 상황         |
| ------------------- | ------------------ | ----- | ----- | ------ | ------------- |
| **① Bedrock Agent** | Bedrock Agents     | 중     | 높음    | 낮음     | 엔터프라이즈, 빠른 도입 |
| **② 오픈소스 Agent**  | LangGraph / CrewAI | 높음    | 중     | 높음     | 복잡한 멀티 에이전트   |
| **③ 워크플로우 기반**  | Step Functions     | 낮음    | 매우 높음 | 중      | 규정·감사 필수      |
| **④ 하이브리드**      | Agent + UI 자동화     | 매우 높음 | 중     | 높음     | 사람 업무 대체      |

##### ① Amazon Bedrock Agents 기반

```text
User
 ↓
Bedrock Agent
 ↓
Action Group (Lambda / API)
 ↓
AWS Services / RAG
```

🟢 적합한 사례

- 고객 지원 Agent
- 사내 Q&A / 정책 상담
- 표준 업무 자동화 (IT Helpdesk)

##### ② 오픈소스 Agent 프레임워크 (LangGraph / CrewAI)

```text
User / Event
 ↓
Supervisor Agent
 ↓
Planner / Tool Agent / Critic
 ↓
AWS SDK / Bedrock / OpenSearch
```

🟢 적합한 사례

- AIOps (원인 분석 → 대응)
- 리서치/분석 에이전트
- 자율 의사결정 시스템

##### ③ AWS Step Functions 기반 (Pseudo-Agent)

```text
Event
 ↓
Step Functions
 ↓
(LLM 판단 → Lambda → 승인 → 실행)
```

🟢 적합한 사례

- 금융/공공 자동화
- 승인 기반 운영
- 규정 엄격한 환경

##### ④ 하이브리드 (Agent + 브라우저/UI 자동화)

```text
Agent (Bedrock / LangGraph)
 ↓
Action Plan
 ↓
UI Executor (Browser Automation)
```

🟢 적합한 사례

- 레거시 운영 자동화
- SaaS 콘솔 조작
- 구매·리서치 Agent

---

# AIOps

```text
[ Observability ]
CloudWatch / OpenSearch
        ↓
[ Reasoning ]
LangGraph Agent (Bedrock LLM)
        ↓
[ Control Layer ]
Step Functions (중요 액션)
        ↓
[ Action ]
API 호출 + UI 자동화
```
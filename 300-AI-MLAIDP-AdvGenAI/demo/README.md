## 1순위

D1. Strands에서 AgentCore까지 (모듈 5, 45~60분)

- 순서: Strands 에이전트를 로컬에서 정의(모델, 도구, 시스템 프롬프트) → AgentCore Runtime에 배포 → Memory 추가 →
  Gateway로 Lambda를 MCP 도구로 노출 → CloudWatch GenAI Observability에서 트레이스 확인
- 상위 폴더의 agentcore-samples-main.zip에 그대로 쓸 수 있는 자료가 있습니다.
  - 06-workshops/01-AgentCore-runtime
  - 02-gateway
  - 04-memory
  - 06-observability
  - 여유가 있으면 07-evaluations, 08-policy
- 슬라이드 18의 Bedrock Agents와 AgentCore 차이도 실제 코드로 보여줄 수 있습니다.

D2. 고객지원 라우팅 플로우 (모듈 4 슬라이드 35, 30분)

- Prompt Management에서 페르소나별 프롬프트 버전과 변형(variant)을 만듭니다.
- Prompt Flows를 구성합니다: 의도 분류 → Condition 노드 → 전문 프롬프트 → Lambda(가짜 CRM 조회) → JSON 스키마 구조화 출력
- 같은 프롬프트의 두 버전을 비교해 A/B 테스트를 보여줍니다.
- 랩 2가 기초 수준이라 이 데모가 모듈 4의 핵심 내용을 대신 전달하게 됩니다.

D3. RAG 평가 (모듈 9 슬라이드 43, 30~36분)

- 랩 1에서 만든 KB를 재사용합니다.
- Bedrock Evaluations의 RAG 평가 작업(LLM-as-a-Judge, 충실도·관련성 등)과 사용자 지정 지표를 시연합니다.
- Python 스크립트로 Precision@K, MRR, NDCG를 계산합니다.
- 장황함 편향을 일부러 재현합니다. 모듈 9 퀴즈 2번과 연결됩니다.

## 2순위: 개념 전달 효과가 큰 것

D4. 모델 독립 라우팅과 복원력 (모듈 1, 20분)

- Converse API로 모델 ID만 바꿔 호출하고 지연 시간과 토큰을 비교합니다.
- 교차 리전 추론 프로파일을 보여줍니다.
- 간단한 회로 차단기와 폴백 코드를 시연합니다.
- Bedrock Intelligent Prompt Routing은 "동적 모델 선택"의 관리형 기능인데 덱에 언급이 없어서 보강 가치가 큽니다.

D5. 비용 최적화 실측 (모듈 7과 모듈 2, 20분)

- 프롬프트 캐싱: cachePoint 적용 전후의 cacheReadInputTokens를 비교합니다.
- Batch inference 작업을 보여줍니다.
- Titan 임베딩으로 시맨틱 캐시를 시연합니다. "암호 재설정" 같은 유사 질의가 캐시 적중되는 장면을 보여줍니다.

D6. 관찰성 (모듈 8, 15분)

- Model Invocation Logging을 켜고 CloudWatch Logs Insights로 사용자별·앱별 토큰을 쿼리합니다.
- 애플리케이션 추론 프로파일과 태그로 비용을 배분합니다.
- D1의 AgentCore 대시보드와 연결해서 설명합니다.

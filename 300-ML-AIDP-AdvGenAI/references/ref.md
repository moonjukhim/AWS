### 1. Foundation Model Selection & Configuration

- 모델 선택은 프레임워크 문제
- 성능은 벤치마크, 가치는 비즈니스로 평가
- 멀티 모델 + 동적 선택이 엔터프라이즈 표준
- 장애·비용·전환은 설계로 해결
- Foundation Model은 운영 자산

### 2. Data Quality for FM

- 데이터 품질은 FM 성능의 전제 조건
- 자동 검증 + 도메인 로직 필수
- 멀티모달은 병렬 + 순차 혼합
- 비용·성능 최적화의 핵심은 입력 관리
- 토큰을 줄이는 것이 ROI를 키운다

### 3. Vector DB & Retrieval Augmentation

- RAG 성능 = 벡터 DB 설계 + Chunking + 검색 전략
- Bedrock KB는 빠른 시작, OpenSearch는 고급 제어
- Hybrid Search는 필수
- 문서 구조·메타데이터를 이해하지 못하면 실패
- 지식 어시스턴트는 검색 + 대화 + 보안 시스템

### 4. Prompt Engineering & Governance

- Prompt를 시스템 자산으로 인식
- Role·Context·출력 구조화가 품질을 결정
- CoT는 복잡한 비즈니스 문제의 기본
- Prompt Flow로 워크플로우화
- Governance 없으면 엔터프라이즈 불가

### 5. Implementing Agentic AI Frameworks with Amazon Bedrock AgentCore

- Agentic AI는 "자동화"를 넘어 "자율 실행"
- 운영 가능한 에이전트에는 전용 플랫폼이 필요
- Amazon Bedrock AgentCore는 [빌드 + 배포 + 운영 + 보안 + 평가]를 통합
- 오픈소스 에이전트 프레임워크의 엔터프라이즈 종착점

### 6. AI Safety & Security

- AI 안전은 기능이 아니라 아키텍처
- Guardrails + Testing + Monitoring 필수
- Privacy-by--Design은 전제 조건
- Zero-Trust는 AI에도 적용
- 신뢰 가능한 AI = 설명 + 감사 + 인간 개입

### 7. Performance Optimization & Cost Management

- 컨텍스트 슬라이딩/요약 적용
- 토큰·비용 실시간 대시보드
- 동적 배치 & 예측 스케일링
- 다층(엣지+의미) 캐싱
- 자동 비용 트리거(모델/컨텍스트 전환)

### 8.Monitoring & Observability for Generative AI

- GenAI 모니터링은 기술+품질+비즈니스 통합 관측
- 토큰 = 비용 = 지연
- 고정 SLA ❌, 동적 기준선 ✅
- 이유를 설명할 수 있어야 신뢰
- 측정하지 못하면 개선도 불가

### 9. Testing, Validation & Continuous Improvement

- GenAI 테스트는 다차원·자동·지속적
- 평가 파이프라인은 CI/CD 일부
- LLM-as-a-Judge는 필수지만 편향 관리 필요
- RAG는 검색 품질이 절반
- 측정 → 개선 → 검증 루프가 품질을 만든다

### 10. Enterprise Integration Patterns

- 엔터프라이즈 AI는 통합 시스템
- REST + Event-driven 패턴 조합
- 보안·ID는 기존 체계에 통합
- 하이브리드는 기본 시나리오
- DR까지 포함하는 ‘운영 가능 AI’

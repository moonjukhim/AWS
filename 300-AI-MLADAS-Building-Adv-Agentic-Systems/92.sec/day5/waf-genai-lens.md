# AWS Well-Architected Framework — Generative AI Lens 질문 정리

- 출처: [AWS Well-Architected Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) (게시일: 2025-11-19)
- 질문 원본: [generative-ai-lens.json](https://github.com/aws-samples/sample-well-architected-custom-lens/blob/main/generative-ai-lens/generative-ai-lens.json) (AWS WA Tool 커스텀 렌즈)
- 적용 범위: Amazon Bedrock의 파운데이션 모델 또는 Amazon SageMaker AI의 고객 관리형 모델을 사용하는 생성형 AI 애플리케이션 (전통적 ML은 [Machine Learning Lens](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html) 참고)

## 요약

| 필러 | 질문 ID | 질문 수 | 모범 사례(BP) 수 |
|---|---|---:|---:|
| 운영 우수성 (Operational Excellence) | GENOPS01–05 | 5 | 10 |
| 보안 (Security) | GENSEC01–06 | 6 | 10 |
| 안정성 (Reliability) | GENREL01–06 | 6 | 10 |
| 성능 효율성 (Performance Efficiency) | GENPERF01–04 | 4 | 8 |
| 비용 최적화 (Cost Optimization) | GENCOST01–05 | 5 | 9 |
| 지속 가능성 (Sustainability) | GENSUS01–03 | 3 | 4 |
| **합계** | | **29** | **51** |


---

## 1. 운영 우수성 (Operational Excellence)

### GENOPS01. 모델 출력 품질의 일관성을 어떻게 달성하고 검증합니까?
*How do you achieve and verify consistent model output quality?*

사용자 피드백, 정답(ground truth) 데이터, 샘플링 기법을 활용한 주기적 평가로 출력 품질을 유지합니다.

- **BP01** 기능적 성능을 주기적으로 평가 — *Periodically evaluate functional performance*
- **BP02** 사용자 피드백 수집 및 모니터링 — *Collect and monitor user feedback*

### GENOPS02. 애플리케이션의 운영 상태를 어떻게 모니터링하고 관리합니까?
*How do you monitor and manage the operational health of your applications?*

핵심 지표 추적, 알림 설정, 이슈 대응 전략. 파운데이션 모델은 기존 시스템과 다르게 소프트웨어·데이터와 상호작용하므로 모든 계층에 걸친 모니터링이 필요합니다.

- **BP01** 모든 애플리케이션 계층 모니터링 — *Monitor all application layers*
- **BP02** 파운데이션 모델 지표 모니터링 — *Monitor foundation model metrics*
- **BP03** 시스템 과부하 위험 완화 솔루션 구현 — *Implement solutions to mitigate the risk of system overload*

### GENOPS03. 모델, 프롬프트, 자산의 추적성을 어떻게 유지합니까?
*How do you maintain traceability for your models, prompts, and assets?*

프롬프트·모델·관련 자산의 버전 관리를 통해 추적성, 재현성, 지속적 개선을 확보합니다. 변형 테스트, 기준선 확보, 지표·정답 데이터 기반 최적화를 포함합니다.

- **BP01** 프롬프트 템플릿 관리 구현 — *Implement prompt template management*
- **BP02** 에이전트 및 RAG 워크플로 트레이싱 활성화 — *Enable tracing for agents and RAG workflows*

### GENOPS04. 생성형 AI 워크로드의 수명 주기 관리를 어떻게 자동화합니까?
*How do you automate the lifecycle management of your generative AI workloads?*

IaC 원칙을 기반으로 도구 선택, CI/CD, 환경 관리, 버전 관리, 거버넌스를 자동화하여 재현 가능하고 확장 가능한 AI 인프라를 구성합니다.

- **BP01** IaC로 생성형 AI 애플리케이션 수명 주기 자동화 — *Automate generative AI application lifecycle with infrastructure as code (IaC)*
- **BP02** GenAIOps를 구현하여 애플리케이션 수명 주기 최적화 — *Implement GenAIOps to optimize the application lifecycle*

### GENOPS05. 생성형 AI 모델 커스터마이징은 언제 수행해야 하는지 어떻게 판단합니까?
*How do you determine when to execute Gen AI model customization?*

작업 특수성, 데이터 가용성, 리소스 제약을 고려합니다. 프롬프트 엔지니어링부터 시작해 RAG, 파인튜닝, 커스텀 모델 구축 순으로 진행하며 성능과 리소스·유지보수 비용의 균형을 맞춥니다.

- **BP01** 모델을 커스터마이징해야 하는 시점 파악 — *Learn when to customize models*

---

## 2. 보안 (Security)

### GENSEC01. 생성형 AI 엔드포인트에 대한 액세스를 어떻게 관리합니까?
*How do you manage access to generative AI endpoints?*

파운데이션 모델은 관리형, 서버리스, 자체 호스팅 엔드포인트로 제공되며 각각 고유한 보안 고려사항이 있습니다.

- **BP01** 파운데이션 모델 엔드포인트에 최소 권한 액세스 부여 — *Grant least privilege access to foundation model endpoints*
- **BP02** 파운데이션 모델과 애플리케이션 간 프라이빗 네트워크 통신 구현 — *Implement private network communication between foundation models and applications*
- **BP03** 데이터 스토어에 접근하는 파운데이션 모델에 최소 권한 구현 — *Implement least privilege access permissions for foundation models accessing data stores*
- **BP04** 생성형 AI 서비스 및 파운데이션 모델에 대한 액세스 모니터링 구현 — *Implement access monitoring to generative AI services and foundation models*

### GENSEC02. 생성형 AI 애플리케이션이 유해하거나 편향되거나 사실과 다른 응답을 생성하지 않도록 어떻게 방지합니까?
*How do you stop generative AI applications from generating harmful, biased, or factually incorrect responses?*

가드레일이 없거나 부적절하면 유해·편향·부정확한 응답이 발생할 수 있으므로 프로덕션 전 위험 완화가 필요합니다.

- **BP01** 유해하거나 부정확한 모델 응답을 완화하는 가드레일 구현 — *Implement guardrails to mitigate harmful or incorrect model responses*

### GENSEC03. 생성형 AI 워크로드와 관련된 이벤트를 어떻게 모니터링하고 감사합니까?
*How do you monitor and audit events associated with your generative AI workloads?*

포괄적인 이벤트 모니터링·감사로 보안 및 성능 문제를 신속하게 식별합니다.

- **BP01** 생성형 AI 서비스 및 파운데이션 모델에 대한 컨트롤 플레인 및 데이터 액세스 모니터링 구현 — *Implement control plane and data access monitoring to generative AI services and foundation models*

### GENSEC04. 시스템 프롬프트와 사용자 프롬프트를 어떻게 보호합니까?
*How do you secure system and user prompts?*

프롬프트는 사용자·애플리케이션이 모델과 상호작용하는 방식을 정의하는 핵심 요소이며, 최적화에 많은 노력이 들어가는 자산입니다.

- **BP01** 안전한 프롬프트 카탈로그 구현 — *Implement a secure prompt catalog*
- **BP02** 파운데이션 모델에 대한 사용자 입력 정제 및 검증 — *Sanitize and validate user inputs to foundation models*

### GENSEC05. 모델의 과도한 권한(Excessive Agency)을 어떻게 방지합니까?
*How do you avoid excessive agency for models?*

과도한 권한은 OWASP LLM Top 10 위협으로, 주로 에이전트 아키텍처에서 발생합니다. 에이전트가 의도된 목적을 넘어서는 행동을 할 위험이 있습니다.

- **BP01** 에이전트 워크플로에 최소 권한 및 권한 경계 구현 — *Implement least privilege access and permissions boundaries for agentic workflows*

### GENSEC06. 데이터 포이즈닝 위험을 어떻게 탐지하고 해결합니까?
*How do you detect and remediate data poisoning risks?*

학습·커스터마이징 시 의도하지 않은 데이터가 사용되어 모델에 바람직하지 않은 영향을 주는 공격으로, 탐지와 복구가 어렵습니다.

- **BP01** 모델 학습 워크플로에 데이터 정제 필터 구현 — *Implement data purification filters for model training workflows*

---

## 3. 안정성 (Reliability)

### GENREL01. 파운데이션 모델의 처리량 할당량(또는 요구량)을 어떻게 결정합니까?
*How do you determine throughput quotas (or needs) for foundation models?*

파운데이션 모델은 동시에 처리할 수 있는 추론 요청량이 제한적이며, 특히 관리형·서버리스 호스팅에서 할당량 관리가 서비스 수준 유지에 중요합니다.

- **BP01** 사용률에 따라 파운데이션 모델 처리량을 확장하고 분산 — *Scale and balance foundation model throughput as a function of utilization*

### GENREL02. 생성형 AI 아키텍처 구성 요소 간 통신의 안정성을 어떻게 유지합니까?
*How do you maintain reliable communication among different components of your generative AI architecture?*

파운데이션 모델, 데이터베이스, 데이터 파이프라인, 프롬프트 카탈로그, 에이전트 API 등 여러 시스템이 네트워크로 통신하므로 안정적이고 안전한 연결이 필요합니다.

- **BP01** 모델 엔드포인트와 지원 인프라 간 이중화된 네트워크 연결 구현 — *Implement redundant network connections among model endpoints and supporting infrastructure*

### GENREL03. 생성형 AI 워크로드의 루프, 재시도, 장애에 대한 복구 조치를 어떻게 구현합니까?
*How do you implement remediation actions for generative AI workload loops, retries, and failures?*

논리적 루프, 재시도, 장애에 적절히 대응하여 안정성과 사용자 경험을 개선합니다.

- **BP01** 로직으로 프롬프트 흐름을 관리하고 장애에서 우아하게 복구 — *Use logic to manage prompt flows and gracefully recover from failure*
- **BP02** 에이전트 워크플로에 타임아웃 메커니즘 구현 — *Implement timeout mechanisms on agentic workflows*

### GENREL04. 프롬프트, 모델 파라미터, 파운데이션 모델의 버전을 어떻게 관리합니까?
*How do you maintain versions for prompts, model parameters, and foundation models?*

프롬프트와 모델 버전, 추론 하이퍼파라미터에 따라 성능이 달라지므로 이를 표준화하고 버전 관리합니다.

- **BP01** 프롬프트 카탈로그 구현 — *Implement a prompt catalog*
- **BP02** 모델 카탈로그 구현 — *Implement a model catalog*

### GENREL05. 추론 워크로드를 여러 가용 영역/리전에 어떻게 분산합니까?
*How do you distribute inference workloads over multiple regions of availability?*

단순 프롬프트-응답부터 멀티 에이전트 오케스트레이션까지, 모든 구성 요소가 서비스 대상 가용 범위에서 동작하도록 설계해야 합니다.

- **BP01** 모든 가용 리전에 걸쳐 추론 요청 로드 밸런싱 — *Load-balance inference requests across all regions of availability*
- **BP02** 모든 가용 리전에 임베딩 데이터 복제 — *Replicate embedding data across all regions of availability*
- **BP03** 모든 가용 리전에서 에이전트 기능 사용 가능 여부 확인 — *Verify that agent capabilities are available across all regions of availability*

### GENREL06. 고성능 분산 컴퓨팅 작업이 성공적으로 완료되도록 어떻게 설계합니까?
*How do you design high-performance distributed computation tasks to maximize successful completion?*

모델 커스터마이징 등 분산 컴퓨팅 작업은 장시간·고비용이며 취약할 수 있으므로 안정성을 고려해 설계해야 합니다.

- **BP01** 고성능 분산 컴퓨팅 작업의 내결함성 설계 — *Design for fault-tolerance for high-performance distributed computation tasks*

---

## 4. 성능 효율성 (Performance Efficiency)

### GENPERF01. 프로덕션 환경에서 생성형 AI 모델의 성능을 어떻게 측정하고 개선합니까?
*How do you capture and improve the performance of your generative AI models in production?*

한 작업(예: 요약)의 성능이 다른 작업(예: 질의응답)의 성능을 보장하지 않습니다. 정답 데이터 기반 벤치마크로 작업별 성능을 평가하며, 지연 시간·처리량 같은 기존 지표도 함께 고려합니다.

- **BP01** 프롬프트와 응답으로 구성된 정답(ground truth) 데이터셋 정의 — *Define a ground truth data set of prompts and responses*
- **BP02** 생성형 AI 워크로드의 성능 지표 수집 — *Collect performance metrics from generative AI workloads*

### GENPERF02. 생성형 AI 워크로드가 허용 가능한 성능 수준을 유지하는지 어떻게 검증합니까?
*How do you verify your generative AI workload maintains acceptable performance levels?*

파운데이션 모델은 비결정적이므로 최소 성능 임계값, 작업별 명확한 요구사항, 성능 저하나 신규 모델 출시 시의 대응 방안이 필요합니다.

- **BP01** 모델 엔드포인트 부하 테스트 — *Load test model endpoints*
- **BP02** 응답 품질 향상을 위한 추론 파라미터 최적화 — *Optimize inference parameters to improve response quality*
- **BP03** 사용 사례에 적합한 모델 선택 및 커스터마이징 — *Select and customize the appropriate model for your use case*

### GENPERF03. 고성능 분산 컴퓨팅 작업에 필요한 컴퓨팅 리소스를 어떻게 최적화합니까?
*How do you optimize computational resources required for high-performance distributed computation tasks?*

학습, 커스터마이징, 대규모 추론 모두 높은 연산 능력이 필요하므로 고성능 컴퓨팅 사용을 최적화합니다.

- **BP01** 모델 호스팅, 커스터마이징, 데이터 액세스에 적절한 경우 관리형 솔루션 사용 — *Use managed solutions for model hosting, customization, and data access where appropriate*

### GENPERF04. 데이터 검색(retrieval) 시스템의 성능을 어떻게 개선합니까?
*How do you improve the performance of data retrieval systems?*

벡터 데이터베이스의 병목은 하위 단계에 연쇄적인 영향을 미치므로, 데이터 특성과 접근 패턴에 대한 이해가 중요합니다.

- **BP01** 벡터 임베딩의 지연 시간 및 관련성 성능 테스트 — *Test vector embeddings for latency and relevant performance*
- **BP02** 사용 사례에 맞게 벡터 크기 최적화 — *Optimize vector sizes for your use case*

---

## 5. 비용 최적화 (Cost Optimization)

### GENCOST01. 비용 최적화를 위해 적절한 모델을 어떻게 선택합니까?
*How do you select the appropriate model to optimize costs?*

모델 제공자, 모델 패밀리·크기, 호스팅 방식에 따라 비용이 크게 다르므로 비용을 모델 선택 기준에 포함합니다.

- **BP01** 추론 비용 최적화를 위한 적정 규모 모델 선택 — *Right-size model selection to optimize inference costs*

### GENCOST02. 비용 효율적인 가격 모델(프로비저닝, 온디맨드, 호스팅, 배치 등)을 어떻게 선택합니까?
*How do you select a cost-effective pricing model (for example, provisioned, on-demand, hosted, or batch)?*

즉시 응답이 필요한 워크로드와 배치로 처리 가능한 워크로드를 구분하고, 호스팅·추론 방식을 비용 관점에서 결정합니다.

- **BP01** 추론 방식 선택 시 비용과 성능의 균형 — *Balance cost and performance when selecting inference paradigms*
- **BP02** 호스팅 비용 최소화를 위한 리소스 소비 최적화 — *Optimize resource consumption to minimize hosting costs*

### GENCOST03. 비용 최적화를 위해 프롬프트를 어떻게 설계합니까?
*How do you engineer prompts to optimize cost?*

프롬프트는 성능뿐 아니라 비용 최적화를 위해서도 설계되어야 합니다.

- **BP01** 프롬프트 토큰 길이 최적화 — *Optimize prompt token length*
- **BP02** 모델 응답 길이 제어 — *Control model response length*
- **BP03** 프롬프트 캐싱으로 토큰 비용 절감 — *Implement prompt caching to reduce token costs*
- **BP04** 비용을 고려한 콘텐츠 필터링을 위해 사용자 입력에 주석(annotation) 추가 — *Annotate user input to enable cost-aware content filtering*

### GENCOST04. 벡터 스토어 비용을 어떻게 최적화합니까?
*How do you optimize vector stores for cost?*

RAG 등에 필요한 벡터 스토어는 전체 운영 비용을 증가시킬 수 있으므로 최적화가 필요합니다.

- **BP01** 임베딩 벡터 길이 축소 — *Reduce vector length on embedded tokens*

### GENCOST05. 에이전트 워크플로 비용을 어떻게 최적화합니까?
*How do you optimize agent workflows for cost?*

에이전트 아키텍처는 자동화 잠재력이 크지만 잘못 구성하면 불필요한 추가 비용이 발생합니다.

- **BP01** 장시간 실행 워크플로를 제어하는 중지 조건 설정 — *Create stopping conditions to control long-running workflows*

---

## 6. 지속 가능성 (Sustainability)

### GENSUS01. 생성형 AI 워크로드의 학습, 커스터마이징, 호스팅에 필요한 컴퓨팅 리소스를 어떻게 최소화합니까?
*How do you minimize the computational resources needed for training, customizing, and hosting generative AI workloads?*

서버리스 아키텍처와 오토스케일링, 관리형 서비스, 인스턴스 최적화, 컨테이너 캐싱, 빠른 모델 로딩, 생성형 AI 전용 인스턴스 활용을 고려합니다.

- **BP01** 오토스케일링 및 서버리스 아키텍처로 리소스 사용률 최적화 — *Implement auto scaling and serverless architectures to optimize resource utilization*
- **BP02** 효율적인 모델 커스터마이징 서비스 사용 — *Use efficient model customization services*

### GENSUS02. 에너지 소비를 최소화하고 효율을 극대화하도록 데이터 처리와 스토리지를 어떻게 최적화합니까?
*How can you optimize data processing and storage to minimize energy consumption and maximize efficiency?*

컬럼형 포맷과 압축으로 전송·처리량을 줄이고, 서버리스 쿼리·ETL 서비스로 상시 인프라 필요성을 줄입니다.

- **BP01** 에너지 소비 최소화를 위한 데이터 처리 및 스토리지 최적화 — *Optimize data processing and storage to minimize energy consumption*

### GENSUS03. 대규모 언어 모델 사용 시 모델 효율성과 리소스 최적화를 어떻게 유지합니까?
*How do you maintain model efficiency and resource optimization when working with large language models?*

양자화, 프루닝, 소형 모델 파인튜닝, 모델 증류(distillation) 등으로 성능과 연산 요구량의 균형을 맞춥니다.

- **BP01** 소형 모델과 최적화된 추론 기법으로 탄소 발자국 감소 — *Leverage smaller models and optimized inference techniques to reduce carbon footprint*

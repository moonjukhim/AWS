##

- SEC 1. 생성형 AI 엔드포인트에 대한 접근 권한을 어떻게 관리하시나요? 
    - 파운데이션 모델 엔드포인트에 대해 최소 권한 원칙을 적용합니다.
    - 파운데이션 모델과 애플리케이션 간의 통신을 위한 프라이빗 네트워크를 구현합니다.
    - 파운데이션 모델이 데이터 저장소에 접근할 때 최소 권한 접근 권한을 적용합니다.
    - 생성형 AI 서비스 및 파운데이션 모델에 대한 접근 모니터링을 구현합니다.
    - 해당 사항 없음

- SEC 2. 생성형 AI 애플리케이션이 유해하거나 편향된, 또는 사실과 다른 응답을 생성하지 않도록 어떻게 방지하시나요? 
    - 모델의 유해하거나 부정확한 응답을 완화하기 위한 가드레일을 구현합니다.
    - 해당 사항 없음

- SEC 3. 생성형 AI 워크로드와 관련된 이벤트를 어떻게 모니터링하고 감사하시나요? 
    - 생성형 AI 서비스 및 파운데이션 모델에 대한 제어 영역(control plane) 및 데이터 접근 모니터링을 구현합니다.
    - 해당 사항 없음

- SEC 4. 시스템 프롬프트와 사용자 프롬프트를 어떻게 보호하시나요? 
    - 안전한 프롬프트 카탈로그를 구현합니다.
    - 파운데이션 모델에 입력되는 사용자 데이터를 정제하고 검증합니다.
    - 해당 사항 없음

- SEC 5. 모델에 과도한 자율 권한(agency)이 부여되는 것을 어떻게 방지하시나요? 
    - 에이전트 기반 워크플로우(agentic workflows)에 대해 최소 권한 원칙 및 권한 경계를 적용합니다.
    - 해당 사항 없음

---

- SEC 1. How do you manage access to generative AI endpoints?
    - Grant least privilege access to foundation model endpoints
    - Implement private network communication between foundation models and applications
    - Implement least privilege access permissions for foundation models accessing data stores
    - Implement access monitoring to generative AI services and foundation models
    - None of these

- SEC 2. How do you prevent generative AI applications from generating harmful, biased, or factually incorrect responses?
    - Implement guardrails to mitigate harmful or incorrect model responses
    - None of these

- SEC 3. How do you monitor and audit events associated with your generative AI workloads?
    - Implement control plane and data access monitoring to generative AI services and foundation models
    - None of these

- SEC 4. How do you secure system and user prompts?
    - Implement a secure prompt catalog
    - Sanitize and validate user inputs to foundation models
    - None of these

- SEC 5. How do you prevent excessive agency for models?
    - Implement least privilege access and permissions boundaries for agentic workflows
    - None of these

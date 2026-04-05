### Threat Composer AI가 분석하는 대상

  소스 코드(codebase) 전체를 분석합니다. 특별한 입력 형식이 필요 없고, 일반적인 프로젝트 디렉토리를 그대로 넘기면 됩니다.

  ```bash  
  uv run threat-composer-ai-cli /path/to/your/project
  ```

  분석 대상 파일

  ┌─────────────┬───────────────────────────────────────────────────┐
  │    유형      │                      확장자                       │
  ├─────────────┼───────────────────────────────────────────────────┤
  │ 소스 코드    │ .ts, .js, .py, .java 등                           │
  ├─────────────┼───────────────────────────────────────────────────┤
  │ 인프라 코드   │ Terraform, CloudFormation (*.yaml, *.yml, *.json) │
  ├─────────────┼───────────────────────────────────────────────────┤
  │ 설정 파일     │ .ini, .cfg, .json, .yaml                          │
  ├─────────────┼───────────────────────────────────────────────────┤
  │ 문서         │ .md                                               │
  └─────────────┴───────────────────────────────────────────────────┘

  - .gitignore를 존중하여 빌드 결과물/의존성은 제외합니다.

  ---

##### 동작 방식: 8개 AI 에이전트가 순차 실행

  1. Application Info    → 앱 이름, 설명, 주요 기능 파악
  2. Architecture        → 코드에서 시스템 아키텍처 추론
  3. Architecture Diagram → SVG 아키텍처 다이어그램 생성
  4. Dataflow            → 데이터 흐름, 신뢰 경계 분석
  5. Dataflow Diagram    → SVG 데이터 흐름 다이어그램 생성
  6. Threats             → STRIDE 방법론으로 15~25개 위협 식별
  7. Mitigations         → 각 위협에 대한 완화 전략 생성
  8. Threat Model        → 최종 위협 모델 JSON 조립

  출력 결과물

  output/
  ├── components/
  │   ├── applicationInfo.tc.json          # 앱 정보
  │   ├── architectureDescription.tc.json  # 아키텍처 설명
  │   ├── architectureDiagram.svg          # 아키텍처 다이어그램
  │   ├── dataflowDescription.tc.json      # 데이터 흐름 설명
  │   ├── dataflowDiagram.svg              # 데이터 흐름 다이어그램
  │   ├── threats.tc.json                  # 위협 목록 (STRIDE)
  │   └── mitigations.tc.json             # 완화 전략
  ├── threatmodel.tc.json                  # 최종 통합 위협 모델
  └── logs/

  최종 threatmodel.tc.json은 Threat Composer 웹앱이나 VS Code 확장에서 바로 열어서 시각적으로 확인/편집할 수 있습니다.

  ---

##### 핵심 요약

  ▎ 소스 코드를 넘기면, AI가 코드를 읽고 아키텍처를 추론한 뒤, STRIDE 기반 위협 분석 + 완화 전략 + 다이어그램까지 자동으로 생성해주는 도구입니다.

  Amazon Bedrock(Claude Sonnet)을 사용하므로 AWS 자격 증명과 Bedrock 접근 권한이 필요합니다.
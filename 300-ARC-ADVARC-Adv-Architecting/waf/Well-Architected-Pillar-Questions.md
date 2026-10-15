# AWS Well-Architected Framework — 원칙(Pillar)별 질문 전체 목록

> 6개 원칙, **총 57개 질문**입니다. 질문 ID와 원문은 AWS 공식 문서의 최신판 기준입니다(2026-10 확인).
> 각 질문에 한국어 번역과 함께, Advanced Architecting on AWS 과정에서 관련된 모듈을 붙였습니다.

| 원칙 | 질문 수 | 영역 |
|---|---|---|
| 운영 우수성 (OPS) | 11 | 조직, 준비, 운영, 발전 |
| 보안 (SEC) | 11 | 기반, ID와 접근, 탐지, 인프라 보호, 데이터 보호, 사고 대응, 애플리케이션 보안 |
| 안정성 (REL) | 13 | 기반, 워크로드 아키텍처, 변경 관리, 장애 관리 |
| 성능 효율성 (PERF) | 5 | 아키텍처 선택, 컴퓨팅, 데이터, 네트워크, 프로세스와 문화 |
| 비용 최적화 (COST) | 11 | 클라우드 재무 관리, 지출 인식, 비용 효율적 리소스, 수요와 공급, 지속적 최적화 |
| 지속 가능성 (SUS) | 6 | 리전, 수요 정렬, 소프트웨어와 아키텍처, 데이터, 하드웨어, 프로세스 |

**과정 모듈 번호:** 01 아키텍팅 개념 검토 · 02 다중 계정 · 03 하이브리드 연결 · 04 특수 인프라 · 05 네트워크 연결 · 06 컨테이너 · 07 CI/CD · 08 고가용성과 DDoS · 09 데이터 보안 · 10 대규모 데이터 저장소 · 11 워크로드 마이그레이션 · 12 비용 최적화 · 13 엣지용 아키텍처

---

## 1. 운영 우수성 (Operational Excellence)

| 영역 | ID | 질문 | 관련 모듈 |
|---|---|---|---|
| **조직** | OPS 1 | 우선순위를 어떻게 결정합니까? | – |
| | OPS 2 | 비즈니스 성과를 지원하도록 조직을 어떻게 구성합니까? | 02 |
| | OPS 3 | 조직 문화가 비즈니스 성과를 어떻게 지원합니까? | – |
| **준비** | OPS 4 | 워크로드에 관측성을 어떻게 구현합니까? | 06, 08 |
| | OPS 5 | 결함을 줄이고, 문제 해결을 쉽게 하고, 프로덕션으로의 흐름을 개선하려면 어떻게 합니까? | **07** |
| | OPS 6 | 배포 위험을 어떻게 완화합니까? | **07** |
| | OPS 7 | 워크로드를 지원할 준비가 되었는지 어떻게 압니까? | 11 |
| **운영** | OPS 8 | 조직에서 워크로드 관측성을 어떻게 활용합니까? | 08 |
| | OPS 9 | 운영 상태를 어떻게 파악합니까? | – |
| | OPS 10 | 워크로드와 운영 이벤트를 어떻게 관리합니까? | 06(이벤트 스트림), 08 |
| **발전** | OPS 11 | 운영을 어떻게 발전시킵니까? | – |


## 2. 보안 (Security)

| 영역 | ID | 질문 | 관련 모듈 |
|---|---|---|---|
| **보안 기반** | SEC 1 | 워크로드를 어떻게 안전하게 운영합니까? | **02**(다중 계정, Control Tower) |
| **ID와 접근 관리** | SEC 2 | 사람과 머신의 인증을 어떻게 관리합니까? | **02**(Identity Center) |
| | SEC 3 | 사람과 머신의 권한을 어떻게 관리합니까? | **02**(SCP), 06(태스크 역할) |
| **탐지** | SEC 4 | 보안 이벤트를 어떻게 탐지하고 조사합니까? | 08(GuardDuty, WAF 로그) |
| **인프라 보호** | SEC 5 | 네트워크 리소스를 어떻게 보호합니까? | 01, 05, **08** |
| | SEC 6 | 컴퓨팅 리소스를 어떻게 보호합니까? | 06 |
| **데이터 보호** | SEC 7 | 데이터를 어떻게 분류합니까? | 10 |
| | SEC 8 | 저장 중인 데이터를 어떻게 보호합니까? | **09**(KMS, CloudHSM) |
| | SEC 9 | 전송 중인 데이터를 어떻게 보호합니까? | 03, **09** |
| **사고 대응** | SEC 10 | 사고를 어떻게 예측하고, 대응하고, 복구합니까? | 08(SRT) |
| **애플리케이션 보안** | SEC 11 | 설계, 개발, 배포 수명 주기 전반에서 애플리케이션 보안 속성을 어떻게 반영하고 검증합니까? | 07 |

## 3. 안정성 (Reliability)

| 영역     | ID    | 질문                                               | 관련 모듈 |
|----------|------|-----------------------------------------------------|---|
| **기반** | REL 1 | 서비스 할당량과 제약을 어떻게 관리합니까? | 06 |
| | REL 2 | 네트워크 토폴로지를 어떻게 계획합니까? | **03, 05** |
| **워크로드 아키텍처** | REL 3 | 워크로드 서비스 아키텍처를 어떻게 설계합니까? | 06 |
| | REL 4 | 장애를 예방하도록 분산 시스템의 상호 작용을 어떻게 설계합니까? | 06 |
| | REL 5 | 장애를 완화하거나 견디도록 분산 시스템의 상호 작용을 어떻게 설계합니까? | 06, 08 |
| **변경 관리** | REL 6 | 워크로드 리소스를 어떻게 모니터링합니까? | 08 |
| | REL 7 | 수요 변화에 적응하도록 워크로드를 어떻게 설계합니까? | 01, 06 |
| | REL 8 | 변경을 어떻게 구현합니까? | **07** |
| **장애 관리** | REL 9 | 데이터를 어떻게 백업합니까? | 10 |
| | REL 10 | 장애 격리로 워크로드를 어떻게 보호합니까? | 01, 02, 06 |
| | REL 11 | 구성 요소 장애를 견디도록 워크로드를 어떻게 설계합니까? | 01, 08, 13 |
| | REL 12 | 안정성을 어떻게 테스트합니까? | – |
| | REL 13 | 재해 복구(DR)를 어떻게 계획합니까? | 13(멀티 리전) |

## 4. 성능 효율성 (Performance Efficiency)

| 영역 | ID | 질문 | 관련 모듈 |
|---|---|---|---|
| **아키텍처 선택** | PERF 1 | 워크로드에 맞는 클라우드 리소스와 아키텍처를 어떻게 선택합니까? | 04, 06 |
| **컴퓨팅과 하드웨어** | PERF 2 | 워크로드에서 컴퓨팅 리소스를 어떻게 선택하고 사용합니까? | **06** |
| **데이터 관리** | PERF 3 | 워크로드에서 데이터를 어떻게 저장, 관리, 접근합니까? | **10** |
| **네트워크와 콘텐츠 전송** | PERF 4 | 워크로드의 네트워크 리소스를 어떻게 선택하고 구성합니까? | 03, 05, **13** |
| **프로세스와 문화** | PERF 5 | 조직의 관행과 문화가 성능 효율성에 어떻게 기여합니까? | – |

## 5. 비용 최적화 (Cost Optimization)

| 영역 | ID | 질문 | 관련 모듈 |
|---|---|---|---|
| **클라우드 재무 관리** | COST 1 | 클라우드 재무 관리를 어떻게 구현합니까? | **12** |
| **지출과 사용량 인식** | COST 2 | 사용량을 어떻게 관리(거버넌스)합니까? | 02(SCP), 12 |
| | COST 3 | 비용과 사용량을 어떻게 모니터링합니까? | **12** |
| | COST 4 | 리소스를 어떻게 폐기합니까? | 12 |
| **비용 효율적 리소스** | COST 5 | 서비스를 선택할 때 비용을 어떻게 평가합니까? | 06, 12 |
| | COST 6 | 리소스 유형, 크기, 수를 고를 때 비용 목표를 어떻게 맞춥니까? | 12 |
| | COST 7 | 가격 모델로 비용을 어떻게 줄입니까? | 06(Spot), **12** |
| | COST 8 | 데이터 전송 요금을 어떻게 계획합니까? | 03, 05, 13 |
| **수요와 공급 관리** | COST 9 | 수요를 어떻게 관리하고 리소스를 어떻게 공급합니까? | 06, 12 |
| **지속적 최적화** | COST 10 | 새 서비스를 어떻게 평가합니까? | 12 |
| | COST 11 | 작업에 드는 노력의 비용을 어떻게 평가합니까? | 11 |

## 6. 지속 가능성 (Sustainability)

| 영역 | ID | 질문 | 관련 모듈 |
|--------------|---|---|---|
| **리전 선택** | SUS 1 | 워크로드의 리전을 어떻게 선택합니까? | 04, 13 |
| **수요 정렬** | SUS 2 | 클라우드 리소스를 수요에 어떻게 맞춥니까? | 06 |
| **소프트웨어와 아키텍처** | SUS 3 | 지속 가능성 목표를 위해 소프트웨어와 아키텍처 패턴을 어떻게 활용합니까? | 06, 13 |
| **데이터** | SUS 4 | 지속 가능성 목표를 위해 데이터 관리 정책과 패턴을 어떻게 활용합니까? | 10, 12 |
| **하드웨어와 서비스** | SUS 5 | 지속 가능성 목표를 위해 클라우드 하드웨어와 서비스를 어떻게 선택하고 사용합니까? | 06(Graviton, Fargate) |
| **프로세스와 문화** | SUS 6 | 조직의 프로세스가 지속 가능성 목표를 어떻게 지원합니까? | 07 |


---

## 참고 자료

- 운영 우수성: [Organization](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-organization.html) · [Prepare](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-prepare.html) · [Operate](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-operate.html) · [Evolve](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-evolve.html)
- 보안: [Security foundations](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-sec-security.html) · [IAM](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-identity-and-access-management.html) · [Detection](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-detective-controls.html) · [Infrastructure protection](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-infrastructure-protection.html) · [Data protection](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-data-protection.html) · [Incident response](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-incident-response.html) · [Application security](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-appsec.html)
- 안정성: [Foundations](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-foundations.html) · [Workload architecture](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-workload-architecture.html) · [Change management](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-change-management.html) · [Failure management](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-failure-management.html)
- 성능 효율성: [Selection](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-selection.html) · [Compute](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-compute-hardware.html) · [Data](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-data-management.html) · [Networking](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-networking-delivery.html) · [Process](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-process-culture.html)
- 비용 최적화: [CFM](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-practice-cloud-financial-management.html) · [Awareness](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-expenditure-and-usage-awareness.html) · [Resources](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-cost-effective-resources.html) · [Demand/supply](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-manage-demand-and-supply-resources.html) · [Optimize over time](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-optimize-over-time.html)
- 지속 가능성: [Region](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-region-selection.html) · [Demand](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-alignment-to-demand.html) · [Software](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-sus-software-architecture.html) · [Data](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-sus-data.html) · [Hardware](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-sus-hardware-and-services.html) · [Process](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-sus-process-and-culture.html)

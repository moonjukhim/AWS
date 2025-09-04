## 📊 사용된 기술 정리 표

| 다이어그램 | 주요 목적 | 사용된 AWS 서비스 / 기술 |
|------------|-----------|--------------------------|
| **Systems Manager +<br> Config +<br> 인벤토리** | - EC2 인스턴스(Web/AppServer) 관리 <br>- 규정 준수 확인 <br>- 인벤토리 탐색 | - **AWS Systems Manager** (Session Manager, 인벤토리)<br>- **AWS Config** (규정 준수 검사)<br>- **Amazon EC2** (WebServer, AppServer)<br>- **IAM 사용자** (액세스 관리)<br>- **VPC / 서브넷** (네트워크) |
| **CloudFormation +<br> 드리프트 탐지** | - 인프라를 템플릿 기반으로 생성/업데이트 <br>- 드리프트 탐지 | - **AWS CloudFormation** (스택, 템플릿)<br>- **Amazon EC2** (WebServer, AppServer)<br>- **리소스 그룹 / 태그** (그룹화 및 관리)<br>- **드리프트 탐지** (Config와 유사한 상태 검증)<br>- **VPC / 서브넷** (네트워크) |
| **Systems Manager +<br> CloudWatch 로그** | 다수의 WebServer/AppServer 그룹 관리 및<br> 실행 로그 수집 | - **AWS Systems Manager** (인스턴스 관리)<br>- **Amazon CloudWatch** (로그 수집)<br>- **Amazon EC2** (WebServer1~3, AppServer1~2)<br>- **VPC / 서브넷** (네트워크) |
| **모니터링 & 경보 자동화** | 인스턴스 상태 변경 시 경보 발송 및 테스트 | - **Amazon CloudWatch** (모니터링, 대시보드, 경보)<br>- **AWS Systems Manager** (Session Manager, 관리)<br>- **Amazon SNS** (SysOpsTeamPager 주제)<br>- **AWS Lambda** (canary 테스트 함수)<br>- **EC2 (AppServer)** |
| **백업 & 복원 자동화** | EBS 백업/복원 및 알림 | - **AWS Backup** (백업 계획/실행)<br>- **Amazon SNS** (BackupNotificationTopic)<br>- **Amazon CloudWatch Logs** (백업 로그 검토)<br>- **AWS Lambda** (Test 복원 함수)<br>- **Amazon EBS** (MyEBSVolume)<br>- **Amazon S3** (저장소 역할로 간접 포함 가능) |
| **규정 준수 & 자동 문제 해결** | 보안 그룹, S3 암호화 등 <br>규정 위반 탐지 및 자동 수정 | - **Amazon SNS** (알림)<br>- **Amazon EventBridge** (규칙/이벤트 트리거)<br>- **AWS Config** (규정 준수 탐지)<br>- **AWS Systems Manager (SSM)** 문서 (자동 수정)<br>- **Amazon S3** (버킷 및 암호화)<br>- **EC2 (WebServer)** |

---

## ✅ 공통 서비스 정리

| 공통 서비스 | 역할 / 쓰임새 |
|-------------------------------|---------------|
| **Amazon EC2** | 항상 관리 대상(WebServer, AppServer). 대부분 T2 인스턴스 예시로 등장 |
| **AWS Systems Manager (SSM)** | Session Manager, 문서 실행, 인벤토리 수집, 자동화 실행 등 운영 관리 허브 역할 |
| **Amazon SNS** | 알림/통지(이벤트, 백업 완료, 경보 전달 등) |
| **Amazon CloudWatch** | 지표 수집, 로그 저장, 경보 생성, 대시보드 제공 |
| **AWS Config** | 규정 준수 확인, 리소스 상태 탐지, 드리프트와 유사한 검증 기능 |
| **AWS Lambda** | 자동화된 처리(예: 경보 테스트, 복원 테스트, Canary 함수) |
| **Amazon S3** | 스냅샷 저장, 백업 저장소, 버킷 암호화 규칙 적용 등 데이터 저장소 |
| **AWS CloudFormation** | 스택과 템플릿을 기반으로 리소스를 정의/배포, 드리프트 탐지 |


---

## ✅ 핵심 공통 패턴

- 운영 대상은 EC2 인스턴스(Web/AppServer)
- 운영 자동화 도구는 Systems Manager
- 상태/규정 검증은 Config & CloudFormation
- 모니터링/로그는 CloudWatch
- 알림 체계는 SNS
- 자동화 함수 실행은 Lambda
- 저장/백업은 S3


### 비용관리


##### Cost Explorer vs CUR 비교

| 구분         | **Cost Explorer**                          | **Cost & Usage Report (CUR)**                            |
| ---------- | ------------------------------------------ | -------------------------------------------------------- |
| **목표**     | 비용/사용량을 직관적으로 분석하고 시각화                     | 가장 상세한 청구·사용량 데이터를 원시 형태로 제공                             |
| **데이터 수준** | 집계된 수준 (일/월 단위, 서비스·계정·태그별 필터링)            | 매우 상세 (시간별, 리소스별, API 호출 단위까지 포함)                        |
| **제공 형식**  | AWS 콘솔 UI 기반 그래프/리포트                       | CSV/Parquet 파일로 Amazon S3에 저장                            |
| **분석 방법**  | 콘솔에서 클릭·필터링으로 바로 분석                        | Athena, Redshift, QuickSight 등 외부 툴과 통합해 쿼리/분석           |
| **사용 편의성** | 손쉬운 시각화, 비전문가도 사용 가능                       | SQL/ETL 등 기술 필요 (데이터 레이크/BI 통합 시 적합)                     |
| **주요 활용**  | - 비용 추세 확인<br>- 예산 초과 위험 감시<br>- 태그별 비용 집계 | - 상세 비용 회계 처리<br>- 부서/서비스 단위 정밀 청구<br>- 맞춤형 리포트 생성 및 자동화 |
| **비용**     | 무료 (데이터는 기본 제공)                            | CUR 자체는 무료, 단 S3 저장·Athena 쿼리 등 추가 비용 발생                 |


##### Trusted Advisor vs Compute Optimizer

| 구분          | **AWS Trusted Advisor**                             | **AWS Compute Optimizer**                       |
| ------------ | --------------------------------------------------- | ----------------------------------------------- |
| **목표**      | AWS 계정 전체의 베스트 프랙티스 점검                              | 개별 리소스의 사이징 및 성능/비용 최적화 권장                      |
| **분석 범위**  | 계정 전체 (보안, 비용, 성능, 서비스 한도, 내결함성 등)                  | 특정 리소스 (EC2, Auto Scaling Group, EBS, Lambda 등) |
| **분석 방식**  | 사전 정의된 체크리스트 기반                                     | 머신러닝 기반 사용 패턴 분석                                |
| **출력 형태**  | 권장 사항 목록 (예: 미사용 리소스, 퍼블릭 접근 위험 등)             | 리소스별 구체적 리사이징 권장안 (예: `m5.large → t3.medium`)   |
| **활용 목적**  | - 비용 절감<br>- 보안 강화<br>- 서비스 한도 확인<br>- 장애 대비        | - 인스턴스/스토리지/함수의 과/저활용 탐지<br>- 최적의 리소스 타입 추천     |
| **지원 범위**  | 모든 AWS 계정 리소스에 대한 종합 점검                             | EC2, Auto Scaling Group, EBS, Lambda 등 특정 리소스   |
| **제약 사항**  | 전체 체크 중 일부만 무료 (전체는 Business/Enterprise Support 필요) | 무료 제공, 단 리소스 모니터링 데이터가 일정 기간 축적되어야 정확도 향상       |
| **비교 포인트** | “넓고 얕게” → 계정 차원의 종합 점검                              | “좁고 깊게” → 리소스 단위의 세밀한 최적화                       |


## 📊 사용된 기술 정리 표

| 다이어그램 | 주요 목적 | 사용된 AWS 서비스 / 기술 |
|------------|-----------|--------------------------|
| **Systems Manager + Config + 인벤토리** | - EC2 인스턴스(Web/AppServer) 관리 <br>- 규정 준수 확인 <br>- 인벤토리 탐색 | - **AWS Systems Manager** (Session Manager, 인벤토리)<br>- **AWS Config** (규정 준수 검사)<br>- **Amazon EC2** (WebServer, AppServer)<br>- **IAM 사용자** (액세스 관리)<br>- **VPC / 서브넷** (네트워크) |
| **CloudFormation + 드리프트 탐지** | - 인프라를 템플릿 기반으로 생성/업데이트 <br>- 드리프트 탐지 | - **AWS CloudFormation** (스택, 템플릿)<br>- **Amazon EC2** (WebServer, AppServer)<br>- **리소스 그룹 / 태그** (그룹화 및 관리)<br>- **드리프트 탐지** (Config와 유사한 상태 검증)<br>- **VPC / 서브넷** (네트워크) |
| **Systems Manager + CloudWatch 로그** | 다수의 WebServer/AppServer 그룹 관리 및 실행 로그 수집 | - **AWS Systems Manager** (인스턴스 관리)<br>- **Amazon CloudWatch** (로그 수집)<br>- **Amazon EC2** (WebServer1~3, AppServer1~2)<br>- **VPC / 서브넷** (네트워크) |
| **① 규정 준수 & 자동 문제 해결** | 보안 그룹, S3 암호화 등 규정 위반 탐지 및 자동 수정 | - **Amazon SNS** (알림)<br>- **Amazon EventBridge** (규칙/이벤트 트리거)<br>- **AWS Config** (규정 준수 탐지)<br>- **AWS Systems Manager (SSM)** 문서 (자동 수정)<br>- **Amazon S3** (버킷 및 암호화)<br>- **EC2 (WebServer)** |
| **② 모니터링 & 경보 자동화** | 인스턴스 상태 변경 시 경보 발송 및 테스트 | - **Amazon CloudWatch** (모니터링, 대시보드, 경보)<br>- **AWS Systems Manager** (Session Manager, 관리)<br>- **Amazon SNS** (SysOpsTeamPager 주제)<br>- **AWS Lambda** (canary 테스트 함수)<br>- **EC2 (AppServer)** |
| **③ 백업 & 복원 자동화** | EBS 백업/복원 및 알림 | - **AWS Backup** (백업 계획/실행)<br>- **Amazon SNS** (BackupNotificationTopic)<br>- **Amazon CloudWatch Logs** (백업 로그 검토)<br>- **AWS Lambda** (Test 복원 함수)<br>- **Amazon EBS** (MyEBSVolume)<br>- **Amazon S3** (저장소 역할로 간접 포함 가능) |

---

## ✅ 공통적으로 쓰인 서비스
- **Amazon SNS (알림/통지)**  
- **자동화 트리거 (EventBridge / CloudWatch Events)**  
- **AWS Lambda (자동 처리, 테스트 함수)**  
- **AWS Systems Manager (SSM, Session Manager)**  

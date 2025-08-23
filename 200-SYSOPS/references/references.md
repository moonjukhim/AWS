| 항목                  | SSM Agent (System Manager Agent)                        | CloudWatch Agent                                        |
| --------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| 주요 목적             | 원격 명령 실행, 패치 관리, 자동화, 세션 관리 등         | 메트릭 및 로그 수집, 모니터링                           |
| 설치 대상             | EC2, 온프레미스 서버                                    | EC2, 온프레미스 서버, 컨테이너                          |
| 기본 기능             | Run Command, Patch Manager, Session Manager 등          | 시스템 메트릭 수집 (CPU, 메모리 등), 로그 수집          |
| 데이터 전송 대상      | AWS Systems Manager                                     | Amazon CloudWatch                                       |
| 로그 수집 가능 여부   | 제한적 (Automation 로그 등 내부 로그)                   | 가능 (애플리케이션 로그, 시스템 로그 등)                |
| 메트릭 수집 가능 여부 | 아니오                                                  | 예                                                      |
| AWS IAM 권한 요구     | `AmazonSSMManagedInstanceCore`                          | `CloudWatchAgentServerPolicy` 등                        |
| 설치 방법             | 대부분의 최신 AMI에 기본 설치되어 있음                  | 수동 설치 또는 SSM을 통한 자동 설치 가능                |
| 구성 방법             | Systems Manager 콘솔, CLI, SDK                          | CloudWatch Agent config 파일(json), SSM Parameter Store |
| 네트워크 요구사항     | SSM endpoint에 대한 액세스 (인터넷 또는 VPC 엔드포인트) | CloudWatch endpoint에 대한 액세스 필요                  |
| 운영 체제 지원        | Windows, Linux                                          | Windows, Linux                                          |
| 사용 요금             | 에이전트 사용 자체는 무료 (기능에 따라 과금 가능)       | 에이전트는 무료, 수집된 메트릭/로그는 과금 대상         |

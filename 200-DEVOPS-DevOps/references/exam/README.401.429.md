### DevOps 

401. 

402. 

|                  | A                               | **D**                    |
| ---------------- | ------------------------------- | ------------------------ |
| 방식               | Control Tower Proactive Control | **SCP**                  |
| 구현               | CloudFormation Hook             | **IAM/Organizations 정책** |
| Terraform 직접 적용  | ❌ 핵심 약점                         | **✅**                    |
| 생성 전 차단          | CFN 경로에서 가능                     | **✅ API 자체 차단**          |
| VPC 없는 Lambda 차단 | 가능하지만 배포 경로 제약                  | **✅**                    |
| 정답               | ❌                               | **✅**                    |

- AWS Control Tower의 Proactive 제어(옵션)는 내부적으로 AWS CloudFormation Hooks(preCreate, preUpdate 핸들러) 기술을 사용합니다.

403. Tags vs TagManager

- 재사용 가능한 인프라 → Construct Library
- 전체 리소스에 공통 태그 → Tags class
- Microservice 독립 관리 → Separate CDK Stacks

Tags = 내가 construct tree에 태그를 붙일 때
TagManager = construct/resource 구현 내부에서 태그를 관리할 때

---

404. S3 Multi-Region Access Point + Failover controls

405. AWS Device Farm

406. CloudWatch Logs → S3는 Subscription Filter + Firehose

```text
Application
    │
    ▼
CloudWatch Logs
    │
    │ 30일 보관
    │ 검색 가능
    │
    └─ Subscription Filter
             │
             ▼
       Amazon Data Firehose
             │
             ▼
            S3
             │
             ├─ ~90일
             │   S3 Standard
             │
             ├─ 90일 이후
             │   S3 Standard-IA
             │
             └─ 180일 이후
                 S3 Glacier Deep Archive
```
408. AWS X-Ray

409. Git + Pull Request + CloudFormation Git sync

410. PR 테스트 -> Main 배포
---
411. CodePipeline 실행 모드: V1/V2, Git tag trigger, EventBridge + ECR
---
412. EKS에서 Control Plane 관측 + Node/Container 관측

```text
             Amazon EKS
                 │
       ┌─────────┴─────────┐
       │                   │
 Control Plane          Worker Nodes
       │                   │
       │                   ├─ Pod / Container
       │                   ├─ CPU / Memory
       │                   └─ Node metrics/logs
       ▼                   ▼
EKS Control Plane     Container Insights
    Logging                 │
       │                    │
       └────────┬───────────┘
                ▼
          Amazon CloudWatch
                │
                ▼
       CloudWatch Logs Insights
```
413. PrincipalTag ↔ ResourceTag를 비교하는 ABAC

414. CloudWatch System Status Check → Recover

```text
EC2 Status Checks
│
├─ System Status Check
│    → AWS 인프라/호스트 문제
│
└─ Instance Status Check
     → 인스턴스 내부 문제
```

415. System Manager Patch Manager & AWS Config

416. CloudWatch Synthetics + Alarm + ECS Rollback

```text
새 ECS 버전 배포
      │
      ▼
새 버전에 테스트 endpoint 제공
      │
      ▼
CloudWatch Synthetics Canary
      │
      ├─ 로그인 테스트
      ├─ 주문 흐름 테스트
      ├─ 주요 API 호출
      └─ 응답 검증
             │
       ┌─────┴─────┐
       │           │
     성공         실패
       │           │
       ▼           ▼
 Traffic 전환   CloudWatch Alarm
                   │
                   ▼
               ECS Rollback
```

417. Centralized log storage

```text
여러 계정의 로그를 한 곳에서 "본다" → CloudWatch cross-account observability
여러 계정의 로그를 실제 중앙 저장소로 "보낸다" + CMK → Subscription → Firehose → 중앙 S3
```

418. Systems Manager Parameter Store의 cross-account parameter sharing

Advanced parameter + AWS RAM + Customer managed KMS key 조합
---
419. L3 Construct + 공통 Stack + 환경 Parameter

```text
Reusable L3 Constructs
│
├─ NetworkingConstruct
│    ├─ VPC
│    ├─ Subnet
│    └─ Security Group
│
├─ DatabaseConstruct
│    ├─ RDS/DynamoDB
│    └─ Security/Backup
│
└─ ServerlessConstruct
     ├─ Lambda
     ├─ API Gateway
     └─ IAM
           │
           ▼
    공통 Deployment Stack
           │
       environment
       parameter
      /     |      \
     /      |       \
   dev   staging   prod
```

421. CloudFront + Origin Shield + Origin Failover

```text
                    Global Users
                         │
                         ▼
               CloudFront Edge Locations
                         │
                         ▼
                 Regional Edge Cache
                         │
                         ▼
                    Origin Shield
                    (us-east-1)
                         │
                  Origin Group
                   /           \
                  ▼             ▼
          Primary Origin    Secondary Origin
          S3 us-east-1      S3 other Region
                  │             ▲
                  │             │
                  └── S3 CRR ───┘
```

422. CodeDeploy Agent Log
423. GuardDuty
424. ALB Weighted Target Groups
425. ECR lifecycle policy
426. CloudWatch agent
427. CDK
428. Auto Mode
429. 
### Control Tower 주요 주제

1. Control(GuardRail)
2. Landingzone
3. Account Provisioning + Baseline
4. New account automatic registration
5. IaC for Guardrail

---

EKS

Pod Identity access

303. AWS Control Tower Account Factory가 AWS Service Catalog를 기반으로 계정을 프로비저닝/등록

```text
Step Functions
     │
     ├─ ① AWS Organizations
     │      ↓
     │   새 Account 생성
     │
     ├─ ② AWSControlTowerExecution Role 생성  ← C
     │
     └─ ③ Service Catalog
             ↓
        ProvisionProduct API              ← D
             ↓
       Control Tower Account Factory
             ↓
       Control Tower 관리 계정
```

---
329. 조직 전체에 적용할 통제와 각 계정에 배포할 사용자 권한

```text
Organizations 전체의 Region/Service 사용 범위 제한 → SCP
여러 AWS 계정에 동일한 IAM Role/리소스 배포 → CloudFormation StackSets
```

334. 

```text
                Control Tower Management Account
                           │
              ┌────────────┴─────────────┐
              │                          │
       기존 OU 재등록 이벤트       신규 Account/Update 이벤트
              │                          │
              └──────── EventBridge ─────┘
                           │
                           ▼
                         Lambda
                           │
                     Lambda IAM Role       ← E
                           │
                    sts:AssumeRole
                           ▼
              AWSControlTowerExecution     ← E
                    (Member Account)
                           │
                           ▼
                AWS Config Recorder
                    Customization
```
---

348. Control Tower Guardrail/Control을 IaC로 관리

  - Guardrail을 OU 전체에 적용 → AWS::ControlTower::EnableControl의 대상은 OU
  - 변경 이력/버전 관리 → CodeCommit
  - 검토 및 롤백 → CloudFormation + Git 기반 관리
  - Security Team이 자기 OU/계정에서 관리 → Security Team 계정의 CodePipeline
  - 승인된 Guardrail만 허용 → 승인된 CloudFormation 템플릿을 Repository에서 관리
  - 운영 효율성 → CodeCommit 변경 → EventBridge → CodePipeline 자동 실행

```text
Security Team
     │
     ▼
CodeCommit
(승인된 Guardrail CFN Templates)
     │
     │ commit
     ▼
EventBridge
     │
     ▼
CodePipeline
     │
     ▼
CloudFormation
     │
     │ AWS::ControlTower::EnableControl
     ▼
Target OU
 ├─ Account A
 ├─ Account B
 └─ Account C
```

---
355. CloudWatch Logs Data Protection

```text
CloudWatch Logs Data Protection은 CloudWatch Logs에 들어오는 로그에서 
민감정보(PII, 금융정보, 자격증명 등)를 탐지하고 마스킹(masking)하는 기능
```

356. Organizations의 모든 계정에 강제

```text
Config Rule + Remediation은 => 잘못된 상태 발생 → 탐지 → 수정
SCP = > 잘못된 요청 → 애초에 거부
```

357. Performance Insights와 DevOps Guru

```text
Transaction 시작
    │
    ├── INSERT / DELETE
    │
    └── Transaction 종료 안 함
             ↓
      idle in transaction
             ↓
      ┌──────┴─────────┐
      ↓                ↓
 다른 Query Blocking   VACUUM 방해
      ↓                ↓
      └──────┬─────────┘
             ↓
        DB 성능 저하
```

359. Health check & Notification(config change)
---
360. CodePipeline → CodeBuild → GitHub 사이에서 누가 CodeStar Connection을 사용하는지

```text
┌──────────────────────────────────────────────────────────┐
│                    AWS CodePipeline                      │
│                                                          │
│  ① Source Stage                                          │
│  ┌─────────────────┐                                     │
│  │     GitHub      │◀──── CodeStar Connection            │
│  │   Repository    │                                     │
│  └────────┬────────┘                                     │
│           │                                              │
│           │ Source 가져오기                               │
│           ▼                                              │
│     Source Artifact                                      │
│           │                                              │
│           ▼                                              │
│  ② Build Stage                                           │
│  ┌──────────────────────────────┐                        │
│  │        AWS CodeBuild         │                        │
│  │                              │                        │
│  │ buildspec.yml                │                        │
│  │                              │                        │
│  │ $ git clone GitHub repo      │ ───────────────┐       │
│  └──────────────────────────────┘                │       │
│                                                  │       │
│                                   GitHub 접근 필요│       │
│                                                  ▼       │
│                                      CodeStar Connection │
│                                                  │       │
│                                                  ▼       │
│                                           GitHub Repo    │
│                                                          │
│           ▼                                              │
│  ③ Deploy Stage                                         │
│  ┌─────────────────┐                                    │
│  │     Deploy      │                                    │
│  └─────────────────┘                                    │
└──────────────────────────────────────────────────────────┘
```

---

361. 패키지 공급망(Package Supply Chain) 관리

```text
                  Public NPM
                      │
                      │ package 가져오기
                      ▼
             ┌─────────────────┐
             │ AWS CodeArtifact│
             │  npm-store      │
             └────────┬────────┘
                      │
                새 버전 검증 CodePipeline
                      │
                      ▼
              ┌───────┴────────┐
              │                │
            성공              실패
              │                │
              ▼                ▼
           사용 가능       Unlisted
              │
              ▼
           CodeBuild
              │
          npm install
              │
              ▼
        Application Build
```

---

362. DR 구조

```text
              ┌──────── CloudFront ────────┐
              │                            │
              ▼                            ▼
        Primary Origin               DR Origin
         Primary ALB                   DR ALB
              │                            │
              ▼                            ▼
       Auto Scaling                  Auto Scaling
       desired = 3                   desired = 0 ⭐
              │                            │
           EC2 × 3                  장애 시 EC2 생성
              │
              ▼
     Primary OpenSearch
              │
              │ Cross-Cluster
              │ Replication
              ▼
        DR OpenSearch
        (계속 데이터 복제)
```

---

363. 지속적 규정 준수 검사 + 자동 Remediation

```text
모든 ALB
   │
   └── WAF가 연결되어 있어야 함
             │
             ▼
       누군가 WAF 제거
             │
             ▼
       자동으로 탐지
             │
             ▼
       WAF 다시 연결
```

---

364. CI/CD에서 스크립트 기반 테스트 실행 → CodeBuild
---
365. 
---

### 366. CodeBuild Webhook + Build Status Reporting + Artifacts

```text
Developer
    │
    │ Pull Request 생성/업데이트
    ▼
Git Repository
    │
    │ Webhook
    ▼
┌─────────────────────────┐
│      AWS CodeBuild      │
│                         │
│  Unit Test 실행          │
│                         │
│  buildspec.yml          │
│       │                 │
│       └─ artifacts      │
└───────┬──────────┬──────┘
        │          │
        │          │ output files
        │          ▼
        │      Amazon S3
        │
        │ Build Status Reporting
        ▼
Git Pull Request
```

---

367. CodeBuild

```text
① CodeBuild Project
   → Artifact destination = S3

② buildspec.yml
   → 어떤 파일을 artifact로 내보낼지 지정

③ CodeBuild Service Role
   → S3에 업로드할 권한
```

---
 
368. CloudFormation Git Sync

```text
                    지정된 Git Provider
                           │
                    Git Repository
                           │
             ┌─────────────┴─────────────┐
             │                           │
         Region A                    Region B
             │                           │
      CodeConnections              CodeConnections
       Connection                   Connection
             │                           │
             ▼                           ▼
       Repository Link              Repository Link
             │                           │
             ▼                           ▼
      CloudFormation               CloudFormation
          Git Sync                     Git Sync
             │                           │
             ▼                           ▼
       CFN Stack A                  CFN Stack B
```

---

369. Nested Stack Fail

```text
Root Stack
│
├── 기존 Resource
│
└── Nested Stack
       │
       ├── EC2 #1
       ├── EC2 #2
       └── EC2 #3
              │
              ❌ CREATE_FAILED
                    ↓
            Nested Stack 실패
                    ↓
              Root Stack 실패
```

---

370. Active-Passive(Warm Standby)

```text
              Route 53
                  │
           Simple Routing
                  │
                  ▼
             Primary EC2
                  │
                  ▼
                 EFS

             Standby EC2
             (대기 중)
```

---
371. 
---
 
372. CodePipeline → Cross-Account CodeDeploy 배포

```text
┌──────────────── PipelineAccount ────────────────┐
│                                                 │
│  CodePipeline                                  │
│      │                                          │
│      └─ CodePipeline_Service_Role               │
│                                                 │
│  S3 Artifact Bucket                             │
│      └─ artifact.zip 🔐 KMS                     │
│                                                 │
│  Customer Managed KMS Key                       │
│                                                 │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Cross-Account Deploy
                    │
                    ▼
┌──────────────── CodeDeployAccount ──────────────┐
│                                                 │
│              DevOps_Role                        │
│                   │                             │
│                   ▼                             │
│              CodeDeploy                         │
│                   │                             │
│                   ▼                             │
│                EC2                              │
│                                                 │
└─────────────────────────────────────────────────┘
```
---
373. Event-driven 자동화

```text
Developer
    │
    │ EC2 생성 API
    │ RunInstances
    ▼
Amazon EC2
    │
    │ API Event
    ▼
CloudTrail
    │
    │ userIdentity
    │ eventName
    │ resource 정보
    ▼
EventBridge
    │
    │ Rule Match
    ▼
Lambda
    │
    ├─ User ID 추출
    ├─ Cost Center 조회
    │
    └─ CreateTags
          │
          ▼
       EC2 Resource

       CreatedBy = user123
       CostCenter = CC-100
```

---

374. CodeBuild + CodeArtifact + Upstream Repository
---
375. 
---
376. Pull Through Cache

```text
                        Upstream Registry
                     Docker Hub / ECR Public
                              │
                              │ 최초 pull
                              ▼
CI/CD ──────────────→ ECR Pull Through Cache
                              │
                              │ Cached Image
                              ▼
                         ECR Private
                          Registry
                              │
                         Image Scanning
                              │
                              ▼
                       취약점 검사
```

---
377. 
---
378.
---
379. CodePipeline + CodeBuild 테스트 게이트

```text
Git Repository
      │
      ▼
┌──────────────┐
│ Source Stage │
└──────┬───────┘
       │ Source Artifact
       ▼
┌──────────────────────────────┐
│ Test Stage                   │
│                              │
│       CodeBuild              │
│          │                   │
│          ├─ Unit Test        │
│          │                   │
│          ├─ Coverage 생성     │
│          │                   │
│          └─ Coverage >= 80%? │
│                │             │
│          ┌─────┴─────┐       │
│          │           │       │
│        YES          NO       │
│          │           │       │
│          ▼           ▼       │
│       Success      Failure ❌ │
└──────────┬───────────────────┘
           │
           │ 80% 이상만 진행
           ▼
┌─────────────────┐
│ Production      │
│ Deploy Stage    │
└─────────────────┘
```

--- 
380. 
---
381. 파이프라인 개선

```text
                  CodePipeline

Source
  │
  ▼
Build
  │
  ├── Unit Test
  │
  ├── Code Coverage
  │
  └── Security Scan ← CodeGuru ⭐
           │
           │ PASS
           ▼
Deploy
  │
  ▼
Production
  │
  └── Smoke Test ⭐
           │
       ┌───┴────┐
      PASS     FAIL
       │         │
       ▼         ▼
      완료     Rollback
```

---

382. Organization 관리

```text
AWS Organizations
       ↓
Trusted Access
       ↓
CloudFormation StackSets
       ↓
Service-managed permissions
       ↓
OU 지정
       ↓
Automatic deployment
       │
       ├─ 기존 Account ✅
       └─ 신규 Account ✅
```

---
383. 
384. 
385. 
386. EC2 Image Builder
387. 
388. 
---
389. CDK + CloudFormation StackSets

- CDK Construct

```text
Security Controls Construct
(CDK)
 │
 │ IAM / Config / Security 정책 등
 ▼
CDK App
 │
 ▼
CloudFormation StackSets
 │
 ├───────────────┬───────────────┐
 ▼               ▼               ▼
Account A       Account B       Account C
 │               │               │
 ├ us-east-1     ├ us-east-1     ├ us-east-1
 ├ ap-northeast-2├ ap-northeast-2├ ap-northeast-2
 └ eu-west-1     └ eu-west-1     └ eu-west-1
 ```

- 보안 정책을 변경

```text
Security Construct 변경
        ↓
CDK Deploy
        ↓
StackSet Update
        ↓
모든 Stack Instance 업데이트
        ↓
모든 Account × Region에 반영
```

---

390. 패키지 승격(Promotion) 패턴

```text
       최신 버전
          │
          ▼
┌──────────────────┐
│ DEV CodeArtifact │ ← Developer만 접근
└────────┬─────────┘
         │
         ▼
    독립적인 Test
         │
     ┌───┴───┐
   FAIL      PASS
     │         │
     ❌        ▼
          Promotion
              │
              ▼
┌───────────────────┐
│ PROD CodeArtifact │ ← 검증된 버전만
└─────────┬─────────┘
          ▼
      Applications
```

---

391. IAM Identity Center Permission Set + SCP + AssumeRole

392. AWS ECR의 Cross-Region Replication
---
393. CodeDeploy Agent 로그 + 애플리케이션 로그

```text
CodeDeploy
    │
    ▼
EC2 CodeDeploy Agent
    │
    ├── ApplicationStop
    ├── BeforeInstall
    ├── AfterInstall
    ├── ApplicationStart
    └── ValidateService
              │
              ▼
        배포 성공 / 실패
```

---

394. DevOps Guru

```text
AWS Infrastructure
 ├─ EC2
 ├─ RDS
 ├─ DynamoDB
 ├─ Lambda
 └─ 기타 지원 리소스
       │
       ▼
 Amazon DevOps Guru
       │
       ├─ Anomaly Detection
       ├─ Insights
       ├─ 관련 Metrics / Events
       └─ Recommendations
                │
                ▼
        DevOps Guru Dashboard
```

395. CodeArtifact
396. 
397. 
398. 
399. 
400. ECR Replication + ECS/NLB + Latency Routing

```text
                       Route 53
                  Latency-based Routing
                    /              \
                   /                \
        ap-southeast-2            eu-west-2
              │                       │
             NLB                     NLB
              │                       │
        ECS Fargate             ECS Fargate
              │                       │
             ECR  ──Replication──→   ECR
```


---

---
1. Q303 패턴 분해

┌────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│    항목    │                                                  내용                                                  │
├────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 상황       │ Control Tower 구성 완료 + 기존 계정 등록 완료 → 신규 계정을 자동으로 등록                              │
├────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 도구       │ 기존 Step Functions 계정 생성 워크플로에 단계 추가                                                     │
├────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 정답       │ ① Account Factory는 Service Catalog 제품 → ProvisionProduct API 호출로 등록 (D)<br>② aws.controltower  │
│ 메커니즘   │ 소스 + CreateManagedAccount detail-type EventBridge 이벤트로 등록 완료 감지·후속 처리 (A)              │
├────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 오답 함정  │ SetupLandingZone(랜딩존 설치용 이벤트), AWSControlTowerExecution 역할(기존 계정 enroll/크로스계정      │
│            │ 실행용), EnableAWSServiceAccess(서비스 액세스 활성화)                                                  │
└────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┘

▎ ⚠️ 문서 오류: 303번에 정답: C, D로 적혀 있으나 바로 아래 해설은 A와 D를 설명합니다(“…ProvisionProduct API를 호출해 계정을 등록(D)하고 … EventBridge 이벤트로 감지(A)”). 실제 정답은 A, D이고 C, D는 오타로 보입니다. 수정 필요.

핵심 축은 “Control Tower 신규 계정 자동 등록 + 이벤트 기반 후속 자동화” 이고, 이 축을 기준으로 4개 그룹이 나옵니다.

---
2. 그룹 A — Control Tower 계정 프로비저닝 / 베이스라인 (가장 유사)

┌──────┬─────────────────────────────┬───────────────────────┬────────────────────────────────────────────────────────┐
│ 번호 │            요지             │                 303과의 연결                      │
├──────┼─────────────────────────────┼───────────────────────┼────────────────────────────────────────────────────────┤
│      │ Control Tower 환경에서      │                                                   │
│ 227  │ 환경별 계정 + CI/CD 계정    │ A (AFC 블루프린트 +   │ 동일하게 Account Factory 경로. StackSets 별도          │
│      │ 생성 시 초기 베이스라인     │ Account정                                         │
│      │ 적용 (LEAST overhead)       │                       │                                                        │
├──────┼─────────────────────────────┼───────────────────────────────────────────────────┤
│      │ 계정이 요청해서 받을 수     │                       │ AFC 3요소 = CFn 템플릿(F) + Service Catalog 제품(C) +  │
│ 163  │ 있는 커스터마이징 제공      │ B, C, FwerBlueprintAccess 역할(B). 303의          │
│      │ (3택)                       │                       │ ProvisionProduct와 같은 “Account Factory = Service     │
│      │                             │                                                   │
├──────┼─────────────────────────────┼───────────────────────┼────────────────────────────────────────────────────────┤
│      │ 기존 + 미래 신규 계정까지   │ B (랜딩                                           │
│ 222  │ 예방적·탐지적 컨트롤        │  + Account Factory    │ “미래 계정까지” 요구 → Control Tower                   │
│      │ 거버넌스                    │ 프로비                                            │
├──────┼─────────────────────────────┼───────────────────────┼────────────────────────────────────────────────────────┤
│      │ 기존 + 미래 모든 계정에     │ B (Stacccount Factory(A)가 오답. 배포 대상이 기존 │
│ 382  │ 동일 IAM 역할/정책 배포     │ service-managed +     │  계정 포함 일괄이면 StackSets, 신규 계정 생성 흐름이면 │
│      │                             │ 자동 배tory                                       │
└──────┴─────────────────────────────┴───────────────────────┴────────────────────────────────────────────────────────┘

---
3. 그룹 B — aws.controltower EventBridge 이벤

┌──────┬──────────────────────────────┬──────┬───────────────────────────────────────────┐
│ 번호 │             요지             │ 정답 │                                 포인트                                 │
├──────┼──────────────────────────────┼──────┼───────────────────────────────────────────┤
│      │ Control Tower 관리형 AWS     │      │ 기존 계정 = OU 등록/재등록 이벤트(C) / 신규 계정 = 계정 enroll·랜딩존  │
│ 334  │ Config recorder를 기존 +     │ C,   │관리계정 역할 → AWSControlTowerExecution   │
│      │ 신규 계정 모두에             │ E, F │ 체이닝(E). 303과 이벤트+크로스계정 역할 조합이 판박이                  │
│      │ 커스터마이즈 (3택)           │      │                                           │
├──────┼──────────────────────────────┼──────┼────────────────────────────────────────────────────────────────────────┤
│      │ 신규 계정까지 Security Hub   │ A,   │ambda + CreateMembers가 오답으로 등장.     │
│ 101  │ 자동 등록 (3택)              │ C, E │ 네이티브 auto-enablement가 있으면 EventBridge+Lambda는 오답 — 303처럼  │
│      │                              │      │분하는 문제                                │
├──────┼──────────────────────────────┼──────┼────────────────────────────────────────────────────────────────────────┤
│      │ Control Tower 가드레일을     │      │trol(OU 단위) + CodeCommit + EventBridge → │
│ 348  │ 버전 관리·롤백 가능하게      │ C    │  CodePipeline. 이벤트 트리거 자동화 축은 같고 대상이 컨트롤            │
│      │ 자동화                       │      │                                           │
└──────┴──────────────────────────────┴──────┴────────────────────────────────────────────────────────────────────────┘

---
4. 그룹 C — “기존 + 미래 계정 모두” 요구 → 자

303의 “new accounts are automatically enrolled입니다.

┌───────────┬───────────────────────────────────────┐
│   번호    │                            수단                            │ 정답  │
├───────────┼───────────────────────────────────────┤
│ 102       │ GuardDuty 위임 관리자 + auto-enable                        │ A     │
├───────────┼───────────────────────────────────────┤
│ 101       │ Security Hub automatic enablement                          │ E     │
├───────────┼───────────────────────────────────────┤
│ 336       │ StackSets service-managed(root OU) + 관리 계정용 별도 스택 │ B     │
├───────────┼───────────────────────────────────────┤
│ 389       │ CDK 앱 + StackSets 컨스트럭트                              │ A     │
├───────────┼───────────────────────────────────────┤
│ 382       │ StackSets service-managed + automatic deployment           │ B     │
├───────────┼───────────────────────────────────────┤
│ 222 / 227 │ Control Tower Account Factory                              │ B / A │
└───────────┴───────────────────────────────────────┘

암기: 서비스 네이티브 자동 활성화 > StackSets ccount Factory/AFC > EventBridge + Lambda커스텀 (뒤로 갈수록 오버헤드 크고, 앞의 수단이 존재하면 뒤는 오답)

---
5. 그룹 D — 계정 생성 API 권한 · 크로스 계정

┌──────┬─────────────────────────────────┬───────────────────────────────────────────────┐
│ 번호 │              요지               │ 정답 │                               포인트                                │
├──────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│      │ Organizations 계정 생성         │      │ organizations:CreateAccount는 관리 계정에서만 → 크로스계정          │
│ 247  │ Lambda를 관리 계정 → 전용       │ A  roltower:CreateManagedAccount 위임이 함정  │
│      │ 계정으로 이전                   │      │                                                                     │
├──────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│ 167  │ CreateAccount CloudTrail        │ A    │ 크로스계정 EventBridge 표준 패턴: 소스 계정 규칙 → 대상 계정 기본   │
│      │ 이벤트를 서비스 계정들에 공유   │    책으로 허용 (305번과 동일 원리)            │
├──────┼─────────────────────────────────┼──────┼─────────────────────────────────────────────────────────────────────┤
│ 305  │ 다중 계정 Connect 이벤트를 단일 │ C  play 권한은 항상 오답                      │
│      │  DevOps 계정으로 집계           │      │                                                                     │
└──────┴─────────────────────────────────┴───────────────────────────────────────────────┘

---
6. 그룹 E — Control Tower 컨트롤 유형 구분 (인접 패턴)

┌──────────┬────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐
│   번호   │  정답  │                                                                   │
├──────────┼────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 206      │ B      │ 스택 생성 시점 차단 → pr                                          │
├──────────┼────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 321      │ A      │ 스택 작업 전 강제 → Clou 포                                       │
├──────────┼────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 198      │ A      │ 사후 탐지 + 알림 → 선택 dge → SNS                                 │
├──────────┼────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 402      │ D      │ Lambda VPC 연결 강제 → SVpcIds 부재 시 Deny). Control Tower       │
│          │        │ hooks(A)가 함정                                                                                │
├──────────┼────────┼───────────────────────────────────────────────────────────────────┤
│ 160 /    │ B,E /  │ SCP는 명시적 Allow 필요(root FullAWSAccess 유지) + 최소 범위 OU에 부착                         │
│ 104      │ C      │                                                                   │
└──────────┴────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘

---
7. 시험 직전 암기 카드 (303 계열)

┌─────────────────────────────────────────┬──────────────────────────────┐
│                 키워드                  │                           용도                            │
├─────────────────────────────────────────┼──────────────────────────────┤
│ ProvisionProduct (Service Catalog)      │ 신규 계정 Account Factory 등록 ← 303 D                    │
├─────────────────────────────────────────┼──────────────────────────────┤
│ CreateManagedAccount (aws.controltower) │ 계정 등록/생성 완료 이벤트 = 후속 자동화 훅 ← 303 A       │
├─────────────────────────────────────────┼──────────────────────────────┤
│ SetupLandingZone                        │ 랜딩존 최초 설치 이벤트 (계정 등록과 무관 = 오답)         │
├─────────────────────────────────────────┼──────────────────────────────┤
│ UpdateLandingZone / OU 재등록           │ 기존 계정 일괄 재적용 트리거 ← 334 C                      │
├─────────────────────────────────────────┼──────────────────────────────┤
│ AWSControlTowerExecution                │ 기존 계정 enroll·관리계정에서의 크로스계정 실행 ← 334 D·E │
├─────────────────────────────────────────┼──────────────────────────────┤
│ AWSControlTowerBlueprintAccess          │ AFC 블루프린트(Service Catalog 제품) 접근 ← 163 B         │
├─────────────────────────────────────────┼──────────────────────────────┤
│ AWS::ControlTower::EnableControl        │ 가드레일을 IaC로, OU 단위 ← 348 C                         │
└─────────────────────────────────────────┴──────────────────────────────┘
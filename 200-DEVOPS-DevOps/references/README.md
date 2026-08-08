### Control Tower 주요 주제

1. Control(GuardRail)
2. Landingzone
3. Account Provisioning + Baseline
4. New account automatic registration
5. IaC for Guardrail

---

EKS

Pod Identity access

355. CloudWatch Logs Data Protection

```text
CloudWatch Logs Data Protection은 CloudWatch Logs에 들어오는 로그에서 <br>
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

365. 

---

366. CodeBuild Webhook + Build Status Reporting + Artifacts

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






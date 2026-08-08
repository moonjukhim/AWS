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
CloudWatch Logs Data Protection은 CloudWatch Logs에 들어오는 로그에서 민감정보(PII, 금융정보, 자격증명 등)를 탐지하고 마스킹(masking)하는 기능
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

360. 

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
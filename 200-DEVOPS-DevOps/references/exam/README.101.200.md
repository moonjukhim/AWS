### 

### 101. Control Tower + Security Hub

Control Tower가 계정을 만들고 → Security Hub가 자동 활성화되고 → Security Account가 조직 전체 결과를 중앙집계하며 → IAM Identity Center가 누가 어디까지 볼 수 있는지를 통제

  - 1.CIS Benchmarks를 조직 전체에서 Security Hub로 평가
  - 2.조직 전체 결과는 Security Team만 조회
  - 3.새 계정이 생기면 자동으로 Security Hub 활성화


```text
AWS Organizations
│
├─ Management Account
│     │
│     └─ Security Hub Trusted Access 활성화
│
├─ Security Account
│     └─ Security Hub
│          ↑
│     **Delegated Administrator**
│          │
│          ├─ CIS AWS Foundations Benchmark
│          │
│          └─ 조직 전체 Findings 집계
│
├─ Member Account A
│     └─ Security Hub
│
├─ Member Account B
│     └─ Security Hub
│
└─ Member Account C
      └─ Security Hub
```

207. AWS Control Tower Proactive Control + CloudFormation Hooks

| 방법                             | 검사 시점   | 잘못된 S3 생성 차단 | Control Tower 필요 |
| ------------------------------- | ---------- | ----------------: | ---------------: |
| **CloudFormation Hook**         | 생성 **전** |               ✅ |                ❌ |
| Control Tower Proactive Control | 생성 **전** |               ✅ |                ✅ |
| AWS Config                      | 생성 **후** |               ❌ |                ❌ |
| SCP                             | API 호출 시 |           ✅ 가능 |                ❌ |

---

208. Amazon Managed Service for Prometheus workload alert

[Amazon Managed Service for Prometheus workload alert](https://aws.amazon.com/blogs/mt/alerting-best-practices-with-amazon-managed-service-for-prometheus/)

---

214. CloudFront Origin Group

```text
                    CloudFront
                        │
                 Default Behavior
                        │
                        ▼
                   Origin Group
                  /            \
                 /              \
        Primary Origin      Secondary Origin
             ALB                 ALB
          Region A             Region B
              │
              │ 5xx 발생
              └──────────────→ Failover
```

227. Account Factory Customization(AFC) Blueprint

```text
A - AFC

Account Factory
      │
      │ Blueprint
      ▼
┌──────────────────┐
│ New Account      │
│                  │
│ Control Tower    │
│ +                │
│ Custom Baseline  │
└──────────────────┘

계정 생성과 Baseline 통합
        ✅
```

```text
B

Account Factory
      │
      ▼
┌──────────────────┐
│ New Account      │
└──────────────────┘
      │
      ▼
CloudFormation StackSets
      │
      ▼
Baseline Configuration

두 가지 프로세스 관리
        △
```

239. AWS API를 호출할 때 누구의 IAM 권한을 사용할 것인가?

| 구분                  | 권한을 사용하는 주체    | 용도                                |
| -------------------- | -------------------- | --------------------------------- |
| **Cluster IAM Role** | EKS Control Plane    | EKS가 AWS 리소스를 관리                  |
| **IRSA**             | Pod → ServiceAccount | Pod에 AWS 권한 부여                    |
| **EKS Pod Identity** | Pod → ServiceAccount | Pod에 AWS 권한 부여, **IRSA보다 관리 단순화** |



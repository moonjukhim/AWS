
#### Control Tower 기능

```text
                    AWS Control Tower

                           │

        ┌──────────────────┼───────────────────┬───────────────────┐

        ▼                  ▼                   ▼                   ▼

   Landing Zone      Account Factory      Governance           Lifecycle Automation

      │                    │                  │                      │

      │                    │                  │

      ▼                    ▼                  ▼

 OU 생성             계정 생성/등록           SCP                       Register OU
 Guardrails          계정 Provision         Config                    Re-register OU
 Logging             Enrollment            Detective Control         기존 리소스(Customization) 자동 적용
```

```text
                      AWS Control Tower
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
     Account Factory   Account Factory     Landing Zone
          │             Customization      OU / Accounts
          │                 │                  │
          ▼                 ▼                  ▼
        AFT               AFC                CfCT
          │                 │                  │
      Terraform         Blueprint        StackSets + SCP
          │            Service Catalog         │
          ▼                 ▼                  ▼
   계정 생성/관리       계정 초기 구성       조직 공통 구성
```



### 101. Control Tower + Security Hub

Control Tower가 계정을 만들고 → Security Hub가 자동 활성화되고 → Security Account가 조직 전체 결과를 중앙집계하며 → IAM Identity Center가 누가 어디까지 볼 수 있는지를 통제

  - 1.CIS Benchmarks를 조직 전체에서 Security Hub로 평가
  - 2.조직 전체 결과는 Security Team만 조회
  - 3.새 계정이 생기면 자동으로 Security Hub 활성화


```text
                    AWS Organizations
                           │
                 Management Account
                           │
                Trusted Access 활성화
                           │
                           ▼
              ┌────────────────────────┐
              │   Security Account     │
              │ Delegated Administrator│ ← A
              │                        │
              │ Security Hub           │
              │ + CIS Benchmark        │
              └────────────┬───────────┘
                           │
                    Findings 집계
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Account A         Account B        New Account
     Security Hub      Security Hub     Security Hub
          ▲                ▲                ▲
          │                │                │
          └────────────────┴────────────────┘
                    Auto-enable ← E


Security Team
     │
     │ IAM Identity Center
     │ Permission Set ← C
     ▼
Security Account
     │
     └─ 조직 전체 Aggregated Findings 조회
```

## 163. AWS Control Tower의 Account Factory Customization(AFC) / Blueprint 구조

```text
CloudFormation Template      ← F
        │
        ▼
Service Catalog Product      ← C
        │
        ▼
Account Factory Blueprint
        │
        │ AWSControlTowerBlueprintAccess ← B
        ▼
AWS Control Tower
        │
        ▼
새 Account + Customization
```

## 334


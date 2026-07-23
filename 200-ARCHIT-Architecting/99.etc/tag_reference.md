````markdown
# AWS Tag & Billing Tag 설정 가이드

## 1. 목적

본 가이드는 AWS 리소스에 일관된 Tag 정책을 적용하여 다음 목적을 달성하는 것을 목표로 한다.

- 비용(Cost) 추적
- 조직 및 프로젝트 관리
- 운영 자동화
- 보안 정책 적용
- 리소스 관리 효율화
- FinOps 기반 구축

---

# 2. Tag란?

AWS Tag는 리소스에 추가하는 메타데이터(Key-Value)이다.

```text
Key = Value
```

예시

| Key | Value |
|------|--------|
| Environment | Production |
| Project | ShoppingMall |
| Owner | Platform-Team |

AWS 리소스 하나당 최대 **50개의 Tag**를 지정할 수 있다.

### 적용 가능한 대표 리소스

- EC2
- S3
- RDS
- Lambda
- VPC
- EKS
- ECS
- IAM Role (일부)
- CloudFormation Stack
- Backup Vault

---

# 3. Tag의 종류

## 3.1 일반 Tag

운영 및 관리 목적으로 사용하는 태그

예시

| Key | Value |
|------|--------|
| Owner | Platform-Team |
| Environment | Dev |
| Application | Payment |

---

## 3.2 Billing Tag (Cost Allocation Tag)

AWS Billing에서 비용 분석을 위해 사용하는 태그

예시

| Key | Value |
|------|--------|
| CostCenter | CC-1001 |
| Project | AI-Agent |
| Department | Platform |

> **중요**
>
> Billing Tag는 태그를 추가하는 것만으로는 비용 분석에 사용되지 않는다.
> 반드시 **Billing Console**에서 활성화해야 한다.

---

# 4. Tag 설계 원칙

## 4.1 Key 이름 표준화

좋은 예

```text
Environment
```

나쁜 예

```text
Env
ENV
environment
환경
```

---

## 4.2 Value 표준화

좋은 예

```text
Production
```

나쁜 예

```text
Prod
prd
live
운영
```

---

## 4.3 대소문자 통일

권장

```text
Environment
Project
Owner
CostCenter
```

---

# 5. 권장 필수(Tag Mandatory)

| Key | 설명 | 예시 |
|------|------|------|
| Name | 리소스 이름 | web-prod-01 |
| Environment | 운영 환경 | Dev / Test / Stage / Prod |
| Project | 프로젝트 | AI-Platform |
| Application | 서비스명 | Payment |
| Owner | 담당 조직 | Platform-Team |
| CostCenter | 비용센터 | CC1001 |
| Department | 부서 | Engineering |
| ManagedBy | 관리도구 | Terraform |
| CreatedBy | 생성도구 | CloudFormation |
| Confidentiality | 데이터 등급 | Public / Internal / Confidential |

---

# 6. Billing Tag 권장 항목

| Key | 목적 |
|------|------|
| CostCenter | 비용센터별 분석 |
| Department | 부서별 비용 |
| Project | 프로젝트별 비용 |
| Application | 서비스별 비용 |
| Environment | 운영/개발 비용 비교 |
| BusinessUnit | 사업부별 비용 |
| Team | 팀별 비용 |
| Customer | 고객별 비용 |
| Product | 제품별 비용 |

---

# 7. Tag 적용 예시

## EC2

| Key | Value |
|------|--------|
| Name | payment-api-01 |
| Environment | Production |
| Project | PG |
| Owner | Backend-Team |
| CostCenter | CC1001 |

---

## S3

| Key | Value |
|------|--------|
| Name | image-storage |
| Environment | Production |
| Project | Commerce |
| Department | Platform |

---

# 8. Billing Tag 활성화

태그를 추가했다고 바로 비용 분석이 가능한 것은 아니다.

다음 메뉴에서 활성화해야 한다.

```text
Billing Console
    ↓
Cost Allocation Tags
    ↓
User-defined
    ↓
Activate
```

> 활성화 이후부터 발생하는 비용만 Cost Explorer 및 CUR에서 사용할 수 있다.

---

# 9. AWS에서 자동 생성하는 Tag

AWS는 일부 시스템 태그를 자동으로 생성한다.

예시

```text
aws:cloudformation:stack-name

aws:createdBy

eks:cluster-name
```

> `aws:`로 시작하는 태그는 수정하거나 삭제할 수 없다.

---

# 10. Cost Explorer 활용

Billing Tag를 활성화하면 Cost Explorer에서 다음과 같이 비용을 분석할 수 있다.

```text
Group By

Project
```

또는

```text
Group By

CostCenter
```

예시

| Project | Cost |
|----------|------|
| AI-Agent | $3,200 |
| Shopping | $8,500 |
| Marketing | $1,200 |

---

# 11. AWS Organizations Tag Policy

Organizations에서는 Tag Policy를 이용하여 태그 값을 표준화할 수 있다.

예시

Environment 허용 값

```text
Dev
Test
Stage
Prod
```

잘못된 값

```text
Production
prd
live
```

Tag Policy를 적용하면 허용되지 않은 값을 탐지하거나 제한할 수 있다.

---

# 12. SCP(Service Control Policy) 연계

필수 태그가 없는 리소스 생성을 차단할 수 있다.

예시

EC2 생성 시

```text
CostCenter
```

태그가 없으면

```text
Deny
```

---

# 13. AWS Config 연계

AWS Config의 `required-tags` Managed Rule을 사용하면

필수 태그가 없는 리소스를 자동으로 탐지할 수 있다.

예시

필수 Tag

- Owner
- Project
- Environment

누락 시

```text
NON_COMPLIANT
```

으로 표시된다.

---

# 14. IaC(Infrastructure as Code)에서 Tag 적용

## CloudFormation

```yaml
Tags:
  - Key: Environment
    Value: Production
```

---

## Terraform

```hcl
tags = {
  Environment = "Production"
  Project     = "AI-Agent"
}
```

---

## AWS CDK (TypeScript)

```typescript
Tags.of(instance).add("Environment", "Production");
Tags.of(instance).add("Project", "AI-Agent");
```

---

# 15. 운영 Best Practice

| 항목 | 권장사항 |
|------|----------|
| Tag 표준 | 중앙에서 정의 및 관리 |
| Mandatory Tag | Name, Environment, Project, Owner, CostCenter |
| IaC | 기본 Tag 자동 적용 |
| Tag Policy | 허용 값 강제 |
| SCP | 필수 Tag 없는 생성 차단 |
| AWS Config | Tag 누락 지속 점검 |
| Billing Tag | CostCenter, Project, Department 활성화 |
| Cost Explorer | Billing Tag 기준 비용 분석 |
| CUR(Cost & Usage Report) | Athena, QuickSight 연계 |
| 자동화 | Lambda + EventBridge로 태그 보완 |

---

# 16. 추천 Tag 표준

| Tag Key | 필수 | Billing | 예시 |
|----------|:----:|:------:|------|
| Name | ✅ | ❌ | web-prod-01 |
| Environment | ✅ | ✅ | Prod |
| Project | ✅ | ✅ | AI-Platform |
| Application | ✅ | ✅ | Payment |
| Owner | ✅ | ❌ | Platform-Team |
| CostCenter | ✅ | ✅ | CC-1001 |
| Department | ✅ | ✅ | Engineering |
| BusinessUnit | 선택 | ✅ | Commerce |
| ManagedBy | 선택 | ❌ | Terraform |
| CreatedBy | 선택 | ❌ | CloudFormation |
| Confidentiality | 선택 | ❌ | Internal |

---

# 17. 운영 아키텍처 예시

```text
Developer
      │
      ▼
Terraform / CloudFormation
      │
      ▼
AWS Resources
      │
      ├──────────────┐
      │              │
      ▼              ▼
Tag Policy      AWS Config
      │              │
      └──────┬───────┘
             ▼
     표준 Tag 적용
             │
             ▼
 Billing Cost Allocation Tag
             │
             ▼
      Cost Explorer / CUR
             │
             ▼
 Athena / QuickSight
             │
             ▼
      FinOps Dashboard
```

---

# 18. 핵심 체크리스트

| 항목 | 완료 여부 |
|------|:---------:|
| Tag 표준 정의 | ☐ |
| Mandatory Tag 정의 | ☐ |
| Billing Tag 활성화 | ☐ |
| IaC 기본 Tag 적용 | ☐ |
| Tag Policy 적용 | ☐ |
| SCP 적용 | ☐ |
| AWS Config Rule 적용 | ☐ |
| Cost Explorer 검증 | ☐ |
| CUR 생성 | ☐ |
| Athena/QuickSight 연계 | ☐ |
````


48. 

```text
              AWS Organizations
                     │
              AWS Control Tower
                     │
               Account Factory
                     │
              신규 Account 생성
                     ↓
          ┌─────────────────────┐
          │        CfCT         │
          │ Customizations for  │
          │ AWS Control Tower   │
          └──────────┬──────────┘
                     │
              Custom Package
              /              \
             ↓                ↓
   CloudFormation         SCP JSON
      Templates
             │                │
             └───────┬────────┘
                     ↓
             OU / Account별 적용
                     ↓
              New AWS Account
```

| 보기    | 핵심 방식                                           | 대표 사용 사례                                                                               | 이 문제에서의 판단                                                             |
| ----- | ----------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **A** | **AWS Service Catalog + Portfolio/Product**     | 조직이 승인한 표준 인프라를 사용자가 **셀프서비스로 선택해서 생성**하도록 제공할 때                                       | ❌ 신규 계정 생성 시 자동 customization 목적과는 다름                                  |
| **B** | **CloudFormation StackSets**                    | 동일한 CloudFormation 템플릿을 **여러 AWS 계정/리전에 일괄 배포**할 때                                     | △ CloudFormation 배포에는 좋지만 Control Tower + SCP customization을 직접 구성해야 함 |
| **C** | **EventBridge + Service Catalog**               | 특정 AWS 이벤트가 발생했을 때 **이벤트 기반으로 별도 provisioning workflow를 실행**할 때                        | ❌ 구현 가능하지만 CfCT보다 구성 요소가 많고 SCP도 별도 처리                                 |
| **D** | **Customizations for AWS Control Tower (CfCT)** | Control Tower Account Factory로 생성되는 계정에 **OU/Account별 CloudFormation + SCP를 자동 적용**할 때 | ✅ **정답**                                                               |

---


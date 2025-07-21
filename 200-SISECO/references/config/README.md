# AWS Config

### AWS Config의 기준선

| 구분       | 설명                                                    |
|-----------|---------------------------------------------------------|
| 정의 방식  | 명시적 규칙 기반 (수동 정의)                                |
| 주요 대상  | IAM, S3, EC2, VPC, CloudTrail, Tag 등                   |
| 관리 방식  | 관리형 규칙 / 사용자 정의 규칙 / Conformance Pack           |
| 적용 목적  | 보안, 비용, 거버넌스 기준 강제                              |

### AWS Config에서 지정할 수 있는 기준선

| 구분                     | 항목                  | 설명                                                      |
|--------------------------|-----------------------|---------------------------------------------------------|
| IAM 및 보안 관련 기준    | MFA 사용 여부         | 루트 계정 또는 모든 사용자에 MFA가 활성화되어야 함                |
| IAM 및 보안 관련 기준    | IAM 정책 제약         | 사용자가 너무 넓은 권한(`*:*`)을 갖지 않도록 제한                 |
| IAM 및 보안 관련 기준    | 루트 계정 사용 금지   | 루트 계정 사용을 탐지 및 금지                                    |
| IAM 및 보안 관련 기준    | S3 퍼블릭 접근 차단   | S3 버킷이 공개되지 않도록 강제                                   |
| 네트워크 설정 관련 기준 | 보안 그룹 제한        | 특정 포트(예: 22, 3389)가 인터넷에 열려 있지 않도록 함            |
| 네트워크 설정 관련 기준 | VPC 흐름 로그 활성화  | VPC에 대해 Flow Logs가 활성화되어 있어야 함                         |
| 네트워크 설정 관련 기준 | 서브넷 라우팅         | 퍼블릭 서브넷은 올바른 NAT 구성을 가져야 함                         |
| 리소스 및 태그 기준     | EC2 인스턴스 유형 제한| 비용 최적화를 위해 특정 인스턴스 유형만 사용 허용                    |
| 리소스 및 태그 기준     | 태그 정책             | 모든 리소스에 `Owner`, `Environment`, `Project` 태그가 있어야 함 |
| 리소스 및 태그 기준     | 리전 제한             | 특정 리전에서만 리소스를 생성하도록 제한                           |
| 암호화 및 로깅 기준     | S3 암호화 강제        | 버킷에 대해 SSE-S3 또는 SSE-KMS 암호화 필수                       |
| 암호화 및 로깅 기준     | EBS 볼륨 암호화       | 새로 생성되는 모든 EBS는 암호화되어야 함                            |
| 암호화 및 로깅 기준     | CloudTrail 활성화     | 모든 리전에 CloudTrail이 활성화되어야 함                          |


---

1. AWS Config 활성화

```bash
aws configservice put-configuration-recorder \
--recording-group allSupported=false,includeGlobalResourceTypes=\
false,resourceTypes=AWS::S3::Bucket \
--configuration-recorder name=default,roleARN=<ConfigRoleARN>
```

```bash
aws configservice put-delivery-channel \
--delivery-channel configSnapshotDeliveryProperties=\
{deliveryFrequency=Twelve_Hours},name=default,\
s3BucketName=<ConfigS3BucketName>,\
snsTopicARN=<ConfigSNSTopic>
```

```bash
aws configservice start-configuration-recorder --configuration-recorder-name default
```

---

# References

- [ISMS-P 를 위한 AWS Config 규정 준수 팩 사용하기](https://aws.amazon.com/ko/blogs/korea/aws-conformance-pack-for-k-isms-p-compliance/)

- [AWS Config Conformance packs - KISMS](https://github.com/awslabs/aws-config-rules/blob/master/aws-config-conformance-packs/Operational-Best-Practices-for-KISMS.yaml)

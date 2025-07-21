# AWS Config

### AWS Config의 기준선

| 구분       | 설명                                                    |
|-----------|---------------------------------------------------------|
| 정의 방식  | 명시적 규칙 기반 (수동 정의)                                |
| 주요 대상  | IAM, S3, EC2, VPC, CloudTrail, Tag 등                   |
| 관리 방식  | 관리형 규칙 / 사용자 정의 규칙 / Conformance Pack           |
| 적용 목적  | 보안, 비용, 거버넌스 기준 강제                              |


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

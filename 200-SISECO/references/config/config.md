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

- [ISMS-P 를 위한 AWS Config 규정 준수 팩 사용하기](https://aws.amazon.com/ko/blogs/korea/aws-conformance-pack-for-k-isms-p-compliance/)

- [AWS Config Conformance packs - KISMS](https://github.com/awslabs/aws-config-rules/blob/master/aws-config-conformance-packs/Operational-Best-Practices-for-KISMS.yaml)

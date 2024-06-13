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

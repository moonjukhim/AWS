# AWS Config를 사용한 모니터링 및 대응

## 과제1.Amazon S3 액세스 정책 검토

## 과제2.Amazon Linux EC2 인스턴스에 연결

## 과제3.AWS Config를 활성화하여 Amazon S3 버킷 모니터링

## 과제4.CloudWatch Events 규칙 생성 및 구성

```bash
cat <<EOF > S3ProhibitPublicReadAccess.json
{
  "ConfigRuleName": "S3PublicReadProhibited",
  "Description": "Checks that your S3 buckets do not allow public read access. If an S3 bucket policy or bucket ACL allows public read access, the bucket is noncompliant.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::S3::Bucket"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }
}
EOF
```

```bash
cat <<EOF > S3ProhibitPublicWriteAccess.json
{
  "ConfigRuleName": "S3PublicWriteProhibited",
  "Description": "Checks that your S3 buckets do not allow public write access. If an S3 bucket policy or bucket ACL allows public write access, the bucket is noncompliant.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::S3::Bucket"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "S3_BUCKET_PUBLIC_WRITE_PROHIBITED"
  }
}
EOF
```
# 모듈11: AWS Glue를 사용하여 ETL 워크로드 자동화


---

## 참고자료

[AWS Glue 리소스에 대한 액세스 권한 관리]https://docs.aws.amazon.com/ko_kr/glue/latest/dg/access-control-overview.html



Kinesis agent 설치

```bash
sudo yum install –y https://s3.amazonaws.com/streaming-data-agent/aws-kinesis-agent-latest.amzn1.noarch.rpm
```

Kinesis agent 구성 파일

```bash
sudo sh -c 'cat <<EOF >  /etc/aws-kinesis/agent.json
{
  "cloudwatch.endpoint": "monitoring.<AWSRegion>.amazonaws.com",
  "cloudwatch.emitMetrics": true,
  "firehose.endpoint": "firehose.<AWSRegion>.amazonaws.com",
  "flows": [
    {
      "filePattern": "/var/log/httpd/access_log",
      "deliveryStream": "<DeliveryStream>"
    }
  ]
}
EOF'
```

Kinesis 에이전트 시작

```bash
sudo systemctl start aws-kinesis-agent.service
```

Apache 액세스 로그 파일 확인

```bash
tail -f /var/log/httpd/access_log
```

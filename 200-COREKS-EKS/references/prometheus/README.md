### Grafana 대시보드 JSON 구성파일

##### 주요 특징

| 항목         | 설명                                                                 |
|--------------|----------------------------------------------------------------------|
| **title**     | Kubernetes cluster monitoring (via Prometheus)                      |
| **gnetId**    | 3119 - Grafana 공식 대시보드 공유 ID                                 |
| **datasource**| Prometheus 사용 (`$datasource` 변수로 다중 Prometheus 지원)         |
| **목표**      | CPU, Memory, Network, Container, Node 등 클러스터 상태 시각화        |
| **템플릿 변수**| `$interval`, `$datasource`, `$Node` 등 사용자 선택 가능             |
| **refresh**   | 기본 10초마다 자동 새로고침                                          |
| **버전**      | Grafana plugin version 10.1.5 기반                                   |
| **스타일**    | 다크 테마(`"style": "dark"`)                                         |

##### 주요 패널 구성

| 패널 제목                          | 설명                                           |
|-----------------------------------|------------------------------------------------|
| **Cluster memory usage**          | 클러스터 메모리 사용률 (%) Gauge로 표시        |
| **Cluster CPU usage**             | 클러스터 CPU 사용률 (%) Gauge로 표시           |
| **Containers CPU usage**          | 컨테이너별 CPU 사용량 그래프                   |
| **Containers memory usage**       | 컨테이너별 메모리 사용량 그래프                |
| **All processes CPU/memory/network I/O** | 전체 프로세스 단위의 자원 사용률     |
| **Network I/O pressure**          | 수신/송신 네트워크 트래픽 시각화              |
| **Used / Total 메모리/CPU**       | 현재 사용량과 총량 비교용 Stat 패널            |

##### Kubernetes에서 Prometheus 구성 요소

| 구성 요소                  | 역할                                                                 |
|---------------------------|----------------------------------------------------------------------|
| **Prometheus Server**     | 지표를 수집(scrape)하고 로컬 DB에 저장                               |
| **Node Exporter**         | 노드의 CPU, 메모리, 디스크 등 **시스템 지표 제공**                   |
| **Push Gateway**          | short-lived job들이 **지표를 push**할 수 있도록 중간 게이트웨이 역할 |
| **Alert Manager**         | 조건 충족 시 **알람 발송**, 슬랙/이메일 연동 가능                     |
| **kube-state-metrics**    | Deployment, ReplicaSet 등의 **상태 정보 지표** 제공 (Kubernetes 상태 중심) |


##### delivery-stream.json

```json
{
  "DeliveryStreamName": "eks-stream",
  "DeliveryStreamType": "DirectPut",
  "AmazonopensearchserviceDestinationConfiguration": {
  "RoleARN": "${STREAM_BUCKET_ARN}",
  "DomainARN": "arn:aws:es:${AWS_REGION}:${ACCOUNT_ID}:domain/eks-domain",
  "IndexName": "access-logs",
  "S3Configuration": {
        "RoleARN": "${FIREHOSE_ROLE_ARN}",
        "BucketARN": "arn:aws:s3:::labstack-2ff18e01-e448-468f-bff5-9d-firehosebucket-zucgqya2sjrx"
    }
  }
}
```

```bash
aws firehose create-delivery-stream --cli-input-json file:///home/ssm-user/delivery-stream.json
```


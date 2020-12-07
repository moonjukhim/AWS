# 실습 4: 로그 수집 및 분석

## 과제 1: 배스천 호스트에 연결

## 과제 2: Amazon Kinesis Data Firehose 전송 스트림 생성 및 Fluent Bit DaemonSet 구성

## 과제 3: 샘플 애플리케이션 배포, 로그 데이터 수집 및 Amazon Athena를 사용하여 데이터 분석

## 과제 4: Amazon CloudWatch Container Insights 배포 및 구성

## 과제 5: AWS X-Ray 배포 및 트레이스 지표 검토

---

cluster.yaml

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: dev-cluster
  region: us-east-1
  version: "1.16"
vpc:
  id: vpc-0b9e59b519b7a3c93
  securityGroup: "sg-056490d2267ca2625"
  subnets:
    public:
      us-east-1a: { id: subnet-0ea91da6f2a89fa60 }
      us-east-1b: { id: subnet-0dfaf08ca9e5864da }
      us-east-1c: { id: subnet-091c39c76e3273bed }
  clusterEndpoints:
    publicAccess: true
    privateAccess: true
iam:
  serviceRoleARN: "arn:aws:iam::702995877146:role/EksClusterRole"
managedNodeGroups:
  - name: dev-nodes
    minSize: 2
    maxSize: 4
    desiredCapacity: 3
    volumeSize: 20
    instanceType: t3.medium
    iam:
      instanceRoleARN: arn:aws:iam::702995877146:role/EksNodeRole
```


## Task3 Load Gen

```bash
#!/bin/bash

################################################################################
# Generate load for the NGINXs services in EKS

# make sure to patch to LB
kubectl patch svc nginx -p '{"spec": {"type": "LoadBalancer"}}'

# give the LB 3 minutes to be up and running
echo "Now waiting for 3min until the load balancer is up ..."
sleep 180

echo "Starting to hammer the load balancer:"

nginxurl=$(kubectl get svc/nginx -o json | jq .status.loadBalancer.ingress[].hostname -r)
while true
do
    printf "Hit "
        curl -s $nginxurl > /dev/null
        printf "$nginxurl "
    printf "\n"
    sleep 2
done
```
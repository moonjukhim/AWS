
## 과제2: Amazon EKS 클러스터 및 관리형 노드 그룹 배포

```
eksctl create cluster \
--name dev-cluster \
--nodegroup-name dev-nodes \
--node-type t3.small \
--nodes 3 \
--nodes-min 1 \
--nodes-max 4 \
--managed \
--version 1.16 \
--region ${AWS_REGION}
```

## 과제3: 샘플 애플리케이션 배포 및 구성

## 과제4: 애플리케이션 배포 확장


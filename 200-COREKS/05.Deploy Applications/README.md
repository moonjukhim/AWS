# ECR

```bash
aws ecr create-repository \
    --repository-name project-a/nginx-web-app

aws ecr set-repository-policy \
    --repository-name project-a/nginx-web-app \
    --policy-text file://repository-policy.json
```

```yaml
{
  "Version": "2008-10-17",
  "Statement":
    [
      {
        "Sid": "allow public pull",
        "Effect": "Allow",
        "Principal": "*",
        "Action":
          [
            "ecr:BatchCheckLayerAvailability",
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
          ],
      },
    ],
}
```

# Helm

```bash
# Chart 생성
helm create helm-test

# 패키지 설치
helm install helm-test helm-test
```

```bash
kubectl get services
```

### References

[Management Console 에서 Kubernetes 리소스 보기](https://docs.aws.amazon.com/eks/latest/userguide/view-kubernetes-resources.html)

# us-west-2

1. Download ekstcl

```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
```

2. Move bin

```bash
sudo mv /tmp/eksctl /usr/local/bin
eksctl version
```

3. Create a EKS Cluster

```bash
eksctl create cluster \
--name fargate-tutorial-cluster \
--version 1.24 \
--region us-west-2 \
--fargate \
--alb-ingress-access
```

4. Verify Cluster Info

```bash
eksctl get cluster --region us-west-2 --name fargate-tutorial-cluster -o yaml
```

5. Check Namespace

```bash
kubectl get ns
kubectl get nodes
```

6. Nginx deployment

```bash
kubectl create deployment nginx --image=nginx
kubectl get deployment
```

7. Delete Nginx Deployment

```bash
kubectl delete deployment nginx
```

8. Delete a EKS Cluster

```bash
eksctl delete cluster \
--name fargate-tutorial-cluster 
```
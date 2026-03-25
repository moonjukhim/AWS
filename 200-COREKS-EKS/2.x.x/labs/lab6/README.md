#

1. 과제 1: 애플리케이션 온라인 연결
2. 과제 2: 애플리케이션 Helm 차트 업데이트
3. 과제 3: 영구 스토리지 구성

apiVersion: v1
kind: Service
metadata:
  name: proddetail
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: instance
  namespace: workshop
  labels:
    app: proddetail
  annotations:
    owner: student
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  selector:
    app: proddetail
  loadBalancerClass: service.k8s.aws/nlb
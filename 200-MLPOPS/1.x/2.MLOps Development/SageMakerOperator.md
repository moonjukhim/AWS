[Simplify Machine Learning Inference on Kubernetes with Amazon SageMaker Operators](https://aws.amazon.com/ko/blogs/machine-learning/simplify-machine-learning-inference-on-kubernetes-with-amazon-sagemaker-operators/)

1. Preparing your hosting deployment

```yaml
apiVersion: sagemaker.aws.amazon.com/v1
kind: HostingDeployment
metadata:
  name: hosting-deployment
spec:
  region: us-east-2
  productionVariants:
    - variantName: AllTraffic
      modelName: xgboost-model
      initialInstanceCount: 1
      instanceType: ml.r5.large
      initialVariantWeight: 1
  models:
    - name: xgboost-model
      executionRoleArn: SAGEMAKER_EXECUTION_ROLE_ARN
      containers:
        - containerHostname: xgboost
          modelDataUrl: s3://BUCKET_NAME/model.tar.gz
          image: 825641698319.dkr.ecr.us-east-2.amazonaws.com/xgboost:latest
```

2. Deploying your model to Amazon SageMaker

```bash
kubectl apply -f hosting.yaml
# hostingdeployment.sagemaker.aws.amazon.com/hosting-deployment created
```

3. Querying the endpoint

```bash
aws sagemaker-runtime invoke-endpoint \
  --region us-east-2 \
  --endpoint-name SAGEMAKER-ENDPOINT-NAME \
  --body $(seq 784 | xargs echo | sed 's/ /,/g') \
  >(cat) \
  --content-type text/csv > /dev/null
```

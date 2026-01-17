# SAM
From: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html

---

## Step 1 - sample 애플리케이션 다운로드
```bash
# cd ~/environment/
sam init --runtime python3.6
```

## Step 2 - 애플리케이션 빌드
```bash
cd sam-app
sam build
```

## Step 3 - 람다 테스트
```bash
sam local invoke "HelloWorldFunction" -e events/event.json
sam local start-api
curl http://127.0.0.1:3000/hello 
```

## Step 4 - 애플리케이션 패키징
```bash
aws s3 mb s3://aws-devops-demo-sam-henry-2021
sam package --output-template-file packaged.yaml --s3-bucket  aws-devops-demo-sam-henry-2021
```

## Step 5 - 애플리케이션 배포

```bash
sam deploy --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name sam-app 
```

## Step 6 - 애플리케이션 삭제

```bash
aws cloudformation delete-stack --stack-name sam-app
```

--- 

# Step 7 - (TODO) DEVOPS에서 CI/CD 파이프라인을 사용하여 배포 자동화
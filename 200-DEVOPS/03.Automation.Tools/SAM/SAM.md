From: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html

---

# Step 1 - sample application 다운로드
```bash
sam init --runtime python3.8
```

# Step 2 - 애플리케이션 빌드
```bash
cd sam-app
sam build
```

# Step 3 - Test the function
```bash
sam local invoke "HelloWorldFunction" -e events/event.json
sam local start-api
curl http://127.0.0.1:3000/hello 
```

# Step 4 - Package your application
sam package --output-template packaged.yaml --s3-bucket aws-devops-course-stephane --region eu-west-1 --profile aws-devops

# Step 5 - Deploy your application
sam deploy --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name aws-sam-getting-started --region eu-west-1 --profile aws-devops
###

1. SAM 프로젝트 초기화

```bash
sam init --runtime python3.13
```

2. 빌드 수행

```bash
cd ./sam-app
sam build
```

3. 테스트

```bash
sam local invoke HelloWorldFunction --event events/event.json
```

4. 애플리케이션 배포

```bash
labBucket=lab4-sam-[YOUR-INITIALS]-[YOUR-POSTAL-CODE]
# labBucket=lab4-sam-henry-1103103103
aws s3 mb s3://$labBucket
```

- sam-app/samconfig.toml의 [default.package.parameters] 섹션에서 
- resolve_s3 = true를 resolve_s3 = false로 변경


```bash
sam package --output-template-file packaged.yaml --s3-bucket $labBucket
```

```bash
sam deploy --template-file packaged.yaml --stack-name sam-app --capabilities CAPABILITY_IAM
```


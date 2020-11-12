# 실습4. AWS SAM과 CI/CD 파이프라인을 사용하여 서버리스 애플리케이션 배포

---

# 작업1 : AWS SAM 요소 소개

# 작업2 : AWS CodePipeline을 사용하여 애플리케이션 배포 자동화

buildspec.yml

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
        nodejs: 10
  build:
    commands:
      - npm install time
      - export BUCKET=lab4-sam-artifacts-<YOUR INITIALS>-<ZIP CODE>
      - aws cloudformation package --template-file template.yaml --s3-bucket $BUCKET --output-template-file outputtemplate.yaml
artifacts:
  type: zip
  files:
    - template.yaml
    - outputtemplate.yaml
```

# 작업3 : 애플리케이션을 새로 변경하고 다시 배포

# 1.소스 파일 설정

```yml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws --version
      - $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)
    # - REPOSITORY_URI=<ACCOUNT-ID>.dkr.ecr.<REGION>.amazonaws.com/<BASE-REPO-NAME>
      - REPOSITORY_URI=000000000000.dkr.ecr.us-west-2.amazonaws.com/gold-repo
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t $REPOSITORY_URI:latest .
      - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker images...
      - docker push $REPOSITORY_URI:latest
      - docker push $REPOSITORY_URI:$IMAGE_TAG
```

Dockerfile

```
FROM ubuntu:18.04

# Install dependencies
RUN apt-get update
RUN apt-get -y install apache2
```

# 2.지속적 전달 파이프라인 생성

# 3.블루/그린 배포를 지원하도록 클러스터 준비

# 4.블루/그린 배포 구성

# 5.CodePipeline 자동화 테스트


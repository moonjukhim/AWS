# 

![ecs_bluegreen](.)

---
### 1.소스 파일 설정

buildspec.yaml

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

Task 1.3: my-webapp 애플리케이션 파일 구성

```
# FROM ubuntu:18.04

# # Install dependencies
# RUN apt-get update
# RUN apt-get -y install apache2

# Install apache and write hello world message
# FROM <ACCOUNT-ID>.dkr.ecr.<REGION>.amazonaws.com/<BASE-REPO-NAME>
FROM 000000000000.dkr.ecr.us-west-2.amazonaws.com/gold-repo
    
RUN echo '<html> <head> <title>Amazon ECS</title> <style>body {margin-top: 40px; background-color:blue;} </style> </head><body> <div style=color:white;text-align:center> <h1>Congratulations!!!</h1> <h2>Your application is now running on a container in Amazon ECS using a base image from ECR</h2> </div></body></html>' > /var/www/html/index.html

# Configure apache
RUN echo '. /etc/apache2/envvars' > /root/run_apache.sh && \
 echo 'mkdir -p /var/run/apache2' >> /root/run_apache.sh && \
 echo 'mkdir -p /var/lock/apache2' >> /root/run_apache.sh && \ 
 echo '/usr/sbin/apache2 -D FOREGROUND' >> /root/run_apache.sh && \ 
 chmod 755 /root/run_apache.sh

EXPOSE 80 8080

CMD /root/run_apache.sh
```

buildspec.yml

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws --version
      - $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)
    # - REPOSITORY_URI=<>ACCOUNT-ID>.dkr.ecr.<REGION>.amazonaws.com/<APPLICATION-REPO-NAME> 
      - REPOSITORY_URI=00000000000.dkr.ecr.ap-northeast-2.amazonaws.com/my-webapp-repo
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=build-$(echo $CODEBUILD_BUILD_ID | awk -F":" '{print $2}')
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
      - echo Writing image definitions file...
      # - printf '[{"name":"sample-website","imageURI":"%s"}]' $REPOSITORY_URI:$IMAGE_TAG > imageDetail.json
      - printf '{"ImageURI":"%s"}' $REPOSITORY_URI:$IMAGE_TAG > imageDetail.json

artifacts:
  files:
    - imageDetail.json
```

### 2.지속적 전달 파이프라인 생성

### 3.블루/그린 배포를 지원하도록 클러스터 준비

taskdef.json

```json
{ 
   "executionRoleArn":"arn:aws:iam::000000000000:role/ecsTaskExecutionRole",
   "containerDefinitions":[ 
      { 
         "name":"my-webapp",
         "image":"my-webapp-repo:latest",
         "essential":true,
         "portMappings":[ 
            { 
               "hostPort":80,
               "protocol":"tcp",
               "containerPort":80
            }
         ]
      }
   ],
   "requiresCompatibilities":[ 
      "EC2",
      "FARGATE"
   ],
   "networkMode":"awsvpc",
   "cpu":"256",
   "memory":"512",
   "family":"my-webapp"
}
```

### 4.블루/그린 배포 구성

### 5.CodePipeline 자동화 테스트

---

Reference

파이프라인의 다른 AWS 계정에서 리소스 사용
- http://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create-cross-account.html

AWS CodePipeline과 Jenkins 통합
- https://wiki.jenkins.io/display/JENKINS/AWS+CodePipeline+Plugin 
# appspec.yml

AppSpec 파일 구조
- appspec'파일'섹션(EC2/온프레미스 배포만 가능)
- appspec'리소스'섹션(Amazon ECS and AWS Lambda 배포만 가능)
- appspec'권한'섹셕(EC2/온프레미스 배포만 가능)
- appspec'후크'섹션

```yaml
files:
  - source: source-file-location
    destination: destination-file-location

resources:
  - name-of-function-to-deploy:
      type: "AWS::Lambda::Function" # 람다에 대한 부분
      properties:
        name: name-of-lambda-function-to-deploy
        alias: alias-of-lambda-function-to-deploy
        currentversion: version-of-the-lambda-function-traffic-currently-points-to
        targetversion: version-of-the-lambda-function-to-shift-traffic-to

resources:
  - TargetService:
      Type: AWS::ECS::Service # ECS에 대한 부분
      Properties:
        TaskDefinition: "task-definition-ARN"
        LoadBalancerInfo: 
          ContainerName: "ECS-container-name-for-your-ECS-application" 
          ContainerPort: port-used-by-your-ECS-application
# Optional properties
      PlatformVersion: "ecs-service-platform-version"
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: ["ecs-subnet-1","ecs-subnet-n"] 
          SecurityGroups: ["ecs-security-group-1","ecs-security-group-n"] 
          AssignPublicIp: "ENABLED-or-DISABLED"

permissions:
  - object: object-specification
    pattern: pattern-specification
    except: exception-specification
    owner: owner-account-name
    group: group-name
    mode: mode-specification
    acls: 
      - acls-specification 
    context:
      user: user-specification
      type: type-specification
      range: range-specification
    type:
      - object-type

hooks:
  - BeforeInstall: "BeforeInstallHookFunctionName"
  - AfterInstall: "AfterInstallHookFunctionName"
  - AfterAllowTestTraffic: "AfterAllowTestTrafficHookFunctionName"
  - BeforeAllowTraffic: "BeforeAllowTrafficHookFunctionName"
  - AfterAllowTraffic: "AfterAllowTrafficHookFunctionName"
```

Example

```yaml
os: windows
files:
  - source: Heartbeat.dll
    destination: c:\HeartbeatService
  - source: HeartbeatService.exe
    destination: c:\HeartbeatService
  - source: HeartbeatService.exe.config
    destination: c:\HeartbeatService
  - source: log4net.dll
    destination: c:\HeartbeatService
  - source: Logger.dll
    destination: c:\HeartbeatService
  - source: wintail.exe
    destination: c:\temp

hooks:
  ApplicationStop:
    - location: uninstall.ps1
      timeout: 30
  AfterInstall:
    - location: install.ps1
      timeout: 30
    - location: copywintail.ps1
      timeout: 30
```

- 각 소스 파일에 대한 개략적 설명하고 파일을 저장해야 하는 대상 EC2 인스턴스의 대상을 지정

---

 # 작업: 5 AWS CodeDeploy를 사용하여 배포 번들을 Amazon S3로 푸시

파일을 번들링

 ```bash
 aws deploy push --application-name CodeDeploy-Demo --source HeartBeat-App \
    --s3-location s3://heartbeat-codedeploy-artifacts-[your-initials]-[your-zip-code]/HeartBeat-App.zip
 ```

 S3로 푸시

 ```
 aws deploy create-deployment --application-name CodeDeploy-Demo \
    --deployment-group-name HeartBeat-Deployment --deployment-config-name CodeDeployDefault.AllAtOnce \
    --description "Initial Deployment" \
    --s3-location bucket=heartbeat-codedeploy-artifacts-[your-initials]-[your-zip-code],key=HeartBeat-App.zip,bundleType=zip
```
# appspec.yml

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

---

- 각 소스 파일에 대한 개략적 설명하고 파일을 저장해야 하는 대상 EC2 인스턴스의 대상을 지정

 # 작업: 5 AWS CodeDeploy를 사용하여 배포 번들을 Amazon S3로 푸시

 ```bash
 aws deploy push --application-name CodeDeploy-Demo --source HeartBeat-App \
    --s3-location s3://heartbeat-codedeploy-artifacts-[your-initials]-[your-zip-code]/HeartBeat-App.zip
 ```
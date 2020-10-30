# Module 4 Overview: CI/CD with Development Tools

CI/CD pipeline and dev tools, Part 1 
Lab 2: Deploy an application to an EC2 fleet using AWS CodeDeploy 
----------Day 1/Day 2 Split----------
CI/CD pipeline and dev tools, Part 2 
Lab 3: Automating code deployments using AWS CodePipeline 

---

References

- CodePipeline
  https://wiki.jenkins.io/display/JENKINS/AWS+CodePipeline+Plugin
- EC2 Plugin
  https://wiki.jenkins.io/display/JENKINS/Amazon+EC2+Plugin
- CodeBuild
  https://wiki.jenkins.io/display/JENKINS/AWS+CodeBuild+Plugin


---

실습 2: AWS CodeDeploy를 사용하여 EC2 플릿에 애플리케이션 배포

appspec.yml

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


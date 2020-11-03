# Module 10 overview: Security Automation

This module is intended to bring to the forefront the security aspect in a DevOps practice. 
The slides explain how we should be implementing security at different stages in the CI/CD pipeline. 
The module breaks down into the following sections:

- Introduction to DevSecOps
- Security of the pipeline
- Security in the pipeline
- Threat detection tools

---

IAM policy example

다음은 사용자가 us-west-2 리전의 MyFirstPipeline이라는 파이프 라인에서 모든 단계 전환을 활성화 및 비활성화 할 수 있도록 허용하는 권한 정책의 예를 보여줍니다.

```json
{
  "Version": "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "codepipeline:EnableStageTransition",
        "codepipeline:DisableStageTransition"
      ],
      "Resource" : [
        "arn:aws:codepipeline:us-west-2:111222333444:MyFirstPipeline"
      ]
    }
  ]
}
```

아래 예제는 키 값이 Production 인 키 환경으로 태그가 지정된 프로젝트에서 언급 된 작업 목록을 거부합니다. 사용자의 관리자는 권한없는 IAM 사용자에게 관리 형 사용자 정책과 함께이 IAM 정책을 연결해야합니다. aws : ResourceTag 조건 키는 태그를 기반으로 리소스에 대한 액세스를 제어하는 ​​데 사용됩니다

```json
{ 
    "Version":"2012-10-17",
    "Statement":[ 
       { 
          "Effect":"Deny",
          "Action":[ 
             "codebuild:CreateProject",
             "codebuild:UpdateProject",
             "codebuild:DeleteProject"
          ],
          "Resource":"*",
          "Condition":{ 
             "ForAnyValue:StringEquals":{ 
                "aws:RequestTag/Environment":"Production"
             }
          }
```

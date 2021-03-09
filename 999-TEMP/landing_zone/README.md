# Landing Zone (Control Tower)

2021-03-09 ~ 2021-03-10

Landing Zone 

1.AWS계정과 google 계정 or 4개의 개인 이메일이 필요
2.CloudFormation에서 Template을 실행하여 생성
[[CodePipeline]]
3.Source Stage 
    - CodePipeline에서 S3에 파일을 수정하여 다시 업로드
4.Build Stage 진행

5.Core Accounts Stage
    [LandingZoneStateMachineTriggerLambda -> StateMachine -> ]
    - Organization (security)이 만들어짐



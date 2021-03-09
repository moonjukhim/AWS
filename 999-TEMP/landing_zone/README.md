# Landing Zone (Control Tower)

2021-03-09 ~ 2021-03-10

Landing Zone 

1.AWS계정과 google 계정 or 4개의 개인 이메일이 필요
2.CloudFormation에서 Template을 실행하여 생성

[[CodePipeline]]
1.Source Stage 
    - CodePipeline에서 S3에 파일을 수정하여 다시 업로드
2.Build Stage 진행

3.Core Accounts Stage (약25분 정도 소요)
    [LandingZoneStateMachineTriggerLambda -> StateMachine -> ]
    - Organization 이 만들어짐
    - SCP가 만들어지지만 이를 나중에 enable 시킬 것임

4.SCP Stage(Policy)
    - SCP를 enable되고
    - Service control policy에 2개의 Policy가 생성이 됨
      - 절대 삭제하면 안됨

5.Core Resource Stage
    - CoreStackSet이 생성


# Landing Zone (Control Tower)

2021-03-09 ~ 2021-03-10


[[prerequisite]]
1.AWS계정과 google 계정 or 4개의 개인 이메일이 필요
2.CloudFormation에서 Template을 실행하여 생성


[[CodePipeline]]
1.Source Stage 
    - CodePipeline에서 S3에 파일을 수정하여 다시 업로드
2.Build Stage 진행

3.Core Accounts Stage (약 25분 정도 소요)
    [LandingZoneStateMachineTriggerLambda -> StateMachine -> ]
    - Organization 이 만들어짐
    - SCP가 만들어지지만 이를 나중에 enable 시킬 것임

4.SCP Stage(Policy)
    - SCP를 enable되고
    - Service control policy에 2개의 Policy가 생성이 됨
      - 절대 삭제하면 안됨

5.Core Resource Stage (약 10분 정도 소요)
    - CoreStackSet이 생성
    - 3개의 account가 만들어졌는데, 각 account의 핵심 기능이 여기서 빌드
      - GuardDuty의 기능이 생성
      - Log는 로깅되는 리소스가 생성
      - Shared는 VPC가 생성
    - 3개 계정에 대한 접속을 하려면 패스워드 찾기를 해야 하나
    - 여기서는 SSO로 활성화 해서 쉽게 접속하도록 할 것임

    Baseline과 Core가 있는데 두 개의 template을 보면 어떤 작업을 하는지 알 수 있음



# Landing Zone (Control Tower) 

### 교육일자 : 2021-03-09 ~ 2021-03-10

멀티계정의 환경을 손쉽게 배포하고 관리하기 위한 서비스

---

# Day1

[[prerequisite]]
1.AWS계정과 google 계정 or 4개의 개인 이메일이 필요
2.CloudFormation에서 Template을 실행하여 생성
    - https://s3.amazonaws.com/solutions-reference/aws-landing-zone/v2.4.2/aws-landing-zone-initiation.template
    - 2AZ를 사용하면 주로 A,C를 사용
    - 3AZ를 사용하면 랜덤하게 AZ를 선택
    - 고객사마다 적절한 서비스 마다 적절한 권한에 대한 설정이 필요할 수 있음 
    - root 계정으로 landingzone 서비스를 생성하면 안되고,
    - 별도의 user를 생성해서 작업하는 것을 권장함
    - CodePipeline에서 자동 생성을 enable 하지 않았으므로
    - S3 Template 파일을 이름 앞에 "_"를 붙임.
    - root는 다운로드가 되지 않으므로 별도 생성한 user를 KMS의 권한을 부여하고
    - user로 접속하여 템플릿 파일들을 다운로드 받습니다.


[[CodePipeline]]
1. Source Stage 
    - CodePipeline에서 S3에 파일을 수정하여 다시 업로드
2. Build Stage 진행

3. Core Accounts Stage (약 25분 정도 소요)
    [LandingZoneStateMachineTriggerLambda -> StateMachine -> ]
    - Organization 이 만들어짐 
    - Organization State Machine
    - SCP가 만들어지지만 이를 나중에 enable 시킬 것임

4. SCP Stage(Policy)
    - SCP를 enable되고
    - Service control policy에 2개의 Policy가 생성이 됨
      - 절대 삭제하면 안됨
    - SCP State Machine

5. Core Resource Stage (약 10분 정도 소요)
    - CoreStackSet이 생성
    - 3개의 account가 만들어졌는데, 각 account의 핵심 기능이 여기서 빌드
      - GuardDuty의 기능이 생성
      - Log는 로깅되는 리소스가 생성
      - Shared는 VPC가 생성
    - 3개 계정에 대한 접속을 하려면 패스워드 찾기를 해야 하나
    - 여기서는 SSO로 활성화 해서 쉽게 접속하도록 할 것임

    Baseline과 Core가 있는데 두 개의 template을 보면 어떤 작업을 하는지 알 수 있음

6. Service Catalog Stage
    - AVM이 생성
    - LandingZoneServiceCatalogStateMachine 이 수행

7. Baseline Resource Stage (약 27분 정도 소요)
    - Baseline resource stackset이 생성
    - CodeBuild가 사용됨
    - Baseline의 대부분의 리소스가 여기서 생성되므로 시간이 상당히 소요

8. Launch AVM Stage (약 20분 정도 소요)
    - CodeBuild로 실행됨
    - python3 launch_avm.py $log_level $wait_time $current/manifest.yaml $sm_arn_launch_avm $batch_size
    - StackSet 화 한 내용을 각 계정에 배포하고 있음

Ref. Deployment Time

[[SSO]]

--- 

# Day2 
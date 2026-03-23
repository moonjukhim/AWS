# Lab 진행시 유의사항

### 5. 서버리스 아키텍처 구축

    - 7번에서 반드시 Standard 선택
    - 48번에 바꿔야 하는 값은 여러개입니다.
        - **SNS_TOPIC_ARN**
        - **SNS_TOPIC_OWNER**
    - 64 : Use an existing role -> Use another role 로 변경되었음


### 6. Amazon S3 오리진으로 Amazon CloudFront 배포 구성

    - 랩을 진행할 때 반드시 경로를 잘 확인해야 합니다.
    
    - 36 bucket poliy에 변경해줘야 하는 ARN이 한 개 입니다.
        - 뒤에 **/\*** 가 붙어 있어야 합니다.


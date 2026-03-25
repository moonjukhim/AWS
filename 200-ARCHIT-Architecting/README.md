#### 200-ARCHIT-Architecting-on-AWS

1. Architecture Fundamentals
2. Account Security
3. Networking 1
4. Compute
5. Storage
6. Database Services
7. Monitoring and Scaling
8. Automation
9. Containers
10. Networking 2
11. Serverless
12. Edge Services
13. Backup and Recovery

---

### References

##### Solution Libraries

- [aws-solutions-library-samples](https://github.com/aws-solutions-library-samples)
- [AWS Solutions Library](https://aws.amazon.com/solutions/)

---

# Lab 진행시 유의사항 : 2026-03-23

### 2. Amazon VPC 인프라 구축

    - 52 : Amazon Linux 2023 kernel-6.1 AMI로 보임
    - 73 : HTTPS가 아니라 HTTP 이어야 합니다.

### 3. Amazon VPC 인프라에 데이터베이스 계층 생성

    - 9번을 진행하기 전에 Cluster scalability type에서 Provisioned로 선택**(UI가 바뀜)**
        - 10번까지 연결되는 내용
    - 16번의 Encryption 섹션에 Enable encryption 메뉴는 없어졌음.
    - 50번의 작업은 2~30분 정도 소요됩니다.
        - 뒤에 4번째 랩을 진행하기 전에 Relica가 만들어진 것을 확인하고 4번 랩을 진행합니다.

### 4. Amazon VPC에서 고가용성 구성

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

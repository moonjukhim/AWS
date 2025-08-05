1. 마이그레이션 시나리오

   - 온프레미스 → AWS 전환
   - 요구사항: 최소 다운타임, 비용 최적화, 성능 유지
   - 자주 등장하는 옵션: AWS Snowball, DMS, S3 Transfer Acceleration

2. 하이브리드 아키텍처 구성

    - VPN, Direct Connect, Route 53, PrivateLink 조합
    - 요구사항: 보안, 가용성, 네트워크 지연 최소화

3. Serverless 아키텍처 선택

    - Lambda, API Gateway, EventBridge, DynamoDB 등을 중심으로
    - 조건: 운영 복잡성 감소, 탄력적 스케일링, 비용 절감

4. 보안 및 인증 구성

    IAM, KMS, SSO, SCP, 조건부 정책

    조건: least privilege 원칙, 특정 사용자 제한, 데이터 암호화

5. 멀티 계정 / 조직 기반 시나리오

    AWS Organizations, SCP, RAM, Account Boundary 정책

    요구사항: 분리된 책임 모델, 비용 통제, 정책 적용 범위 이해 필요

6. 고가용성 및 장애 복구 설계

    AZ/Region 레벨의 HA 구성

    Auto Scaling, Multi-AZ RDS, Route 53 Failover, S3 CRR 등 사용

7. 스토리지 최적화 시나리오

    S3, EBS, EFS, FSx, Glacier 간의 비용/성능/가용성 트레이드오프 비교

    액세스 패턴 기반으로 Storage Class 선택

8. CI/CD 및 자동화

    CodePipeline, CodeDeploy, CloudFormation, CDK, Terraform

    요구사항: 롤백 전략, Canary 배포, Infra as Code 적용

9. 컨테이너 및 마이크로서비스 설계

    ECS vs EKS vs Lambda 비교

    요구사항: 운영 단순화, 자동 확장, 환경 분리

10. 모니터링 및 로깅 전략

    CloudWatch, X-Ray, CloudTrail, AWS Config

    조건: 이상 탐지, 규정 준수, 감사 로그 보존
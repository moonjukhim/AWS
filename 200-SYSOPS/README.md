## 5.x

1. Introduction to Cloud Operations on AWS
2. Access Management
3. System Discovery (lab1: System Manager & Config)
4. Deploy and Update Resources
5. Automate Resource Deployment (lab2: IaC)
6. Manage Resources (lab3: OaC)
7. Configure Highly Available Systems
8. Automate Scaling
9. Monitor and Maintain System Health (lab4: Monitoring Apps and Infra)
10. Data Security and System Auditing
11. Operate Secure and Resilient Networks
12. Mountable Storage (lab5: AWS Backup)
13. Object Storage
14. Cost Reporting, Alerts and Optimization

---

1. Introduction

   - SLI/SLO/SLA 소개
   - 체크리스트
     - SRE vs DevOps
     - SLO/SLI/SLA 정의
     - MTTR, MTBF, Error Budget 개념
   - 운영 지표 설정 가능한 곳?

2. Access Management

   - IAM
   - 최소권한원칙
   - 체크리스트
     - IAM 정책 자동화
     - Break-glass 계정 관리 방안

3. System Discovery

   - 자산 및 서비스 식별
   - CMDB(Configuration Management DB)
   - 체크리스트
     - 자원 자동 식별 및 태깅
     - 서비스 맵 자동 생성 도구(Config, Datadog)
     - 누락된 시스템에 대한 경고 설정

4. Deploy and Update Resources

   - IaC
   - CI/CD 파이프라인 통합
   - 체크리스트
     - IaC 도구
     - 배포 프로세스
     - Canary/Blue-green 배포

5. Automate Resource Deployment

   - 자동화된 인프라 구축
   - 체크리스트
     - CI/CD와 인프라 프로비저닝 통합
     - DR 환경
     - CloudFormation StackSets

6. Manage Resources

   - 자원 모니터링, 할당, 최적화
   - 체크리스트
     - 자원 사용량 모니터링 (CPU/RAM/Network)
     - 태그 기반 비용 분석
     - 리소스 미사용 감지 및 정리

7. Configure Highly Available Systems

   - 고가용성 구성 설계 (HA)
   - 체크리스트
     - 다중 AZ/Region 배포
     - Auto Healing 구성 여부 (예: ASG, Kubernetes)
     - 헬스 체크 및 장애 조치 정책 구성

---

- 2024-06-22 200-SYSOPS-54

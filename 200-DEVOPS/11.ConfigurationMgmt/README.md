# 모듈 11 개요 : 구성 관리

이 모듈에서는 구성 관리 프로세스, 워크 플로, AWS Config, AWS Systems Manager의 기능 및 AWS OpsWorks (Chef 및 Puppet) 
및 AWS OpsWorks Stacks에 대한 간략한 소개에 대해 학습합니다. 
이 모듈에 새로 추가 된 사항에는 AMI 옵션과 사전 구축 된 AMI가 포함됩니다. 
모듈은 다음 섹션으로 나뉩니다.

- 구성 관리 프로세스 소개
- 구성 관리를위한 AWS 서비스 및 도구
  
---

구성 관리가 필요한 이유는 무엇입니까?

실행중인 웹 서비스에서 웹 서버의 구성 파일을 간단히 변경하여 수정할 수있는 버그를 발견했습니다. 

이 변경 사항을 다운 타임이 거의 또는 전혀없이 플릿에서 현재 실행중인 모든 인스턴스에 어떻게 적용합니까? 
그러한 변경이 이루어진 후 누군가가 실수로 변경하여 알려진 양호한 상태에서 벗어나는 것을 방지하려면 어떻게해야합니까? 


-- Additional Resources

- Snowflake 서버 (Martin Fowler) : https://martinfowler.com/bliki/SnowflakeServer.html 
- AWS CodeStar를 사용한 사용자 지정 AWS Config 규칙 : https://aws.amazon.com/blogs/mt/how-to-create-custom-aws-config-rules-with-aws-codestar/
- 동적 DevOps 환경의 IT 거버넌스 : https://aws.amazon.com/blogs/devops/it-governance-in-a-dynamic-devops-environment/ 
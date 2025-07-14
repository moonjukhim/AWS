# 1. Introduction to Threat Modeling
# 2. Threat Modeling at AWS

Exercises
  - What are we working on?
  - What cloud go wrong?
  - What are we going to do about it?
  - Did we do a good enough job?

## TODO

1. draw.io에서 ["Vehicle Registraion"](./imgs/vehicle_registraion_module.png) 
2. 차량 등록 기능이 어떻게 작동하는지 몇 가지 가정을 작성합니다.

| Label         | Description                                                   |
|---------------|---------------------------------------------------------------|
|WWWO-Assume-1	| REST 기반 API는 AWS Lambda와 Amazon API Gateway에서 제공됩니다.   |
|WWWO-Assume-2  | 모든 사용자가 모든 작업을 수행할 수 있습니다.                       |
|WWWO-Assume-3  | GUID는 무작위적이고 비순차적입니다.                               |
| ...           | ...                                                           |

3. 시스템 요소 그리기/데이터 흐름 그리기


---

[위협 모델링에 접근하는 방법](https://aws.amazon.com/ko/blogs/security/how-to-approach-threat-modeling/)

[SAFECode 전술적 위협 모델링 백서](https://safecode.org/wp-content/uploads/2017/05/SAFECode_TM_Whitepaper.pdf)

[OWASP(Open Web Application Security Project) 위협 모델링 치트 시트](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)

[Threat Modeling for Builders Workshop](https://explore.skillbuilder.aws/learn/course/external/view/elearning/13274/threat-modeling-the-right-way-for-builders-workshop)

---

### Threat Modeling

- Start Here
  - Introduction to Threat Modeling
  - Theat Modeling at AWS
- Section 1
  - Exercise: Create a Data Flow Diagram
- Section 2
  - Threat Grammar
  - Exercise: Find Threats
- Section 3
  - Exercise: Select Risk Response Strategies
- Section 4
  - Exercise: Assess the Usefulness of the Process


---

### threat-composer

https://github.com/awslabs/threat-composer#readme
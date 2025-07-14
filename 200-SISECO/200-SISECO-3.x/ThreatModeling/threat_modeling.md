# 1. Introduction to Threat Modeling
# 2. Threat Modeling at AWS

Exercises
  - What are we working on?
  - What can go wrong?
  - What are we going to do about it?
  - Did we do a good enough job?

--- 

## TODO

##### What are we working on?

1. draw.io에서 ["Vehicle Registraion"](./imgs/vehicle_registraion_module.png) 
2. 차량 등록 기능이 어떻게 작동하는지 몇 가지 가정을 작성합니다.

| Label         | Description                                                   |
|---------------|---------------------------------------------------------------|
|WWWO-Assume-1	| REST 기반 API는 AWS Lambda와 Amazon API Gateway에서 제공됩니다.   |
|WWWO-Assume-2  | 모든 사용자가 모든 작업을 수행할 수 있습니다.                       |
|WWWO-Assume-3  | GUID는 무작위적이고 비순차적입니다.                               |
| ...           | ...                                                           |

3. 시스템 요소 그리기/데이터 흐름 그리기

    [샘플 데이터 흐름](./imgs/system_data_flow_sample.png)

4. 신뢰의 경계 그리기

    [샘플 신뢰의 영역](./imgs/trust_zone_sample.png)

##### What can go wrong?

STRIDE : 여섯 가지 위협 범주로 구성된 약어. 유사한 위협들을 침해하는 보안 속성에 따라 그룹화.

    - 1. Spoofing — Violates authenticity
    - 2. Tampering — Violates integrity
    - 3. Repudiation — Violates non-repudiation
    - 4. Information disclosure — Violates confidentiality
    - 5. Denial of service (DoS) — Violates availability
    - 6. Elevation of privilege (EoP) — Violates authorization

1. STRIDE-per-element

    ![STRIDE](./imgs/STRIDE.png)
    [STRIDE-per-element chart](./imgs/STRIDE-per-element%20chart_NOPROCESS_.png)

2. Threat Grammar

    [threat source] [prerequisites] can [threat action], which leads to [threat impact], negatively impacting [impacted assets].

    [Sample statements](./static/threat_grammar_statements.xlsx)

3. Find Threats

    - [STRIDE-per-element 사용](./imgs/STRIDE-per-element%20chart_NOPROCESS_.png)
    - [State of assumptions xlsx](./static/sheet1-what_are_we_working_on.xlsx)
    - [Threat composer tool](https://awslabs.github.io/threat-composer/?mode=ThreatsOnly)
        - [GitHub repo:](https://github.com/awslabs/threat-composer)
    - [[S] Find spoofing threats to external entities](./imgs/1_spoofing.jpg)
    - [[T] Find tampering threats to data stores](./imgs/2_tampering.jpg)
    - [[R] Find repudiation threats to external entities](./imgs/3_repudiation.jpg)
    - [[I] Find information disclosure threats to processes](./imgs/4_info_disclosure.jpg)
    - [[D] Find denial of service (DoS) threats to data stores](./imgs/5_dos.jpg)
    - [[E] Find elevation of privilege (EoP) threats to processes](./imgs/6_eop.jpg)
    - [우선순위 결정](./imgs/7_priorities.jpg)



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
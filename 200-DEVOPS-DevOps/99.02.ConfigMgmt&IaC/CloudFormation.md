# 자동화 : 인프라 자동화 & 구성관리 자동화

---

# 1.인프라 자동화

# CloudFormation

Building Blocks

- AWSTemplateFormatVersion : CloudFormation 템플릿 버전
- Description : 설명
- Parameter :  템플릿 입력 변수
- Mappings : 정적 변수, 키-값 페어
- Conditions : 특정 리소스의 생성 또는 업데이트 여부와 시기를 제어
- Transform : 사용할 AWS SAM 버전을 지정
- Resources(mandatory) : 사용자 지정 리소스 값(URL, 사용자 이름 등)
- Outputs : 템플릿에서 생성하는 사용자 지정 리소스 값

```yaml
---
AWSTemplateFormatVersion: "2020-01-09"

Description: 
    String

Parameters:
    set of parameters

Mappings: 
    set of mappings

Conditions: 
    set of conditions

Transform: 
    set of transform

Resources: 
    set of resources

Outputs:
    set of outputs
```

---

# 
```bash
aws cloudformation create-stack --stack-name myteststack --template-body file:///home/testuser/mytemplate.json --parameters ParameterKey=Parm1,ParameterValue=test1 ParameterKey=Parm2,ParameterValue=test2
{
  "StackId" : "arn:aws:cloudformation:us-west-2:123456789012:stack/myteststack/330b0120-1771-11e4-af37-50ba1b98bea6"
}
```

---

- Intrinsic Functions
- 헬퍼 함수{cfn-init, cfn-hup, cfn-get-metadata, cfn-signal}
- Nested Stack
- Stack Policy
- Custom Resources
- Drift Detection
# 자동화 : 인프라 자동화 & 구성관리 자동화

---

# 1.인프라 자동화

# CloudFormation

Building Blocks

- Resources(mandatory) : 사용자 지정 리소스 값(URL, 사용자 이름 등)
- Parameter
- Mappings
- Outputs
- Conditionals
- Metadata

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


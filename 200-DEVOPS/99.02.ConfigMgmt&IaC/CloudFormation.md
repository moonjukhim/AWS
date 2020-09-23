# 자동화 : 인프라 자동화 & 구성관리 자동화

---

# 1.인프라 자동화

CloudFormation

Building Blocks

- Resources
- Parameter
- Mappings
- Outputs
- Conditionals
- Metadata
   
---

# 
```bash
aws cloudformation create-stack --stack-name myteststack --template-body file:///home/testuser/mytemplate.json --parameters ParameterKey=Parm1,ParameterValue=test1 ParameterKey=Parm2,ParameterValue=test2
{
  "StackId" : "arn:aws:cloudformation:us-west-2:123456789012:stack/myteststack/330b0120-1771-11e4-af37-50ba1b98bea6"
}
```


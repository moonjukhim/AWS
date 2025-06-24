```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: ''
Resources:
  IamRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: Ec2RoleForSSM
      Description: EC2 IAM role for SSM access
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - ec2.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
  Ec2InstanceProfile:
    Type: 'AWS::IAM::InstanceProfile'
    Properties:
      InstanceProfileName: Ec2RoleForSSM
      Roles:
        - Ref: IamRole
Parameters: {}
Metadata: {}
Conditions: {}
```
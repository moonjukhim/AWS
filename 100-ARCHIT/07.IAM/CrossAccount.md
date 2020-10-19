# Cross Account(교차 계정)

[AWS account ID] <-- 계정 ID 값을 기억합니다

--- 

## Task1.역할 생성

  NetworkAdmin 역할 생성
    - VPCFullAccess 정책을 부여

## Task2.사용자 생성

  - iamtest
    - 인라인 정책 지정

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::702995877146:role/NetworkAdmin"
        }
    ]
}
```

## Task3.사용자로 로그인 하여 권한 확인
  - https://[ACCOUNT ALIAS]].signin.aws.amazon.com/console
  부여된 권한이 없기 때문에 어떠한 작업도 수행할 수 없습니다.

## Task4.역할 전환

## Task5.Role이 위임됐는지 확인

---

# AWS CLI를 사용하여 IAM 역할을 위임(참고)
https://aws.amazon.com/ko/premiumsupport/knowledge-center/iam-assume-role-cli/

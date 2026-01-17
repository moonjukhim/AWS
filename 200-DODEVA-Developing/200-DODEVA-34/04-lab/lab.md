1. 사용중인 자격 증명 확인

```bash
aws sts get-caller-identity

# Output
{
    "UserId": "AROA3IBQZWZS7IOLI6SZE:i-0143c8169c68331a3",
    "Account": "123456789101",
    "Arn": "arn:aws:sts::123456789101:assumed-role/Exam-Role/i-0143c8169c68331a3"
}
```

2. [역할에 대한 최대 세션 기간 설정 보기](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles_use.html#id_roles_use_view-role-max-session)

역할의 최대 세션 기간 설정 확인(AWS CLI)

```bash
aws iam list-roles
aws iam get-role
```
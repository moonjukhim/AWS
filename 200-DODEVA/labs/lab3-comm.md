
```bash
# Java
aws dynamodb create-table ^
  --table-name Notes ^
  --attribute-definitions AttributeName=UserId,AttributeType=S AttributeName=NoteId,AttributeType=N ^
  --key-schema AttributeName=UserId,KeyType=HASH AttributeName=NoteId,KeyType=RANGE ^
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

aws dynamodb wait table-exists --table-name Notes

aws dynamodb describe-table --table-name Notes | findstr TableStatus
```
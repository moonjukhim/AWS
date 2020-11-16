```bash
aws ssm send-command --targets Key=tag:SecurityScan,Values=true \
--document-name "AmazonInspector-ManageAWSAgent" \
--query Command.CommandId \
--output-s3-bucket-name <LogBucket>
```

Inspector 에이전트가 성공적으로 설치되었는지 확인

```bash
aws ssm list-command-invocations --details \
--query "CommandInvocations[*].[InstanceId,DocumentName,Status]" \
--command-id <CommandId>
```

## 과제4: 패치 기준선 생성 및 적용

### 서브넷 별 탑재 대상 생성

```bash
subnets=($(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=EksPublic*" | jq --raw-output '.Subnets[].SubnetId'))
for subnet in ${subnets[@]}
do
    echo "creating mount target in " $subnet
    aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $subnet --security-groups $MOUNT_TARGET_GROUP_ID
done
```

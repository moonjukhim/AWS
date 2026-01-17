1.

2.  VPC ID 확인

```bash
VPC=$(aws ec2 describe-vpcs --query 'Vpcs[*].VpcId' --filters 'Name=tag:Name, Values=labVPC' | jq -r '.[0]')
echo $VPC
```

3. 라우팅 데이트 ID 확인

```bash
RTB=$(aws ec2 describe-route-tables --query 'RouteTables[*].RouteTableId' --filters 'Name=tag:Name, Values=PrivateRouteTable' | jq -r '.[0]')
echo $RTB
```

3. 리전 정보 확인

```bash
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
echo $AWS_REGION
```

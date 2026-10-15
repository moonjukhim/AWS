### Task1

```bash
sudo yum install gettext -y

export awsAccount=`aws sts get-caller-identity --query "Account" --output text` && echo export awsAccount=$awsAccount >> ~/.bashrc

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
export awsRegion=`curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/placement/region` && echo export awsRegion=$awsRegion >> ~/.bashrc

export VPC=`aws ec2 describe-vpcs --filters Name=tag:Name,Values=wa-lab-vpc --query 'Vpcs[*].VpcId' --output text --region $awsRegion` && echo export VPC=$VPC >> ~/.bashrc

export awsAZ1=`aws ec2 describe-availability-zones --region $awsRegion --query 'AvailabilityZones[].ZoneName[]|[0]' --output text` && echo export awsAZ1=$awsAZ1 >> ~/.bashrc

export awsAZ2=`aws ec2 describe-availability-zones --region $awsRegion --query 'AvailabilityZones[].ZoneName[]|[1]' --output text` && echo export awsAZ2=$awsAZ2 >> ~/.bashrc

aws ec2 create-subnet --vpc-id $VPC --cidr-block "10.100.2.0/24" --availability-zone $awsAZ2 --tag-specifications 'ResourceType=subnet, Tags=[{Key=Name,Value=wa-public-subnet-2}]' --region $awsRegion

#
aws ec2 create-subnet --vpc-id $VPC --cidr-block "10.100.3.0/24" --availability-zone $awsAZ2 --tag-specifications 'ResourceType=subnet, Tags=[{Key=Name,Value=wa-private-subnet-2}]' --region $awsRegion

export publicSubnetId=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-public-subnet-2 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export publicSubnetId=$publicSubnetId >> ~/.bashrc

export privateSubnetId=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-private-subnet-2 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export privateSubnetId=$privateSubnetId >> ~/.bashrc

export publicRt=`aws ec2 describe-route-tables --filters Name=tag:Name,Values=wa-public-rt --query 'RouteTables[*].RouteTableId' --output text --region $awsRegion` && echo export publicRt=$publicRt >> ~/.bashrc

export privateRt=`aws ec2 describe-route-tables --filters Name=tag:Name,Values=wa-private-rt --query 'RouteTables[*].RouteTableId' --output text --region $awsRegion` && echo export privateRt=$privateRt >> ~/.bashrc

aws ec2 associate-route-table --subnet-id $publicSubnetId --route-table-id $publicRt --region $awsRegion

aws ec2 associate-route-table --subnet-id $privateSubnetId --route-table-id $privateRt --region $awsRegion
```

### Task2

```bash
aws ec2 create-subnet --vpc-id $VPC --cidr-block "10.100.4.0/24" --availability-zone $awsAZ1 --tag-specifications 'ResourceType=subnet, Tags=[{Key=Name,Value=wa-rds-subnet-1}]' --region $awsRegion

aws ec2 create-subnet --vpc-id $VPC --cidr-block "10.100.5.0/24" --availability-zone $awsAZ2 --tag-specifications 'ResourceType=subnet, Tags=[{Key=Name,Value=wa-rds-subnet-2}]' --region $awsRegion

export rdsSubnet1Id=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-rds-subnet-1 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export rdsSubnet1Id=$rdsSubnet1Id >> ~/.bashrc

export rdsSubnet2Id=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-rds-subnet-2 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export rdsSubnet2Id=$rdsSubnet2Id >> ~/.bashrc

aws ec2 associate-route-table --subnet-id $rdsSubnet1Id --route-table-id $privateRt --region $awsRegion

aws ec2 associate-route-table --subnet-id $rdsSubnet2Id --route-table-id $privateRt --region $awsRegion

aws rds create-db-subnet-group --db-subnet-group-name "wa-rds-subnet-group" --db-subnet-group-description "WA RDS Subnet Group" --subnet-ids $rdsSubnet1Id $rdsSubnet2Id --region $awsRegion

aws rds create-db-subnet-group --db-subnet-group-name "wa-rds-subnet-group" --db-subnet-group-description "WA RDS Subnet Group" --subnet-ids $rdsSubnet1Id $rdsSubnet2Id --region $awsRegion

export rdsSg=`aws ec2 describe-security-groups --filters Name=group-name,Values=wa-rds-sg --query 'SecurityGroups[*].GroupId' --output text --region $awsRegion` && echo export rdsSg=$rdsSg >> ~/.bashrc

export ec2DbSg=`aws ec2 describe-security-groups --filters Name=group-name,Values=wa-database-sg --query 'SecurityGroups[*].GroupId' --output text --region $awsRegion` && echo export ec2DbSg=$ec2DbSg >> ~/.bashrc

aws ec2 authorize-security-group-ingress --group-id $rdsSg --source-group $ec2DbSg --protocol "tcp" --port "3306" --region $awsRegion

aws rds create-db-instance --db-name "WaRdsDb" --db-instance-identifier "wadbinstance" --allocated-storage 20 --db-instance-class db.t3.micro --engine "mariadb" --master-username "mainuser" --master-user-password "WaStr0ngP4ssw0rd" --vpc-security-group-ids $rdsSg --db-subnet-group-name "wa-rds-subnet-group" --db-parameter-group-name "wa-mariadb-params" --multi-az --no-publicly-accessible --backup-retention-period 0 --region $awsRegion
```

### Task3

```bash
aws rds describe-db-instances --db-instance-identifier "wadbinstance" --query 'DBInstances[*].Endpoint.Address' --output text --region $awsRegion
```

```bash
aws ssm get-parameters --names "DbPrivateDns" --region $awsRegion --output table

export rdsEndPoint=`aws rds describe-db-instances --db-instance-identifier "wadbinstance" --query 'DBInstances[*].Endpoint.Address' --output text --region $awsRegion` && echo export rdsEndPoint=$rdsEndPoint >> ~/.bashrc

aws ssm put-parameter --name "DbPrivateDns" --value $rdsEndPoint --overwrite --region $awsRegion

aws ssm get-parameters --names "DbPrivateDns" --output table --region $awsRegion
```

### Task4

```bash
export VPC=`aws ec2 describe-vpcs --filters Name=tag:Name,Values=wa-lab-vpc --query 'Vpcs[*].VpcId' --output text --region $awsRegion` && echo export VPC=$VPC >> ~/.bashrc

aws ec2 create-security-group --description "ALB Security group" --group-name "wa-alb-sg" --vpc-id $VPC --region $awsRegion

export albSg=`aws ec2 describe-security-groups --filters Name=group-name,Values=wa-alb-sg --query 'SecurityGroups[*].GroupId' --output text --region $awsRegion` && echo export albSg=$albSg >> ~/.bashrc

aws ec2 authorize-security-group-ingress --group-id $albSg --protocol "tcp" --port "80" --cidr "0.0.0.0/0" --region $awsRegion

export albSubnet1Id=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-public-subnet-1 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export albSubnet1Id=$albSubnet1Id >> ~/.bashrc

export albSubnet2Id=`aws ec2 describe-subnets --filters Name=tag:Name,Values=wa-public-subnet-2 --query 'Subnets[*].SubnetId' --output text --region $awsRegion` && echo export albSubnet2Id=$albSubnet2Id >> ~/.bashrc

aws elbv2 create-load-balancer --name "waAlb" --subnets $albSubnet1Id $albSubnet2Id --security-groups $albSg --type "application" --region $awsRegion

aws elbv2 create-target-group --name "waAutoscale-tg" --protocol "HTTP" --port 80 --vpc-id $VPC --target-type "instance" --region $awsRegion


export waTg=`aws elbv2 describe-target-groups --names waAutoscale-tg --query 'TargetGroups[*].TargetGroupArn' --output text --region $awsRegion` && echo export waTg=$waTg >> ~/.bashrc

export albArn=`aws elbv2 describe-load-balancers --names waAlb --query 'LoadBalancers[*].LoadBalancerArn' --output text --region $awsRegion` && echo export albArn=$albArn >> ~/.bashrc
```

```bash
cd ~
wget https://aws-tc-largeobjects.s3-us-west-2.amazonaws.com/ILT-TF-200-CSAWAF-10-EN/listener-source.json


envsubst < "listener-source.json" > "listener.json"

aws elbv2 create-listener --load-balancer-arn $albArn --protocol "HTTP" --port 80 --default-actions file://listener.json --region $awsRegion
```

### Task 5

```bash
aws rds describe-db-instances --db-instance-identifier "wadbinstance" --query 'DBInstances[*].{DB_Identifier:DBInstanceIdentifier,Status:DBInstanceStatus}' --output table --region $awsRegion
```

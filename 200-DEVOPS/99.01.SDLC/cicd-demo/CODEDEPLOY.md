CodeDeploy :

배포 가능한 컴퓨팅
- EC2/On-premises
- AWS Lambda
- Amazon ECS

---

# Installing the CodeDeploy agent on EC2
```
sudo yum update -y
sudo yum install -y ruby wget
wget https://aws-codedeploy-eu-west-1.s3.eu-west-1.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto
sudo service codedeploy-agent status
```


# create a bucket and enable versioning
```
aws s3 mb s3://aws-devops-course-henry --region ap-northeast-2
aws s3api put-bucket-versioning --bucket aws-devops-course-henry --versioning-configuration Status=Enabled \
    --region ap-northeast-2
```

# deploy the files into S3
```
aws deploy push --application-name CodeDeployDemo \
    --s3-location s3://aws-devops-course-henry/codedeploy-demo/app.zip --ignore-hidden-files \
    --region ap-northeast-2
```
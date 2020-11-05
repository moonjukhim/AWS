# Packer를 이용하여 AMI 생성

packer template.json

```json
{
    "builders": [{
        "ami_name": "packer-example",
        "instance_type": "t2.micro",
        "region": "us-east-2",
        "type": "amazon-ebs",
        "source_ami": "ami-0c55b159cbfafe1f0",
        "ssh_username": "ubuntu"
    }],
    "provisioners": [{
        "type": "shell",
        "inline": [
        "sudo apt-get update",
        "sudo apt-get install -y php apache2",
        "sudo git clone https://github.com/brikis98/php-app.git /var/www/html/app"
    ],
    "environment_vars": [
        "DEBIAN_FRONTEND=noninteractive"
    ]
    }]
}
```

CodeBuild의 buildspec.yml 파일

```yaml
---
version: 0.2

phases:
  pre_build:
    commands:
      - echo "Installing HashiCorp Packer..."
      - curl -qL -o packer.zip https://releases.hashicorp.com/packer/0.12.3/packer_0.12.3_linux_amd64.zip && unzip packer.zip
      - echo "Installing jq..."
      - curl -qL -o jq https://stedolan.github.io/jq/download/linux64/jq && chmod +x ./jq
      - echo "Validating amazon-linux_packer-template.json"
      - ./packer validate amazon-linux_packer-template.json
  build:
    commands:
      ### HashiCorp Packer cannot currently obtain the AWS CodeBuild-assigned role and its credentials
      ### Manually capture and configure the AWS CLI to provide HashiCorp Packer with AWS credentials
      ### More info here: https://github.com/mitchellh/packer/issues/4279
      - echo "Configuring AWS credentials"
      - curl -qL -o aws_credentials.json http://169.254.170.2/$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI > aws_credentials.json
      - aws configure set region $AWS_REGION
      - aws configure set aws_access_key_id `./jq -r '.AccessKeyId' aws_credentials.json`
      - aws configure set aws_secret_access_key `./jq -r '.SecretAccessKey' aws_credentials.json`
      - aws configure set aws_session_token `./jq -r '.Token' aws_credentials.json`
      - echo "Building HashiCorp Packer template, amazon-linux_packer-template.json"
      - ./packer build amazon-linux_packer-template.json
  post_build:
    commands:
      - echo "HashiCorp Packer build completed on `date`"
```
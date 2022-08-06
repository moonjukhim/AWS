#!/bin/bash

# This script installs tools for this lab.

# Install eksctl
#curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
# curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/0.20.0-rc.0/eksctl_Linux_amd64.tar.gz" | tar xz -C /tmp
# sudo mv /tmp/eksctl /usr/local/bin
# eksctl version

# Install kubectl

# sudo curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/kubectl
# sudo chmod +x ./kubectl
# sudo mkdir -p $HOME/bin && sudo cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
# sudo echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
# sudo pip install --upgrade awscli && hash -r
# sudo yum -y install jq gettext bash-completion
# for command in kubectl jq envsubst aws
#     do
#         which $command &>/dev/null && echo "$command in path" || echo "$command NOT FOUND"
#     done

# kubectl completion bash >>  ~/.bash_completion
# . /etc/profile.d/bash_completion.sh
# . ~/.bash_completion
# kubectl version --short

# Install aws-iam-authenticator

# curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/aws-iam-authenticator
# chmod +x ./aws-iam-authenticator
# sudo mkdir -p $HOME/bin && sudo cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin
# echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
# which aws-iam-authenticator

# Create ssh key

#ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""
#aws ec2 import-key-pair --key-name "ekslab" --public-key-material file://~/.ssh/id_rsa.pub


# Udate IAM for kubectl
rm -vf ${HOME}/.aws/credentials
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
test -n "$AWS_REGION" && echo AWS_REGION is "$AWS_REGION" || echo AWS_REGION is not set
echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bash_profile
echo "export AWS_REGION=${AWS_REGION}" | tee -a ~/.bash_profile
aws configure set default.region ${AWS_REGION}
aws configure get default.region
aws sts get-caller-identity --query Arn | grep lab2FargateRole -q && echo "IAM role valid" || echo "IAM role NOT valid"

# Create KMS key
# export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
# echo $AWS_REGION

# aws kms create-alias --alias-name alias/ekstest --target-key-id $(aws kms create-key --query KeyMetadata.Arn --output text)
# export MASTER_ARN=$(aws kms describe-key --key-id alias/ekstest --query KeyMetadata.Arn --output text)
# echo "export MASTER_ARN=${MASTER_ARN}" | tee -a ~/.bash_profile

# Install Helm
# curl -sSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
# helm version --short
# helm repo add stable https://kubernetes-charts.storage.googleapis.com/
# helm search repo stable
# helm completion bash >> ~/.bash_completion
# . /etc/profile.d/bash_completion.sh
# . ~/.bash_completion
# source <(helm completion bash)

# Installl Docker
sudo yum install -y docker git
sudo usermod -a -G docker ssm-user
sudo service docker start
sudo chmod 777 /var/run/docker.sock
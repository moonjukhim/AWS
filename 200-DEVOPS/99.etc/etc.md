# 기타 내용
# Python

1.Python 설치

```bash
sudo yum list installed | grep -i python3
sudo yum install python36
```

2.virtual env 설정

```bash
python3 -m venv my_app/env
source ~/my_app/env/bin/activate
pip install pip --upgrade
pip install boto3
python3
```


3.package import

```python
import boto3
s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
    print(bucket.name)
```


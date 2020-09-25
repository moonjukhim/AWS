# 기타 내용
# Python

---

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

4.deactivate

```bash
deactivate
```


5.로그인할 때 가상 환경을 자동으로 활성화하려면 ~/.bashrc 파일에 추가

```bash
echo "source ${HOME}/my_app/env/bin/activate" >> ${HOME}/.bashrc
```

---

# MariaDB

1.MariaDB 설치



2.DB & Table 생성

3.데이터 임포트

```mysql
LOAD DATA LOCAL INFILE '파일명'
REPLACE
INTO TABLE `mydb`.`target_table`
COLUMNS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
```







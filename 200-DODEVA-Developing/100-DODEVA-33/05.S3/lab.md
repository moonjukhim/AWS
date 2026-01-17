# 1. 개발 환경에 연결

# 2. 애플리케이션 개발
  - s3 리소스 생성

```python
s3 = boto3.resource('s3')
return s3
```

  - s3로부터 다운로드

```python
bucket.download_file(key, key)
```

  - s3에 업로드

```python
bucket.upload_file(filename, key)
```

  - 미리 서명된 url 생성

API를 이용한 pre-signed url 생성
```python
url = s3.meta.client.generate_presigned_url(
        'get_object', Params={'Bucket': bucketname, 'Key': key}, ExpiresIn=900)
return url
```

pre-signed url 생성
1.Role 생성하기(EC2를 신뢰하는 entity로 role 생성)
2.instance profile을 지정하여 EC2인스턴스 생성
3.AWS CLI로 pre-signed url 생성

```bash
aws s3 mb s3://presignedurl-sample-bucket
echo "My First Presigned URL" > test.txt
aws s3 cp test.txt s3://presignedurl-sample-bucket
aws s3 ls s3://presignedurl-sample-bucket

aws s3 presign s3://presignedurl-sample-bucket/test.txt --expires-in 120
```

- 암호화 하여 저장

```python
bucket.upload_file(
        filename, key, ExtraArgs={
            'ServerSideEncryption': 'AES256', 'Metadata': {
                'contact': 'John Doe'}})
```


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

```python
url = s3.meta.client.generate_presigned_url(
        'get_object', Params={'Bucket': bucketname, 'Key': key}, ExpiresIn=900)
return url
```

  - 암호화 하여 저장

```python
bucket.upload_file(
        filename, key, ExtraArgs={
            'ServerSideEncryption': 'AES256', 'Metadata': {
                'contact': 'John Doe'}})
```


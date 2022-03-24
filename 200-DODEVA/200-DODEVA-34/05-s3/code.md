![boto3.aws.s3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#service-resource)

```python
# Create S3 resource
s3 = boto3.resource('s3', config=Config(s3={"addressing_style":"virtual"}))

# Download an S3 object to a file
import boto3
s3 = boto3.resource('s3')
s3.meta.client.download_file('mybucket', 'hello.txt', '/tmp/hello.txt')
```

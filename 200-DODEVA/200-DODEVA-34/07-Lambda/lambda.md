### AWS 기반 개발- 실습 4 - Lambda

1. Python 코드

```python
# boto3 import
import boto3

def lambda_handler(event, context):
    "Process upload event"
    bucket = event['Records'][0]["s3"]["bucket"]["name"]
    key = event['Records'][0]["s3"]["object"]["key"]
    result = "No numbers found in file"
    print("Received event. Bucket: [%s], Key: [%s]" % (bucket, key))

    # construct s3 client
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    # get the object contents
    file_contents = response['Body'].read().decode("utf-8").strip()
    # find matches of all positive or negative numbers
    numbers = [int(n) for n in re.findall(r"-?\d+", file_contents)]
    if numbers:
        # caclulate min/max/average
        mn, mx, avg = min(numbers), max(numbers), sum(numbers)/len(numbers)
        result = "Min: %s Max: %s Average: %s" % (mn, mx, avg)

    print("Result: %s" % result)
    return result

# This is used for debugging, it will only execute when run locally
if __name__ == "__main__":
    # local debugging, send a simulated event
    # TODO 1: Update the event bucket name
    fake_s3_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "REPLACE WITH BUCKET NAME"
                    },
                    "object": {
                        "key": "numbers.txt"
                    }
                }
            }
        ]
    }

    fake_context = []
    lambda_handler(fake_s3_event, fake_context)
```

2. zip 파일로 압축파일 생성
   
3. 압축파일을 사용하여 람다 코드 업로드

```bash
aws lambda update-function-code --function-name PythonCalculator --zip-file fileb://lambda_function.zip
```

4. Test

5. CloudWatch 확인
   
![CloudWatch Log]


# Lambda

## 과제1:개발 환경에 연결

## 과제2:AWS Management Console에서 입력 버킷 생성

## 과제3:Lambda 함수에 대한 실행 역할 생성

## 과제4:AWS Lambda 함수 생성

## 과제5:Lambda 함수 빌드, 패키징 및 배포

5.1 Lambda 함수 테스트

```bash
python lambda_function.py
```

5.2 Lambda 함수 배포

```bash
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name PythonCalculator --zip-file fileb://lambda_function.zip
```



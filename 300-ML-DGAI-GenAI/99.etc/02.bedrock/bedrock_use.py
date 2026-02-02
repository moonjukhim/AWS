import boto3
import json

# Bedrock 클라이언트 생성
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# 모델 ID 및 프롬프트 설정
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
prompt = "생성형 AI에 대해서 설명해줘"

# 요청 생성
native_request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 512,
    "temperature": 0.5,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ],
}

request = json.dumps(native_request)

# Bedrock API 호출
response = client.invoke_model(modelId=model_id, body=request)
model_response = json.loads(response["body"].read())

# 응답 출력
response_text = model_response["content"][0]["text"]
print(response_text)

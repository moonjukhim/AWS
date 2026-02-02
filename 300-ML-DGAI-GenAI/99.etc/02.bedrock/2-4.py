import boto3
from botocore.exceptions import ClientError

# 이미지 생성 작업을 위한 베드락 런타임 클라이언트 생성
client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

image_path = "미리내.jpg"
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()

# 이미지와 이미지 분석 요청 텍스트가 포함된 ContentBlock 작성
user_message = "서문 없이 사진을 분석한 결과를 작성해 주세요."
conversation = [
    {
        "role": "user",
        "content": [
            { "text": user_message },
            {
                "image": {
                    "format": "png",
                    "source": {
                        "bytes": image_bytes
                    }
                }
            }
        ]
    }
]

try:
    response = client.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 4096, "temperature": 0.5, "topP": 0.9},
    )

    response_text = response["output"]["message"]["content"][0]["text"]
    print(response_text)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

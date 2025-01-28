from langchain_aws import BedrockLLM

# Bedrock 모델 설정
llm = BedrockLLM(model_id="anthropic.claude-v2:1")

# 모델을 호출하여 응답 받기
response = llm.invoke("랭체인으로 LLM 활용하기 참 쉽죠?")

print(response)

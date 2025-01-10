[amazon-bedrock-claudev3-sonnet-blog-generation](https://github.com/aws-samples/amazon-bedrock-claudev3-sonnet-blog-generation)

```bash
aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-3-sonnet-v1:0 \
    --body "{\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"Write the test case for uploading the image to Amazon S3 bucket\\nCertainly! Here's an example of a test case for uploading an image to an Amazon S3 bucket using a testing framework like JUnit or TestNG for Java:\\n\\n...."}]}],\"anthropic_version\":\"bedrock-2023-05-31\",\"max_tokens\":2000}" \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    invoke-model-output.txt
```

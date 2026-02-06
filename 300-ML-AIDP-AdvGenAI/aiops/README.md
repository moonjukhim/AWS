
You are an AWS solutions architect.

Generate an AWS Lambda function written in Python 3.13 that will be used
as an Amazon Bedrock Agent Action Group handler.

Requirements:

1. The Lambda function must inspect the event input from a Bedrock Agent
   and branch logic based on event["apiPath"].

2. If apiPath is "/get_all_alarms":
   - Use boto3 to query Amazon CloudWatch
   - Call describe_alarms
   - Filter alarms with:
     - Alarm name: "EC2_Instance_CPU_Utilization"
     - StateValue: "ALARM"

3. If no alarms are in ALARM state:
   - Return a response indicating there are no operational issues.

4. If alarms exist:
   - Extract the EC2 instance ID from alarm dimensions
   - Return a JSON list with:
     - ID
     - ResourceType (EC2)
     - State description

5. The response must strictly follow the Amazon Bedrock Agent
   Action Group Lambda response format:
   - messageVersion
   - response (actionGroup, apiPath, httpMethod, httpStatusCode, responseBody)
   - promptSessionAttributes must be preserved.

6. The responseBody must be wrapped under:
   {
     "application/json": {
       "body": ...
     }
   }

7. The Lambda function must be minimal, synchronous,
   and suitable for a timeout of under 30 seconds.

Provide the complete Lambda handler code only.

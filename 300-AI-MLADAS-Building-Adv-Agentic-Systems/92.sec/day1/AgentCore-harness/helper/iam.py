import json
import os

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_DEFAULT_REGION")

DEFAULT_ROLE_NAME = "AgentCoreHarnessExecutionRole"
_POLICY_NAME = "AgentCoreHarnessExecutionPolicy"


def _make_session():
    """Create a boto3 session"""
    session = boto3.Session(region_name=REGION)
    return session


def _trust_policy(account_id: str) -> dict:
    """Allow the AgentCore service to assume the role (scoped to this account)."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {"StringEquals": {"aws:SourceAccount": account_id}},
            }
        ],
    }


def _permissions_policy(account_id: str) -> dict:
    """Permissions the Harness needs: Bedrock model invocation, logs, and tracing."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockModelInvocation",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:*:{account_id}:inference-profile/*",
                    "arn:aws:bedrock:*:*:inference-profile/*",
                ],
            },
            {
                "Sid": "CloudWatchLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                ],
                "Resource": f"arn:aws:logs:*:{account_id}:log-group:*",
            },
            {
                "Sid": "Observability",
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "cloudwatch:PutMetricData",
                ],
                "Resource": "*",
            },
            {
                "Sid": "AgentCoreWorkloadIdentity",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                "Resource": f"arn:aws:bedrock-agentcore:*:{account_id}:workload-identity-directory/default*",
            },
        ],
    }


def create_harness_role(role_name: str = DEFAULT_ROLE_NAME) -> str:
    """Create the Harness execution role (idempotent) and return its ARN."""
    session = _make_session()
    iam = session.client("iam")
    account_id = session.client("sts").get_caller_identity()["Account"]

    try:
        role_arn = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(_trust_policy(account_id)),
            Description="Execution role for harness in AgentCore",
        )["Role"]["Arn"]
        print(f"Created role: {role_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "EntityAlreadyExists":
            raise
        role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
        print(f"Role already exists: {role_name}")

    # put_role_policy overwrites, so re-running keeps the policy up to date
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=_POLICY_NAME,
        PolicyDocument=json.dumps(_permissions_policy(account_id)),
    )
    return role_arn


def delete_harness_role(role_name: str = DEFAULT_ROLE_NAME) -> None:
    """Delete the Harness execution role and its inline/attached policies."""
    iam = _make_session().client("iam")
    try:
        for name in iam.list_role_policies(RoleName=role_name)["PolicyNames"]:
            iam.delete_role_policy(RoleName=role_name, PolicyName=name)
        for p in iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]:
            iam.detach_role_policy(RoleName=role_name, PolicyArn=p["PolicyArn"])
        iam.delete_role(RoleName=role_name)
        print(f"Deleted role: {role_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise
        print(f"Role not found: {role_name}")

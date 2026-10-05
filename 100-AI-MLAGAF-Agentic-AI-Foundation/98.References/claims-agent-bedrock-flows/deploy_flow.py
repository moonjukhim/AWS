#!/usr/bin/env python3
"""보험 청구 처리 흐름을 Amazon Bedrock Flows에 배포합니다.

만드는 것은 두 개뿐입니다.
  1. 흐름 실행용 IAM 역할 (Bedrock 모델 호출 권한)
  2. Bedrock Flow + 버전 + 별칭

Lambda, DynamoDB, SES, S3, EventBridge는 만들지 않습니다.

사용법:
    python deploy_flow.py                 # 생성 또는 갱신
    python deploy_flow.py --region us-east-1
"""

import argparse
import json
import os
import sys
import time

import boto3
from botocore.exceptions import ClientError

from flow_definition import PROCESSOR_MODEL, VALIDATOR_MODEL, build_definition

FLOW_NAME = os.getenv("FLOW_NAME", "claims-processing-flow")
ROLE_NAME = os.getenv("FLOW_ROLE_NAME", "BedrockFlowsClaimsRole")
ALIAS_NAME = "live"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".flow-config.json")


def ensure_role(region, account_id):
    """흐름 실행 역할을 만들거나 기존 것을 재사용합니다."""
    iam = boto3.client("iam")
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock:{region}:{account_id}:flow/*"},
                },
            }
        ],
    }
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:{region}:{account_id}:inference-profile/*",
                    "arn:aws:bedrock:*:*:inference-profile/*",
                ],
            }
        ],
    }

    try:
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust),
            Description="Execution role for the Bedrock Flows claims processing demo",
        )["Role"]
        created = True
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "EntityAlreadyExists":
            raise
        role = iam.get_role(RoleName=ROLE_NAME)["Role"]
        iam.update_assume_role_policy(RoleName=ROLE_NAME, PolicyDocument=json.dumps(trust))
        created = False

    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="BedrockFlowsInvokeModel",
        PolicyDocument=json.dumps(policy),
    )

    print(f"  IAM 역할 {'생성' if created else '재사용'}: {role['Arn']}")
    if created:
        # IAM 전파를 기다립니다. 바로 CreateFlow를 호출하면 역할 검증에 실패할 수 있습니다.
        print("  IAM 전파 대기 (10초)...")
        time.sleep(10)
    return role["Arn"]


def find_flow(client, name):
    paginator = client.get_paginator("list_flows")
    for page in paginator.paginate():
        for flow in page.get("flowSummaries", []):
            if flow["name"] == name:
                return flow["id"]
    return None


def wait_for_status(client, flow_id, target, timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = client.get_flow(flowIdentifier=flow_id)["status"]
        if status == target:
            return status
        if status == "Failed":
            detail = client.get_flow(flowIdentifier=flow_id).get("validations", [])
            raise RuntimeError(f"흐름 준비 실패: {json.dumps(detail, ensure_ascii=False, indent=2)}")
        time.sleep(3)
    raise TimeoutError(f"{timeout}초 안에 {target} 상태가 되지 않았습니다.")


def ensure_alias(client, flow_id, version):
    for alias in client.list_flow_aliases(flowIdentifier=flow_id).get("flowAliasSummaries", []):
        if alias["name"] == ALIAS_NAME:
            client.update_flow_alias(
                flowIdentifier=flow_id,
                aliasIdentifier=alias["id"],
                name=ALIAS_NAME,
                routingConfiguration=[{"flowVersion": version}],
            )
            return alias["id"]
    return client.create_flow_alias(
        flowIdentifier=flow_id,
        name=ALIAS_NAME,
        routingConfiguration=[{"flowVersion": version}],
    )["id"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default=os.getenv("AWS_REGION") or "us-west-2")
    args = parser.parse_args()

    region = args.region
    account_id = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
    client = boto3.client("bedrock-agent", region_name=region)

    print(f"청구 처리 흐름 배포 ({region} / {account_id})")
    print(f"  처리 에이전트 모델: {PROCESSOR_MODEL}")
    print(f"  검증 에이전트 모델: {VALIDATOR_MODEL}")

    role_arn = ensure_role(region, account_id)
    definition = build_definition()

    flow_id = find_flow(client, FLOW_NAME)
    if flow_id:
        client.update_flow(
            flowIdentifier=flow_id,
            name=FLOW_NAME,
            description="이메일로 접수된 보험 청구를 처리하고 신뢰도에 따라 라우팅하는 흐름",
            executionRoleArn=role_arn,
            definition=definition,
        )
        print(f"  흐름 갱신: {flow_id}")
    else:
        flow_id = client.create_flow(
            name=FLOW_NAME,
            description="이메일로 접수된 보험 청구를 처리하고 신뢰도에 따라 라우팅하는 흐름",
            executionRoleArn=role_arn,
            definition=definition,
        )["id"]
        print(f"  흐름 생성: {flow_id}")

    client.prepare_flow(flowIdentifier=flow_id)
    wait_for_status(client, flow_id, "Prepared")
    print("  흐름 준비 완료")

    version = client.create_flow_version(flowIdentifier=flow_id)["version"]
    alias_id = ensure_alias(client, flow_id, version)
    print(f"  버전 {version} / 별칭 {ALIAS_NAME} ({alias_id})")

    config = {
        "region": region,
        "flow_id": flow_id,
        "flow_name": FLOW_NAME,
        "flow_version": version,
        "alias_id": alias_id,
        "role_arn": role_arn,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)

    print(f"\n배포 완료. 설정 저장: {CONFIG_FILE}")
    print("\n다음 명령으로 실행해 보십시오.")
    print("  python run_flow.py samples/01-auto-approve.txt")
    print("  python run_flow.py --all")
    print(
        f"\n콘솔: https://{region}.console.aws.amazon.com/bedrock/home?region={region}#/flows/{flow_id}"
    )


if __name__ == "__main__":
    try:
        main()
    except ClientError as exc:
        print(f"AWS 오류: {exc}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""배포한 흐름과 IAM 역할을 정리합니다.

사용법:
    python delete_flow.py            # 흐름(별칭/버전 포함)만 삭제
    python delete_flow.py --all      # IAM 역할까지 삭제
"""

import argparse
import json
import os
import sys

import boto3
from botocore.exceptions import ClientError

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, ".flow-config.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="IAM 역할도 함께 삭제")
    args = parser.parse_args()

    if not os.path.exists(CONFIG_FILE):
        print("삭제할 배포 설정이 없습니다.", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_FILE, encoding="utf-8") as fh:
        cfg = json.load(fh)

    client = boto3.client("bedrock-agent", region_name=cfg["region"])

    try:
        client.delete_flow(flowIdentifier=cfg["flow_id"], skipResourceInUseCheck=True)
        print(f"  흐름 삭제: {cfg['flow_id']} (별칭과 버전 포함)")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        print("  흐름이 이미 없습니다.")

    if args.all:
        iam = boto3.client("iam")
        role_name = cfg["role_arn"].split("/")[-1]
        try:
            for policy in iam.list_role_policies(RoleName=role_name)["PolicyNames"]:
                iam.delete_role_policy(RoleName=role_name, PolicyName=policy)
            iam.delete_role(RoleName=role_name)
            print(f"  IAM 역할 삭제: {role_name}")
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "NoSuchEntity":
                raise
            print("  IAM 역할이 이미 없습니다.")

    os.remove(CONFIG_FILE)
    print("정리 완료.")


if __name__ == "__main__":
    main()

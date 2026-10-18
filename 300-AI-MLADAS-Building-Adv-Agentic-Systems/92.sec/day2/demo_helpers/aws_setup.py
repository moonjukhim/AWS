"""노트북에서만 사용하는 AWS 리소스 준비 헬퍼 (IAM 역할, Cognito, Transaction Search 등).

강의 흐름에 집중할 수 있도록 반복적인 준비 코드를 이곳에 모았습니다.
모든 함수는 여러 번 실행해도 안전하도록(idempotent) 작성되어 있습니다.
"""

import base64
import json
import time

import boto3
from boto3.session import Session

from . import config


def get_region() -> str:
    region = Session().region_name
    if not region:
        raise RuntimeError("AWS 리전이 설정되지 않았습니다. `aws configure` 또는 AWS_DEFAULT_REGION 을 설정하세요.")
    return region


def get_account_id() -> str:
    return boto3.client("sts").get_caller_identity()["Account"]


def wait_for(fn, ready, failed=(), interval=5, timeout=600, label="resource"):
    """fn() 이 반환하는 상태가 ready 에 들어갈 때까지 대기합니다."""
    start = time.time()
    while True:
        status = fn()
        if status in ready:
            print(f"  ✅ {label}: {status}")
            return status
        if status in failed:
            raise RuntimeError(f"{label} 실패: {status}")
        if time.time() - start > timeout:
            raise TimeoutError(f"{label} 대기 시간 초과 (마지막 상태: {status})")
        print(f"  ⏳ {label}: {status}")
        time.sleep(interval)


# ════════════════════════════════════════════════════════════════════
# IAM: AgentCore Runtime 실행 역할 (03장 '실행 역할' 슬라이드에서 내용을 살펴봄)
# ════════════════════════════════════════════════════════════════════
def runtime_role_policy(region: str, account_id: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {   # 컨테이너 이미지 가져오기
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
                "Resource": [f"arn:aws:ecr:{region}:{account_id}:repository/*"],
            },
            {"Sid": "ECRToken", "Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
            {   # 런타임 로그
                "Sid": "Logs",
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogStreams", "logs:CreateLogGroup", "logs:DescribeLogGroups",
                    "logs:CreateLogStream", "logs:PutLogEvents",
                ],
                "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:*"],
            },
            {   # 관찰성: X-Ray 트레이스 + CloudWatch 지표
                "Sid": "Observability",
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments", "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules", "xray:GetSamplingTargets",
                ],
                "Resource": "*",
            },
            {
                "Sid": "Metrics",
                "Effect": "Allow",
                "Action": "cloudwatch:PutMetricData",
                "Resource": "*",
                "Condition": {"StringEquals": {"cloudwatch:namespace": "bedrock-agentcore"}},
            },
            {   # 모델 호출 (스트리밍 포함)
                "Sid": "BedrockModelInvocation",
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:*:{account_id}:inference-profile/*",
                ],
            },
            {   # AgentCore Identity: 워크로드 액세스 토큰 + 아웃바운드 자격 증명 (03장)
                "Sid": "AgentCoreIdentity",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                    "bedrock-agentcore:GetResourceApiKey",
                    "bedrock-agentcore:GetResourceOauth2Token",
                ],
                "Resource": "*",
            },
            {   # Identity 가 보관한 자격 증명은 Secrets Manager 에 저장됨
                "Sid": "IdentitySecrets",
                "Effect": "Allow",
                "Action": ["secretsmanager:GetSecretValue"],
                "Resource": f"arn:aws:secretsmanager:{region}:{account_id}:secret:bedrock-agentcore-identity!*",
            },
            {   # AgentCore Code Interpreter (04장)
                "Sid": "CodeInterpreter",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:StartCodeInterpreterSession",
                    "bedrock-agentcore:InvokeCodeInterpreter",
                    "bedrock-agentcore:StopCodeInterpreterSession",
                ],
                "Resource": "*",
            },
            {   # AgentCore Memory (05장)
                "Sid": "Memory",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:CreateEvent", "bedrock-agentcore:ListEvents", "bedrock-agentcore:GetEvent",
                    "bedrock-agentcore:RetrieveMemoryRecords", "bedrock-agentcore:ListMemoryRecords",
                    "bedrock-agentcore:GetMemoryRecord", "bedrock-agentcore:GetMemory",
                ],
                "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:memory/*"],
            },
        ],
    }


def ensure_runtime_execution_role() -> str:
    """에이전트가 런타임에서 사용할 IAM 실행 역할을 생성(또는 갱신)합니다."""
    iam = boto3.client("iam")
    region, account_id = get_region(), get_account_id()
    role_name = f"{config.RUNTIME_ROLE_NAME_PREFIX}-{region}"
    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": account_id},
                "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"},
            },
        }],
    }
    created = False
    try:
        role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
        print(f"ℹ️  기존 실행 역할 재사용: {role_name}")
    except iam.exceptions.NoSuchEntityException:
        role_arn = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust),
            Description="AgentCore demo - customer support agent runtime role",
        )["Role"]["Arn"]
        created = True
        print(f"✅ 실행 역할 생성: {role_name}")

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="AgentCoreDemoRuntimePolicy",
        PolicyDocument=json.dumps(runtime_role_policy(region, account_id)),
    )
    if created:
        print("⏳ IAM 전파 대기 (15초)...")
        time.sleep(15)
    config.save_state(runtime_role_arn=role_arn, runtime_role_name=role_name)
    return role_arn


# ════════════════════════════════════════════════════════════════════
# Cognito: 인바운드 인증용 사용자 풀 (03장)
# ════════════════════════════════════════════════════════════════════
def ensure_cognito_user_pool() -> dict:
    """Cognito 사용자 풀, 앱 클라이언트, 데모 사용자(alice, bob)를 준비합니다."""
    region = get_region()
    cognito = boto3.client("cognito-idp", region_name=region)
    state = config.load_state()

    pool_id = state.get("cognito_pool_id")
    if pool_id:
        try:
            cognito.describe_user_pool(UserPoolId=pool_id)
            print(f"ℹ️  기존 Cognito 사용자 풀 재사용: {pool_id}")
            return state
        except cognito.exceptions.ResourceNotFoundException:
            pass

    pool_id = cognito.create_user_pool(
        PoolName=config.COGNITO_POOL_NAME,
        Policies={"PasswordPolicy": {"MinimumLength": 8}},
    )["UserPool"]["Id"]
    client_id = cognito.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName=config.COGNITO_CLIENT_NAME,
        GenerateSecret=False,
        ExplicitAuthFlows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
    )["UserPoolClient"]["ClientId"]

    for user in config.DEMO_USERS:
        cognito.admin_create_user(
            UserPoolId=pool_id, Username=user, MessageAction="SUPPRESS",
            TemporaryPassword=config.DEMO_PASSWORD,
        )
        cognito.admin_set_user_password(
            UserPoolId=pool_id, Username=user, Password=config.DEMO_PASSWORD, Permanent=True
        )

    discovery_url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration"
    print(f"✅ Cognito 사용자 풀 생성: {pool_id} (사용자: {', '.join(config.DEMO_USERS)})")
    return config.save_state(
        cognito_pool_id=pool_id, cognito_client_id=client_id, cognito_discovery_url=discovery_url
    )


def get_bearer_token(username: str) -> str:
    """사용자 이름/비밀번호로 로그인해 Cognito 액세스 토큰(JWT)을 발급받습니다 (유효기간 1시간)."""
    state = config.require_state("cognito_client_id")
    cognito = boto3.client("cognito-idp", region_name=get_region())
    result = cognito.initiate_auth(
        ClientId=state["cognito_client_id"],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": config.DEMO_PASSWORD},
    )
    return result["AuthenticationResult"]["AccessToken"]


def decode_jwt_claims(token: str) -> dict:
    """JWT 페이로드를 디코딩합니다 (서명 검증은 AgentCore 가 이미 수행)."""
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


# ════════════════════════════════════════════════════════════════════
# 04장: Lambda 실행 역할 / Gateway 서비스 역할
# ════════════════════════════════════════════════════════════════════
def _ensure_role(role_name: str, service: str, inline_policy: dict = None, managed_arns=()) -> str:
    iam = boto3.client("iam")
    trust = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Principal": {"Service": service}, "Action": "sts:AssumeRole"}],
    }
    created = False
    try:
        arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
    except iam.exceptions.NoSuchEntityException:
        arn = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust))["Role"]["Arn"]
        created = True
    for managed in managed_arns:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=managed)
    if inline_policy:
        iam.put_role_policy(RoleName=role_name, PolicyName=f"{role_name}Policy", PolicyDocument=json.dumps(inline_policy))
    if created:
        print(f"✅ IAM 역할 생성: {role_name} (전파 대기 15초)")
        time.sleep(15)
    else:
        print(f"ℹ️  기존 IAM 역할 재사용: {role_name}")
    return arn


def ensure_lambda_role() -> str:
    return _ensure_role(
        config.LAMBDA_ROLE_NAME,
        "lambda.amazonaws.com",
        managed_arns=["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
    )


def ensure_gateway_role(lambda_arn: str) -> str:
    region, account_id = get_region(), get_account_id()
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": lambda_arn},
            {   # AgentCore Policy 엔진 평가 권한
                "Effect": "Allow",
                "Action": "bedrock-agentcore:*",
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:policy-engine/*",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:gateway/*",
                ],
            },
        ],
    }
    return _ensure_role(config.GATEWAY_ROLE_NAME, "bedrock-agentcore.amazonaws.com", inline_policy=policy)


# ════════════════════════════════════════════════════════════════════
# 06장: CloudWatch Transaction Search 활성화 (계정·리전당 1회)
# ════════════════════════════════════════════════════════════════════
def enable_transaction_search():
    region, account_id = get_region(), get_account_id()
    logs = boto3.client("logs", region_name=region)
    xray = boto3.client("xray", region_name=region)

    current = xray.get_trace_segment_destination()
    if current.get("Destination") == "CloudWatchLogs" and current.get("Status") == "ACTIVE":
        print("ℹ️  Transaction Search 가 이미 활성화되어 있습니다.")
        return

    logs.put_resource_policy(
        policyName="AgentCoreDemoTransactionSearch",
        policyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "TransactionSearchXRayAccess",
                "Effect": "Allow",
                "Principal": {"Service": "xray.amazonaws.com"},
                "Action": "logs:PutLogEvents",
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:aws/spans:*",
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/application-signals/data:*",
                ],
                "Condition": {
                    "ArnLike": {"aws:SourceArn": f"arn:aws:xray:{region}:{account_id}:*"},
                    "StringEquals": {"aws:SourceAccount": account_id},
                },
            }],
        }),
    )
    try:
        xray.update_trace_segment_destination(Destination="CloudWatchLogs")
    except xray.exceptions.InvalidRequestException as e:
        if "already" not in str(e).lower():
            raise
    wait_for(
        lambda: xray.get_trace_segment_destination().get("Status"),
        ready={"ACTIVE"}, interval=10, timeout=300, label="Transaction Search",
    )

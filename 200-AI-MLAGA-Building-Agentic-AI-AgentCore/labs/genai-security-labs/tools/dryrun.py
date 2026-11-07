"""
노트북 드라이런: 모든 AWS API 호출을 가로채 botocore 서비스 모델로 파라미터를 검증하고,
출력 셰이프로부터 만든 가짜 응답을 돌려줘 노트북을 처음부터 끝까지 실행한다.
"""
import io, json, os, sys, time, types, urllib.request, builtins
import nbformat
import botocore.client, botocore.waiter
from botocore.validate import ParamValidator

os.environ["LAB_MODEL_ID"] = "us.anthropic.claude-haiku-4-5-test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ.setdefault("AWS_ACCESS_KEY_ID", "AKIAFAKE"); os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "fake")

ERRORS, CALLS = [], []
PREF = ["READY", "ACTIVE", "COMPLETE", "end_turn", "NONE", "ENFORCE", "Enabled", "aws:kms"]
FAKE_JWT = "h." + __import__("base64").urlsafe_b64encode(json.dumps({"username": "dr_kim", "client_id": "c", "token_use": "access", "iss": "i"}).encode()).decode().rstrip("=") + ".s"


def gen(shape, name="", depth=0):
    if shape is None or depth > 8:
        return None
    t = shape.type_name
    if t == "structure":
        if shape.metadata.get("union"):
            k = next(iter(shape.members)); return {k: gen(shape.members[k], k, depth + 1)}
        return {k: gen(v, k, depth + 1) for k, v in shape.members.items()}
    if t == "list":
        return [gen(shape.member, name, depth + 1)]
    if t == "map":
        return {"k": gen(shape.value, name, depth + 1)}
    if t == "string":
        if shape.enum:
            for p in PREF:
                if p in shape.enum: return p
            return shape.enum[0]
        if name == "uri": return "s3://x/docs/01_outpatient_hours.txt"
        if name in ("AccessToken", "IdToken"): return FAKE_JWT
        if name.lower().endswith("arn"): return "arn:aws:service:us-east-1:123456789012:thing/x/y"
        if name == "ETag": return '"etag"'
        if name.endswith("Url"): return "https://gw.example.com/mcp"
        n = max(int(shape.metadata.get("min", 1) or 1), 12)
        return ("abc123def456" * 10)[:n]
    if t in ("integer", "long"): return 1
    if t in ("double", "float"): return 0.5
    if t == "boolean": return False
    if t == "timestamp":
        import datetime; return datetime.datetime(2026, 11, 5)
    if t == "blob":
        return io.BytesIO(b'{"ok": true, "sources": ["s3://x/a"]}') if shape.serialization.get("streaming") or name == "Payload" else b"x"
    return None


OVERRIDES = {
    "GetCallerIdentity": lambda p: {"Account": "123456789012", "Arn": "arn", "UserId": "u"},
    "ListGuardrails": lambda p: {"guardrails": []},
    "ListKnowledgeBases": lambda p: {"knowledgeBaseSummaries": []},
    "ListDataSources": lambda p: {"dataSourceSummaries": []},
    "ListUserPools": lambda p: {"UserPools": []},
    "ListUserPoolClients": lambda p: {"UserPoolClients": []},
    "ListPolicyEngines": lambda p: {"policyEngines": []},
    "ListGateways": lambda p: {"items": []},
    "ListGatewayTargets": lambda p: {"items": []},
    "ListPolicies": lambda p: {"policies": []},
    "DescribeStacks": lambda p: {"Stacks": [{"StackName": "s", "CreationTime": 0, "StackStatus": "CREATE_COMPLETE", "Outputs": [
        {"OutputKey": k, "OutputValue": "x" if k == "DocsBucketName" else f"arn:aws:x:us-east-1:1:{k}/id"} for k in
        ["KmsKeyArn", "DocsBucketName", "VpcId", "AgentRuntimeEndpointId", "RetrieverFunctionName", "RetrieverRoleArn"]]}]},
}


def fake_call(self, op, params):
    model = self.meta.service_model.operation_model(op)
    svc = self.meta.service_model.service_name
    CALLS.append(f"{svc}.{op}")
    if model.input_shape is not None:
        report = ParamValidator().validate(params, model.input_shape)
        if report.has_errors():
            ERRORS.append(f"[{CURRENT}] {svc}.{op}: {report.generate_report()}")
    if op in OVERRIDES:
        return OVERRIDES[op](params)
    out = gen(model.output_shape) if model.output_shape else {}
    out = out or {}
    out["ResponseMetadata"] = {"RequestId": "req-1", "HTTPStatusCode": 200}
    return out


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): pass


def fake_urlopen(req, timeout=None):
    body = json.loads(req.data.decode())
    if body["method"] == "tools/list":
        res = {"tools": [{"name": "HospitalEMR___get_patient_summary", "description": "d", "inputSchema": {"type": "object", "properties": {}}}]}
    else:
        res = {"content": [{"type": "text", "text": "ok"}], "isError": False}
    return FakeResp(json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": res}).encode())


botocore.client.BaseClient._make_api_call = fake_call
botocore.waiter.Waiter.wait = lambda self, **k: None
urllib.request.urlopen = fake_urlopen
time.sleep = lambda s: None

# boto3 S3 upload_file은 s3transfer 스레드를 쓰므로 put_object로 대체
import boto3.s3.inject
def _upload_file(self, Filename, Bucket, Key, **kw):
    self.put_object(Bucket=Bucket, Key=Key, Body=open(Filename, "rb").read())
boto3.s3.inject.upload_file = _upload_file
import botocore.client as bc

CURRENT = ""


def run(nb_path):
    global CURRENT
    nb = nbformat.read(nb_path, as_version=4)
    d = os.path.dirname(os.path.abspath(nb_path))
    cwd = os.getcwd(); os.chdir(d)
    sys.path.insert(0, d)
    g = {"__name__": "__main__"}
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        CURRENT = f"{os.path.basename(nb_path)}#cell{i}"
        try:
            exec(compile(c.source, CURRENT, "exec"), g)
        except Exception as e:
            import traceback
            ERRORS.append(f"[{CURRENT}] EXEC {type(e).__name__}: {e}\n" + "".join(traceback.format_exc().splitlines(True)[-4:]))
    os.chdir(cwd)


if __name__ == "__main__":
    import contextlib
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    state = os.path.join(root, "lab_state.json")
    if os.path.exists(state): os.remove(state)
    for nb in sys.argv[1:]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run(os.path.join(root, nb))
        print(f"== {nb}: 출력 {len(buf.getvalue())}자")
    print("\nAPI 호출 수:", len(CALLS), "| 고유:", len(set(CALLS)))
    print("오류 수:", len(ERRORS))
    for e in ERRORS:
        print("-", e[:700])
    for leftover in ["lab_state.json", "lab2_adversarial/redteam_regression.jsonl", "lab3_rag_security/lineage_log.jsonl"]:
        p = os.path.join(root, leftover)
        if os.path.exists(p): os.remove(p)

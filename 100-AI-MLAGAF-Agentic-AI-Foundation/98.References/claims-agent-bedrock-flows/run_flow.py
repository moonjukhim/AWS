#!/usr/bin/env python3
"""배포한 흐름에 이메일을 넣고 결과를 확인합니다.

사용법:
    python run_flow.py samples/01-auto-approve.txt      # 파일 하나 처리
    python run_flow.py --all                            # 샘플 4건 모두 처리
    python run_flow.py --text "POL-12345 ... 3천 달러 피해"   # 직접 입력
    python run_flow.py samples/01-auto-approve.txt --trace   # 노드별 추적 출력
    python run_flow.py --all --json                     # 결과를 JSON으로만 출력
"""

import argparse
import glob
import json
import os
import sys
import time

import boto3
from botocore.config import Config

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, ".flow-config.json")

ACTION_LABEL = {
    "AUTO_APPROVE": "자동 승인",
    "HUMAN_REVIEW": "사람 검토로 에스컬레이션",
    "REJECT": "거절",
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("배포 설정이 없습니다. 먼저 python deploy_flow.py 를 실행하십시오.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def invoke(client, cfg, email_text, trace=False):
    """흐름을 한 번 호출하고 (결과 문서, 결과를 낸 노드 이름, 추적 목록)을 돌려줍니다."""
    kwargs = {
        "flowIdentifier": cfg["flow_id"],
        "flowAliasIdentifier": cfg["alias_id"],
        "inputs": [
            {
                "nodeName": "EmailInput",
                "nodeOutputName": "document",
                "content": {"document": email_text},
            }
        ],
    }
    if trace:
        kwargs["enableTrace"] = True

    response = client.invoke_flow(**kwargs)

    document, node_name, traces, completion = None, None, [], None
    for event in response["responseStream"]:
        if "flowOutputEvent" in event:
            out = event["flowOutputEvent"]
            node_name = out.get("nodeName")
            document = out.get("content", {}).get("document")
        elif "flowTraceEvent" in event:
            traces.append(event["flowTraceEvent"]["trace"])
        elif "flowCompletionEvent" in event:
            completion = event["flowCompletionEvent"].get("completionReason")

    if completion and completion != "SUCCESS":
        print(f"  흐름 완료 상태: {completion}", file=sys.stderr)
    return document, node_name, traces


def print_traces(traces):
    print("\n  ── 노드 추적 ──")
    for trace in traces:
        node = trace.get("nodeInputTrace") or trace.get("nodeOutputTrace") or {}
        name = node.get("nodeName")
        if not name:
            continue
        if "nodeInputTrace" in trace:
            for field in node.get("fields", []):
                value = json.dumps(field.get("content", {}).get("document"), ensure_ascii=False)
                print(f"  [입력 ] {name}.{field.get('nodeInputName')}: {value[:160]}")
        else:
            for field in node.get("fields", []):
                value = json.dumps(field.get("content", {}).get("document"), ensure_ascii=False)
                print(f"  [출력 ] {name}.{field.get('nodeOutputName')}: {value[:160]}")


def print_result(document, node_name, elapsed):
    if not isinstance(document, dict):
        print(f"  결과: {document}")
        return

    action = document.get("action", "?")
    print(f"  경로: {node_name} 노드 → {ACTION_LABEL.get(action, action)}  ({elapsed:.1f}초)")
    print(
        f"  증권 {document.get('policy_number')} / "
        f"${document.get('amount', 0):,} / {document.get('category')} / "
        f"조회 {'성공' if document.get('policy_found') else '실패'}"
    )
    print(f"\n  [1단계 처리] {document.get('decision')} — {document.get('reasoning')}")
    if document.get("coverage_check"):
        print(f"             보장 확인: {document['coverage_check']}")
    print(
        f"\n  [2단계 검증] 신뢰도 {document.get('confidence')}/100 "
        f"(임계값 {document.get('threshold')}) → {document.get('routing')}"
    )
    if document.get("validation_notes"):
        print(f"             {document['validation_notes']}")
    if document.get("concerns"):
        print(f"             우려: {document['concerns']}")

    print(f"\n  [3단계 실행] 상태 {document.get('status')}")
    if document.get("claim_id"):
        print(f"             청구 생성: {document['claim_id']}")
    if document.get("review_id"):
        print(f"             검토 요청: {document['review_id']} (우선순위 {document.get('priority')})")
    note = document.get("notification", {})
    if note.get("recipient"):
        print(f"             알림 → {note['recipient']}: {note.get('subject')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="이메일 텍스트 파일 경로")
    parser.add_argument("--all", action="store_true", help="samples 디렉터리의 모든 샘플 실행")
    parser.add_argument("--text", help="파일 대신 직접 입력한 청구 내용")
    parser.add_argument("--trace", action="store_true", help="노드별 입출력 추적 출력")
    parser.add_argument("--json", action="store_true", dest="as_json", help="결과 JSON만 출력")
    args = parser.parse_args()

    cfg = load_config()
    # 흐름 한 건에 20초 안팎이 걸리므로 기본 60초 읽기 제한을 늘려 둡니다.
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=cfg["region"],
        config=Config(read_timeout=300, connect_timeout=15, retries={"max_attempts": 2}),
    )

    jobs = []
    if args.text:
        jobs.append(("(직접 입력)", args.text))
    if args.all:
        for path in sorted(glob.glob(os.path.join(HERE, "samples", "*.txt"))):
            jobs.append((os.path.basename(path), open(path, encoding="utf-8").read()))
    for path in args.files:
        jobs.append((os.path.basename(path), open(path, encoding="utf-8").read()))

    if not jobs:
        parser.error("파일 경로, --all, --text 중 하나를 지정하십시오.")

    results = []
    for name, text in jobs:
        if not args.as_json:
            first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
            print(f"\n{'=' * 78}\n{name}  |  {first_line[:60]}\n{'=' * 78}")
        started = time.time()
        document, node_name, traces = invoke(client, cfg, text, trace=args.trace)
        elapsed = time.time() - started
        results.append({"source": name, "output_node": node_name, "result": document})
        if args.as_json:
            continue
        print_result(document, node_name, elapsed)
        if args.trace:
            print_traces(traces)

    if args.as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

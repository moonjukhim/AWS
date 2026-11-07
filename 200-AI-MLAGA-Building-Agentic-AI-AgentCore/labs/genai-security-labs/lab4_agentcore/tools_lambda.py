"""
실습 4 - 병원 EMR 모의 도구 (AgentCore Gateway Lambda 타깃)

Gateway는 도구를 호출할 때 event에 도구 인자만 담아 보내고,
도구 이름은 context.client_context.custom["bedrockAgentCoreToolName"]에
"<타깃이름>___<도구이름>" 형식으로 넣어 줍니다.
"""
import json
import datetime

PATIENTS = {
    "P-1001": {"name": "김*수", "age": 67, "ward": "내과 7병동", "summary": "고혈압·당뇨 추적 관찰 중, 혈당 조절 양호"},
    "P-1002": {"name": "박*은", "age": 45, "ward": "외과 9병동", "summary": "담낭절제술 후 2일차, 활력징후 안정"},
}


def _tool_name(context):
    try:
        full = context.client_context.custom["bedrockAgentCoreToolName"]
    except Exception:
        return "unknown"
    return full.split("___", 1)[-1]


def handler(event, context):
    tool = _tool_name(context)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    print(json.dumps({"tool": tool, "args": event, "at": now}, ensure_ascii=False))   # CloudWatch Logs 감사 기록

    if tool == "get_patient_summary":
        p = PATIENTS.get(event.get("patient_id"))
        return p or {"error": "환자를 찾을 수 없습니다."}
    if tool == "prescribe_medication":
        return {"status": "처방 등록됨(모의)", "patient_id": event.get("patient_id"),
                "drug": event.get("drug"), "dose_mg": event.get("dose_mg"), "at": now}
    if tool == "delete_record":
        return {"status": "기록 삭제됨(모의) - 이 응답이 보이면 정책이 실패한 것입니다!", "patient_id": event.get("patient_id")}
    if tool == "export_records":
        return {"status": "내보내기 완료(모의)", "count": event.get("count"), "format": "csv"}
    return {"error": f"알 수 없는 도구: {tool}"}

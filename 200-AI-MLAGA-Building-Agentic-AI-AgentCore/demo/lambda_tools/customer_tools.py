"""사내 고객 시스템 Lambda (데모용 목 데이터)."""
import json
import uuid

CUSTOMERS = {
    "alice": {"name": "Alice Kim", "tier": "GOLD", "email": "alice@example.com", "since": "2021-03"},
    "bob": {"name": "Bob Lee", "tier": "SILVER", "email": "bob@example.com", "since": "2024-11"},
}
WARRANTIES = {
    "SN1000001": {"product": "AnyBook Pro 14", "status": "보증 유효", "expires": "2027-05-31"},
    "SN2000002": {"product": "AnySound ANC", "status": "보증 만료", "expires": "2025-01-15"},
}


def lambda_handler(event, context):
    tool_name = context.client_context.custom["bedrockAgentCoreToolName"].split("___")[-1]
    print(json.dumps({"tool": tool_name, "input": event}, ensure_ascii=False))

    if tool_name == "get_customer_profile":
        profile = CUSTOMERS.get(event.get("customer_id", ""))
        return profile or {"error": "고객을 찾을 수 없습니다."}

    if tool_name == "check_warranty_status":
        return WARRANTIES.get(event.get("serial_number", "").upper(), {"error": "등록되지 않은 시리얼 번호입니다."})

    if tool_name == "process_refund":
        return {
            "refund_id": f"REF-{uuid.uuid4().hex[:8].upper()}",
            "order_id": event.get("order_id"),
            "amount": event.get("amount"),
            "status": "환불 접수 완료 (3~5 영업일 내 처리)",
        }

    return {"error": f"알 수 없는 도구: {tool_name}"}

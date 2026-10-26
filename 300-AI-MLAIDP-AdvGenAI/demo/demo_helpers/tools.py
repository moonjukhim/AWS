"""고객지원 에이전트의 로컬 도구와 시스템 프롬프트 (챕터 02부터 사용).

로컬 도구 = 에이전트 코드 안에 함께 배포되는 '런타임 정의 도구'입니다.
챕터 04에서는 여러 에이전트가 공유해야 하는 도구를 AgentCore Gateway 로 옮깁니다.
"""

from strands import tool

SYSTEM_PROMPT = """당신은 전자제품 온라인 쇼핑몰 'AnyCompany Electronics'의 친절한 고객지원 상담원입니다.

역할:
- 사용 가능한 도구를 활용해 정확한 정보를 제공합니다. 추측하지 말고 도구 결과에 근거해 답합니다.
- 제품 정보, 반품/교환 정책, 기술 지원 문의를 처리합니다.
- 친절하고 간결하게 답하며, 답변 끝에 추가로 도울 일이 있는지 묻습니다.
- 처리할 수 없는 요청은 고객센터(1588-0000)로 안내합니다.
- 고객이 사용한 언어로 답합니다.
"""

_PRODUCTS = {
    "laptop": {
        "name": "AnyBook Pro 14 노트북",
        "price": "1,890,000원",
        "warranty": "1년 제조사 보증 (최대 3년 연장 가능)",
        "specs": "Intel Core Ultra 7, 32GB RAM, 1TB SSD, 14인치 2.8K OLED",
        "features": "백라이트 키보드, Thunderbolt 4, Wi-Fi 7",
    },
    "smartphone": {
        "name": "AnyPhone 16",
        "price": "1,250,000원",
        "warranty": "1년 제조사 보증",
        "specs": "5G, 256GB, 트리플 카메라, 6.3인치 디스플레이",
        "features": "무선 충전, IP68 방수, 얼굴 인식",
    },
    "headphones": {
        "name": "AnySound ANC 무선 헤드폰",
        "price": "349,000원",
        "warranty": "1년 제조사 보증",
        "specs": "블루투스 5.3, 액티브 노이즈 캔슬링, 30시간 재생",
        "features": "터치 컨트롤, 멀티포인트 연결, USB-C 고속 충전",
    },
    "monitor": {
        "name": "AnyView 27 4K 모니터",
        "price": "590,000원",
        "warranty": "3년 제조사 보증",
        "specs": "27인치 4K IPS, 144Hz, HDR600",
        "features": "USB-C 90W 충전, 높이 조절 스탠드",
    },
}

_RETURN_POLICIES = {
    "laptop": ("30일", "기술 지원팀 점검 후 반품 가능, 구성품 및 원 포장 필수", "검수 후 7~10 영업일"),
    "smartphone": ("14일", "초기화 필수, 외관 손상 없을 것", "검수 후 5~7 영업일"),
    "headphones": ("30일", "미개봉 시 전액 환불, 개봉 시 10% 차감", "수령 후 3~5 영업일"),
    "monitor": ("30일", "불량 화소 기준(3개 이상) 충족 시 무상 교환", "검수 후 5~7 영업일"),
}


@tool
def get_product_info(product_type: str) -> str:
    """제품의 가격, 사양, 보증 정보를 조회합니다.

    Args:
        product_type: 제품 유형 (laptop, smartphone, headphones, monitor 중 하나)
    """
    product = _PRODUCTS.get(product_type.lower().strip())
    if not product:
        return f"'{product_type}' 제품 정보를 찾을 수 없습니다. 지원 유형: {', '.join(_PRODUCTS)}"
    return "\n".join(f"- {k}: {v}" for k, v in product.items())


@tool
def get_return_policy(product_type: str) -> str:
    """제품 유형별 반품/교환 정책을 조회합니다.

    Args:
        product_type: 제품 유형 (laptop, smartphone, headphones, monitor 중 하나)
    """
    window, condition, refund = _RETURN_POLICIES.get(
        product_type.lower().strip(), ("30일", "구성품 포함 원 상태", "검수 후 5~7 영업일")
    )
    return f"- 반품 가능 기간: 수령 후 {window}\n- 조건: {condition}\n- 환불 소요: {refund}"

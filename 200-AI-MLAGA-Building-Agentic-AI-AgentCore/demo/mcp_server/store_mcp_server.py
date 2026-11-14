"""매장 운영 MCP 서버 (Streamable HTTP, stateless)."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(host="127.0.0.1", port=8000, stateless_http=True)


@mcp.tool()
def get_store_hours(city: str) -> str:
    """도시별 오프라인 서비스센터 운영 시간을 알려줍니다."""
    hours = {"서울": "평일 09:00-20:00, 토 10:00-17:00", "부산": "평일 09:00-18:00"}
    return hours.get(city, "해당 도시에는 서비스센터가 없습니다. 택배 A/S 를 이용하세요.")


@mcp.tool()
def estimate_delivery_days(region: str) -> int:
    """배송 지역의 예상 배송 소요일을 계산합니다."""
    return 1 if region in ("서울", "경기", "인천") else 2


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

"""
AnyCompany Consulting - 고객 지원 이메일 에이전트 (LangGraph)

워크플로 패턴: 라우팅(Routing) + 스레드 단위 상태 영속화(Checkpointer) + Human-in-the-loop

    START
      │
    load_thread ── (같은 thread_id의 이전 대화/티켓 상태 로드, 후속 메일 여부 판단)
      │
    classify ──── (LLM 구조화 출력: spam / simple / escalate)
      │
      ├─ spam      → mark_spam    → END
      ├─ simple    → auto_reply   → END
      └─ escalate  → escalate(티켓 생성/연결) → human_review(interrupt: 담당자 답변 대기)
                                                → send_human_reply → END

실행:
    pip install langgraph openai pydantic grandalf
    set OPENAI_API_KEY=...
    (선택) set OPENAI_MODEL=gpt-5
    python email_agent.py
"""

from __future__ import annotations

import operator
import os
import uuid
from typing import Annotated, Literal, Optional, TypedDict

from openai import OpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
client = OpenAI()  # OPENAI_API_KEY 환경 변수 사용

# 간단한 질문에 답할 때 참고하는 지식 베이스 (실서비스에서는 RAG/DB로 대체)
FAQ = """
- 영업시간: 평일 09:00~18:00 (KST), 주말/공휴일 휴무
- 비밀번호 재설정: 로그인 화면의 '비밀번호 찾기' 클릭 후 가입 이메일로 링크 수신
- 청구서 확인: 대시보드 > 결제 > 청구서 메뉴에서 PDF 다운로드
- 요금제 변경: 대시보드 > 구독 관리에서 언제든 변경 가능, 다음 결제일부터 적용
- 컨설팅 미팅 예약: https://anycompany.example.com/booking
"""


# ──────────────────────────────────────────────────────────────
# 상태 정의
# ──────────────────────────────────────────────────────────────
class Email(TypedDict):
    sender: str
    subject: str
    body: str


class Classification(BaseModel):
    """LLM이 반환하는 분류 결과 (구조화 출력)."""

    route: Literal["spam", "simple", "escalate"] = Field(
        description="spam: 스팸/피싱/광고, simple: FAQ로 답변 가능한 단순 질문, "
        "escalate: 긴급하거나 복잡해서 사람이 처리해야 하는 문제"
    )
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(description="이메일 내용 한 줄 요약 (한국어)")
    reason: str = Field(description="이 경로를 선택한 이유 (한국어, 한 문장)")


class ReplyDraft(BaseModel):
    reply: str = Field(description="고객에게 보낼 한국어 답장 본문")
    answered_from_faq: bool = Field(
        description="FAQ 정보만으로 답변이 충분하면 true, 아니면 false"
    )


class EmailState(TypedDict, total=False):
    # 이번에 수신한 이메일 (매 호출마다 입력)
    email: Email
    # 스레드 전체 이력 - reducer(operator.add)로 누적되고 checkpointer가 thread_id별로 보관
    history: Annotated[list[dict], operator.add]
    # 스레드 수준 상태 (후속 메일 추적용)
    is_followup: bool
    ticket_id: Optional[str]
    # 이번 메일 처리 결과
    classification: dict
    outcome: str
    reply: Optional[str]


# ──────────────────────────────────────────────────────────────
# LLM 헬퍼
# ──────────────────────────────────────────────────────────────
def llm_parse(system: str, user: str, schema: type[BaseModel]) -> BaseModel:
    # Responses API 구조화 출력: Pydantic 스키마에 맞는 JSON을 받아 바로 검증된 객체로 변환
    response = client.responses.parse(
        model=MODEL,
        instructions=system,
        input=user,
        text_format=schema,
        # 대량(시간당 1,000건+) 처리이므로 낮은 reasoning effort로 비용·지연 절감
        reasoning={"effort": "low"},
        max_output_tokens=4096,
    )
    if response.output_parsed is None:
        raise RuntimeError(f"LLM 응답을 파싱할 수 없습니다: status={response.status}")
    return response.output_parsed


def format_history(history: list[dict]) -> str:
    if not history:
        return "(이전 대화 없음)"
    return "\n".join(f"[{h['role']}] {h['content']}" for h in history[-10:])


# ──────────────────────────────────────────────────────────────
# 노드
# ──────────────────────────────────────────────────────────────
def load_thread(state: EmailState) -> dict:
    """스레드 이력을 보고 후속 메일인지 판단하고, 수신 메일을 이력에 추가."""
    email = state["email"]
    is_followup = len(state.get("history", [])) > 0
    print(f"\n📨 수신: [{email['subject']}] from {email['sender']}"
          f"{'  (후속 메일' + (', 티켓 ' + state['ticket_id'] if state.get('ticket_id') else '') + ')' if is_followup else ''}")
    return {
        "is_followup": is_followup,
        "history": [{"role": "customer", "content": f"{email['subject']} - {email['body']}"}],
        # 이전 메일의 처리 결과는 초기화
        "classification": {},
        "outcome": "",
        "reply": None,
    }


def classify(state: EmailState) -> dict:
    email = state["email"]
    system = (
        "당신은 AnyCompany Consulting 고객 지원팀의 이메일 분류기입니다. "
        "수신 이메일을 spam / simple / escalate 중 하나로 분류하세요.\n"
        "- 아래 FAQ로 답할 수 있는 단순 질문은 simple\n"
        "- 서비스 장애, 데이터 유실, 보안, 환불/계약 분쟁, 강한 불만, FAQ로 답할 수 없는 문제는 escalate\n"
        "- 이미 담당자에게 에스컬레이션된 스레드(티켓 존재)의 후속 메일은 스팸이 아닌 한 escalate\n"
        f"\nFAQ:\n{FAQ}"
    )
    user = (
        f"스레드 티켓: {state.get('ticket_id') or '없음'}\n"
        f"이전 대화:\n{format_history(state.get('history', [])[:-1])}\n\n"
        f"보낸 사람: {email['sender']}\n제목: {email['subject']}\n본문:\n{email['body']}"
    )
    result = llm_parse(system, user, Classification)
    print(f"   🔎 분류: {result.route} (긴급도 {result.urgency}) - {result.reason}")
    return {"classification": result.model_dump()}


def route_email(state: EmailState) -> Literal["mark_spam", "auto_reply", "escalate"]:
    return {
        "spam": "mark_spam",
        "simple": "auto_reply",
        "escalate": "escalate",
    }[state["classification"]["route"]]


def mark_spam(state: EmailState) -> dict:
    print("   🗑️  스팸 폴더로 이동")
    return {"outcome": "spam"}


def auto_reply(state: EmailState) -> Command[Literal["escalate", "__end__"]]:
    email = state["email"]
    draft = llm_parse(
        system=(
            "당신은 AnyCompany Consulting 고객 지원 담당자입니다. "
            "FAQ에 있는 정보만 사용해 정중하고 간결한 한국어 답장을 작성하세요. "
            "FAQ로 답할 수 없으면 answered_from_faq=false로 표시하세요.\n"
            f"\nFAQ:\n{FAQ}"
        ),
        user=(
            f"이전 대화:\n{format_history(state.get('history', [])[:-1])}\n\n"
            f"제목: {email['subject']}\n본문:\n{email['body']}"
        ),
        schema=ReplyDraft,
    )
    # 안전장치: 자동 답변에 자신이 없으면 에스컬레이션으로 넘김
    if not draft.answered_from_faq:
        print("   ↪️  FAQ로 답변 불가 → 에스컬레이션")
        return Command(goto="escalate")

    print(f"   ✉️  자동 답장 발송:\n{indent(draft.reply)}")
    return Command(
        goto=END,
        update={
            "outcome": "auto_replied",
            "reply": draft.reply,
            "history": [{"role": "agent(auto)", "content": draft.reply}],
        },
    )


def escalate(state: EmailState) -> dict:
    """티켓을 생성하거나 기존 티켓에 후속 메일을 연결."""
    if state.get("ticket_id"):
        print(f"   🚨 에스컬레이션: 기존 티켓 {state['ticket_id']}에 후속 메일 추가")
        return {}
    ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
    print(f"   🚨 에스컬레이션: 신규 티켓 {ticket_id} 생성")
    return {"ticket_id": ticket_id}


def human_review(state: EmailState) -> dict:
    """사람 담당자의 답변을 기다린다 (interrupt).

    재개(resume) 시 이 노드는 처음부터 다시 실행되므로, 티켓 생성 같은 부수효과는
    앞 노드(escalate)에 두고 여기에는 interrupt만 둔다.
    """
    cls = state.get("classification", {})
    human_reply = interrupt(
        {
            "ticket_id": state["ticket_id"],
            "urgency": cls.get("urgency"),
            "summary": cls.get("summary"),
            "email": state["email"],
            "history": state.get("history", []),
        }
    )
    return {"reply": human_reply}


def send_human_reply(state: EmailState) -> dict:
    print(f"   👩‍💼 담당자 답장 발송 ({state['ticket_id']}):\n{indent(state['reply'])}")
    return {
        "outcome": "escalated",
        "history": [{"role": f"agent(human, {state['ticket_id']})", "content": state["reply"]}],
    }


def indent(text: str) -> str:
    return "\n".join("      │ " + line for line in text.splitlines())


# ──────────────────────────────────────────────────────────────
# 그래프 구성
# ──────────────────────────────────────────────────────────────
def build_graph(checkpointer=None):
    builder = StateGraph(EmailState)
    builder.add_node("load_thread", load_thread)
    builder.add_node("classify", classify)
    builder.add_node("mark_spam", mark_spam)
    builder.add_node("auto_reply", auto_reply)
    builder.add_node("escalate", escalate)
    builder.add_node("human_review", human_review)
    builder.add_node("send_human_reply", send_human_reply)

    builder.add_edge(START, "load_thread")
    builder.add_edge("load_thread", "classify")
    builder.add_conditional_edges("classify", route_email)
    builder.add_edge("mark_spam", END)
    builder.add_edge("escalate", "human_review")
    builder.add_edge("human_review", "send_human_reply")
    builder.add_edge("send_human_reply", END)

    # 실서비스: SqliteSaver / PostgresSaver 등으로 교체하면 스레드 상태가 재시작 후에도 유지됨
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


def process_email(graph, thread_id: str, email: Email, human_reply_fn=None) -> dict:
    """이메일 1건 처리. 에스컬레이션으로 중단되면 human_reply_fn으로 담당자 답변을 받아 재개."""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"email": email}, config)

    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        reply = human_reply_fn(payload) if human_reply_fn else input("담당자 답변 입력> ")
        result = graph.invoke(Command(resume=reply), config)
    return result


# ──────────────────────────────────────────────────────────────
# 데모
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_ascii())  # pip install grandalf 필요

    def simulated_agent(payload: dict) -> str:
        # 데모용: 실제로는 상담원 UI/Slack 등에서 입력받음
        return (
            f"안녕하세요, 지원팀 김지원입니다. [{payload['ticket_id']}]\n"
            "문의 주신 건을 최우선으로 확인 중이며, 1시간 내에 진행 상황을 다시 안내드리겠습니다."
        )

    inbox = [
        ("thread-001", {
            "sender": "promo@win-prize.biz",
            "subject": "축하합니다! 아이폰 당첨",
            "body": "아래 링크를 클릭하고 카드 정보를 입력하면 경품을 받으실 수 있습니다.",
        }),
        ("thread-002", {
            "sender": "minji@client.co.kr",
            "subject": "비밀번호를 잊어버렸어요",
            "body": "로그인이 안 되는데 비밀번호는 어떻게 재설정하나요?",
        }),
        ("thread-003", {
            "sender": "cto@bigcorp.com",
            "subject": "[긴급] 프로덕션 대시보드 전체 접속 불가",
            "body": "오늘 오전 10시부터 전 직원이 대시보드에 접속하지 못하고 있습니다. 500 에러가 발생합니다.",
        }),
        # thread-003 후속 메일 → 같은 티켓으로 추적
        ("thread-003", {
            "sender": "cto@bigcorp.com",
            "subject": "RE: [긴급] 프로덕션 대시보드 전체 접속 불가",
            "body": "아직도 복구가 안 됐습니다. 예상 복구 시간을 알려주세요.",
        }),
        # thread-002 후속 메일 → 이전 맥락을 참고해 자동 응답
        ("thread-002", {
            "sender": "minji@client.co.kr",
            "subject": "RE: 비밀번호를 잊어버렸어요",
            "body": "감사합니다, 해결됐어요! 혹시 청구서는 어디서 받을 수 있나요?",
        }),
    ]

    for thread_id, email in inbox:
        result = process_email(graph, thread_id, email, simulated_agent)
        print(f"   ✅ 결과: {result['outcome']}")

    # 스레드별 누적 상태 확인
    print("\n=== thread-003 누적 이력 ===")
    state = graph.get_state({"configurable": {"thread_id": "thread-003"}}).values
    print(f"ticket_id={state['ticket_id']}")
    for h in state["history"]:
        print(f" - [{h['role']}] {h['content'][:60]}")

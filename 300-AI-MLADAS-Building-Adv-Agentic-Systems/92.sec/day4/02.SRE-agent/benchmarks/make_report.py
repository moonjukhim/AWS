#!/usr/bin/env python3
"""Build benchmarks/RESULTS.md from the JSON files written by context_benchmark.py."""

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
BEFORE, AFTER = "sre_agent_before", "sre_agent"

# Claude Haiku 4.5 list prices (USD per 1M tokens). Bedrock bills separately - estimate only.
PRICE_IN, PRICE_OUT = 1.00, 5.00
PRICE_CACHE_WRITE, PRICE_CACHE_READ = PRICE_IN * 1.25, PRICE_IN * 0.10
ROLE_ORDER = [
    "supervisor_planning", "metrics_agent", "logs_agent", "kubernetes_agent",
    "runbooks_agent", "executive_summary", "supervisor_other",
]


def load(mode):
    path = RESULTS / f"context_benchmark_{mode}.json"
    return json.loads(path.read_text(encoding="utf-8"))["runs"] if path.exists() else None


def pct(before, after):
    if not before:
        return "-"
    return f"{(after - before) / before * 100:+.1f}%"


def row(label, b, a, fmt="{:,}"):
    return f"| {label} | {fmt.format(b)} | {fmt.format(a)} | {pct(b, a)} |"


def total_input(call):
    """Provider-reported input incl. cache read/write (Bedrock excludes them from input_tokens)."""
    return call.get("api_input_tokens", 0) + call.get("api_cache_read", 0) + call.get("api_cache_write", 0)


def cost(calls):
    return sum(
        c.get("api_input_tokens", 0) * PRICE_IN
        + c.get("api_cache_write", 0) * PRICE_CACHE_WRITE
        + c.get("api_cache_read", 0) * PRICE_CACHE_READ
        + c.get("api_output_tokens", 0) * PRICE_OUT
        for c in calls
    ) / 1_000_000


def per_turn_role(calls, key):
    table = defaultdict(int)
    for c in calls:
        table[(c["turn"], c["role"])] += key(c)
    return table


def turn_role_table(runs, key, title_unit):
    b_tab, a_tab = per_turn_role(runs[BEFORE]["calls"], key), per_turn_role(runs[AFTER]["calls"], key)
    lines = [f"| 턴 | 호출 주체 | 이전 ({title_unit}) | 개선 ({title_unit}) | 변화 |", "|---|---|---:|---:|---:|"]
    turns = sorted({t for t, _ in b_tab} | {t for t, _ in a_tab})
    for t in turns:
        for role in ROLE_ORDER:
            b, a = b_tab.get((t, role)), a_tab.get((t, role))
            if b is None and a is None:
                continue
            lines.append(
                f"| {t} | {role} | {'-' if b is None else f'{b:,}'} | {'-' if a is None else f'{a:,}'} | "
                f"{pct(b, a) if b is not None and a is not None else '실행 안 됨' if a is None else '새로 실행'} |"
            )
    return "\n".join(lines)


def offline_section(runs):
    b, a = runs[BEFORE], runs[AFTER]
    bc, ac = b["calls"], a["calls"]

    def s(calls, key):
        return sum(c.get(key, 0) for c in calls)

    planning_b = [c for c in bc if c["role"] == "supervisor_planning" and c["turn"] == 1]
    planning_a = [c for c in ac if c["role"] == "supervisor_planning" and c["turn"] == 1]
    first_calls = []
    for calls, label in [(bc, "이전"), (ac, "개선")]:
        seen = set()
        for c in calls:
            if c["role"].endswith("_agent") and (c["turn"], c["role"]) not in seen:
                seen.add((c["turn"], c["role"]))
                first_calls.append((label, c))

    out = [
        "## 1. 통제 실험 (offline, 스크립트 LLM)",
        "",
        "두 버전이 **같은 계획·같은 도구 호출·같은 답변**을 하도록 고정한 결과입니다. "
        "차이는 오직 코드가 LLM에 무엇을 보내는가에서만 나옵니다. "
        "토큰 수는 `tiktoken cl100k` 기준 **근사치**(같은 요청에서 Bedrock 실측이 21~28% 더 큼)로, 버전 간 상대 비교용입니다.",
        "",
        "| 지표 | 이전 | 개선 | 변화 |",
        "|---|---:|---:|---:|",
        row("LLM 호출 수", len(bc), len(ac)),
        row("LLM 입력 토큰 합계 (근사)", s(bc, "input_tokens_est"), s(ac, "input_tokens_est")),
        row("단일 호출 최대 입력 (근사)", max(c["input_tokens_est"] for c in bc), max(c["input_tokens_est"] for c in ac)),
        row("입력 중 도구 결과 토큰 (근사)", s(bc, "tool_result_tokens"), s(ac, "tool_result_tokens")),
        row("캐시 체크포인트가 붙은 호출", sum(c["cache_marked"] for c in bc), sum(c["cache_marked"] for c in ac)),
        row("메모리 조회 API 호출", b["memory"]["retrieve_calls"], a["memory"]["retrieve_calls"]),
        row("메모리 조회로 받은 레코드 수", b["memory"]["records_returned"], a["memory"]["records_returned"]),
        row("메모리 이벤트 저장 (create_event)", b["memory"]["create_event_calls"], a["memory"]["create_event_calls"]),
        "",
        "### 1-1. 턴·호출 주체별 입력 토큰 (근사)",
        "",
        turn_role_table(runs, lambda c: c["input_tokens_est"], "토큰"),
        "",
        "### 1-2. 슈퍼바이저 계획 단계 구성 (1턴)",
        "",
        "| 구성 요소 | 이전 | 개선 |",
        "|---|---:|---:|",
        f"| LLM 호출 수 | {len(planning_b)} | {len(planning_a)} |",
        f"| 도구 정의 토큰 (호출당) | {planning_b[0]['tools_tokens']:,} | {planning_a[0]['tools_tokens']:,} |",
        f"| system 토큰 (호출당) | {planning_b[0]['system_tokens']:,} | {planning_a[0]['system_tokens']:,} |",
        f"| messages 토큰 (마지막 호출) | {planning_b[-1]['message_tokens']:,} | {planning_a[-1]['message_tokens']:,} |",
        f"| 계획 단계 입력 합계 | {sum(c['input_tokens_est'] for c in planning_b):,} | {sum(c['input_tokens_est'] for c in planning_a):,} |",
        f"| system에 캐시 체크포인트 | {'있음' if planning_b[0]['cache_marked'] else '없음'} | {'있음' if planning_a[0]['cache_marked'] else '없음'} |",
        "",
        "이전 버전의 system 토큰에는 정적 슈퍼바이저 프롬프트에 더해 **메모리 원본 JSON(인프라 지식 50건, 들여쓰기 4칸)**이 들어 있어 요청마다 바뀝니다. "
        "개선 버전은 system을 정적 내용만으로 고정하고, 질문·메모리(텍스트만 10건 이하)는 human 메시지로 옮겼습니다.",
        "",
        "### 1-3. 전문 에이전트 첫 호출의 입력 (격리 효과)",
        "",
        "각 전문 에이전트가 작업을 시작할 때 받는 입력입니다. 이전 버전은 앞선 에이전트들의 도구 호출·결과 원본이 그대로 누적됩니다.",
        "",
        "| 버전 | 턴 | 에이전트 | 메시지 수 | 입력 토큰 (근사) |",
        "|---|---|---|---:|---:|",
    ]
    for label, c in first_calls:
        out.append(f"| {label} | {c['turn']} | {c['role']} | {c['n_messages']} | {c['input_tokens_est']:,} |")
    out += [
        "",
        "개선 버전은 메시지 수가 항상 2개(system + 과제)로 고정되고, 입력이 앞선 에이전트 수에 비례해 늘지 않습니다. "
        "반대로 **첫 번째로 실행되는 에이전트**(1턴 metrics, 2턴 kubernetes)는 개선 후 조금 커졌습니다. "
        "이전 버전에서 빠져 있던 메모리 인프라 지식(텍스트 10건 이하)과, 이름 오타가 고쳐져 새로 붙은 전역 검색 도구 정의(약 100토큰)가 추가됐기 때문입니다.",
    ]
    return "\n".join(out)


def live_section(runs):
    b, a = runs[BEFORE], runs[AFTER]
    bc, ac = b["calls"], a["calls"]

    def s(calls, key):
        return sum(c.get(key, 0) for c in calls)

    def t1(calls):
        return [c for c in calls if c["turn"] == 1]

    out = [
        "## 2. 실제 실행 (Amazon Bedrock, Claude Haiku 4.5)",
        "",
        "실제 모델이 계획과 도구 호출을 스스로 결정하므로 두 버전의 실행 경로가 다를 수 있습니다. "
        "토큰 값은 Bedrock이 응답에 보고한 실측치입니다. "
        "총 입력 = `input_tokens + cache_read + cache_write` (Bedrock의 `input_tokens`는 캐시분을 제외).",
        "",
        "### 2-1. 전체 세션 (3턴)",
        "",
        "| 지표 | 이전 | 개선 | 변화 |",
        "|---|---:|---:|---:|",
        row("LLM 호출 수", len(bc), len(ac)),
        row("총 입력 토큰 (실측)", sum(total_input(c) for c in bc), sum(total_input(c) for c in ac)),
        row("  └ 캐시 없이 처리된 입력", s(bc, "api_input_tokens"), s(ac, "api_input_tokens")),
        row("  └ 캐시 읽기", s(bc, "api_cache_read"), s(ac, "api_cache_read")),
        row("  └ 캐시 쓰기", s(bc, "api_cache_write"), s(ac, "api_cache_write")),
        row("출력 토큰", s(bc, "api_output_tokens"), s(ac, "api_output_tokens")),
        row("단일 호출 최대 입력", max(total_input(c) for c in bc), max(total_input(c) for c in ac)),
        row("max_tokens(4096) 도달 응답 수", sum(c.get("api_output_tokens", 0) >= 4096 for c in bc), sum(c.get("api_output_tokens", 0) >= 4096 for c in ac)),
        row("실행 시간 (초)", b["elapsed_seconds"], a["elapsed_seconds"], "{:,.1f}"),
        row("예상 비용 (USD, Haiku 4.5 정가 기준)", cost(bc), cost(ac), "${:.4f}"),
        "",
        "### 2-2. 턴별 실행 경로",
        "",
        "| 턴 | 질문 | 이전: 호출된 에이전트 | 개선: 호출된 에이전트 |",
        "|---|---|---|---|",
    ]
    for tb, ta in zip(b["turns"], a["turns"]):
        query = {1: "web-service 5xx·지연 원인", 2: "DB 파드가 원인인지 (후속)", 3: "이것을 해결할 런북·에스컬레이션 (후속)"}[tb["turn"]]
        out.append(f"| {tb['turn']} | {query} | {', '.join(tb['agents_invoked'])} | {', '.join(ta['agents_invoked'])} |")

    b1, a1 = t1(bc), t1(ac)
    same_path = b["turns"][0]["agents_invoked"] and set(b["turns"][0]["agents_invoked"]) == set(a["turns"][0]["agents_invoked"])
    out += [
        "",
        "### 2-3. 1턴 직접 비교" + (" (두 버전 모두 같은 4개 에이전트 호출)" if same_path else ""),
        "",
        "| 지표 | 이전 | 개선 | 변화 |",
        "|---|---:|---:|---:|",
        row("LLM 호출 수", len(b1), len(a1)),
        row("총 입력 토큰 (실측)", sum(total_input(c) for c in b1), sum(total_input(c) for c in a1)),
        row("출력 토큰", s(b1, "api_output_tokens"), s(a1, "api_output_tokens")),
        row("예상 비용 (USD)", cost(b1), cost(a1), "${:.4f}"),
        "",
        "### 2-4. 턴·호출 주체별 총 입력 토큰 (실측)",
        "",
        turn_role_table(runs, total_input, "토큰"),
        "",
        "### 2-5. 프롬프트 캐싱",
        "",
        "| 버전 | 턴 | 호출 주체 | 캐시 쓰기 | 캐시 읽기 | 캐시 없이 처리 |",
        "|---|---|---|---:|---:|---:|",
    ]
    for label, calls in [("이전", bc), ("개선", ac)]:
        for c in calls:
            if c["role"] == "supervisor_planning" and c is next(x for x in calls if x["turn"] == c["turn"] and x["role"] == "supervisor_planning"):
                out.append(
                    f"| {label} | {c['turn']} | {c['role']} | {c.get('api_cache_write', 0):,} | "
                    f"{c.get('api_cache_read', 0):,} | {c.get('api_input_tokens', 0):,} |"
                )
    agent_cache = sum(c.get("api_cache_read", 0) + c.get("api_cache_write", 0) for c in ac if c["role"].endswith("_agent"))
    out += [
        "",
        f"전문 에이전트 호출의 캐시 읽기+쓰기 합계(개선): {agent_cache:,} 토큰. "
        "전문 에이전트의 정적 접두사(도구 정의 + system ≈ 3.3K 토큰)는 Haiku 4.5의 최소 캐시 크기 4,096 토큰에 못 미쳐 캐시되지 않습니다.",
    ]
    return "\n".join(out)


def ablation_section(ablation, live):
    cum = ablation["cumulative"]
    loo = {v["removed"]: v for v in ablation["leave_one_out"]}
    labels = {c["key"]: c for c in ablation["changes"]}
    base, full = cum[0]["input_tokens_est"], cum[-1]["input_tokens_est"]
    out = [
        "## 개선 항목별 기여도 (절제 실험)",
        "",
        "통제 실험(offline)에서 개선 버전(`sre_agent`)의 변경을 원본 구현(`sre_agent_before`의 해당 함수·설정)으로 되돌린 변형을 돌렸습니다(`benchmarks/ablation.py`). "
        f"모든 변경을 되돌린 변형의 입력은 {base:,}토큰으로 실제 원본 실행과 거의 같고, 모든 변형에서 실행 경로가 같습니다.",
        "",
        "- **차례로 적용**: 모두 되돌린 상태에서 변경을 표의 순서대로 하나씩 적용. 감소량을 모두 더하면 전체 감소량과 같지만, 순서에 따라 값이 달라집니다.",
        "- **하나만 빼기**: 개선 버전에서 그 변경만 되돌렸을 때 늘어나는 양. 다른 변경과 효과가 겹치면 두 값이 다릅니다.",
        "",
        "| 변경 | 내용 | 차례로 적용 시 감소 (토큰, 근사) | 비중 | 하나만 빼면 증가 | 메모리 조회 (차례로 적용 후) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for prev, cur in zip(cum, cum[1:]):
        key = cur["added"]
        saved = prev["input_tokens_est"] - cur["input_tokens_est"]
        out.append(
            f"| {labels[key]['label']} | {labels[key]['detail']} | {saved:,} | {saved / (base - full):.1%} | "
            f"{loo[key]['input_tokens_est'] - full:+,} | {cur['memory_retrieve_calls']}회 / {cur['memory_records_returned']}건 |"
        )
    out += ["", f"합계: {base:,} → {full:,} (−{base - full:,}토큰, {(full - base) / base:+.1%}).", ""]
    if live and AFTER in live:
        calls = live[AFTER]["calls"]
        read = sum(c.get("api_cache_read", 0) for c in calls)
        saved_usd = read * (PRICE_IN - PRICE_CACHE_READ) / 1_000_000
        out += [
            "**프롬프트 캐싱**은 보내는 토큰 수를 바꾸지 않아 위 표에서 거의 0입니다. 대신 단가를 낮춥니다. "
            f"Bedrock 실측 개선 버전 세션에서 캐시 읽기 {read:,}토큰 → 약 ${saved_usd:.4f} 절감 "
            f"(캐싱이 없었다면 ${cost(calls) + saved_usd:.4f}, 실제 ${cost(calls):.4f}). "
            "계획 단계의 정적 프롬프트만 캐시됐고, 전문 에이전트는 최소 캐시 크기에 못 미쳐 캐시되지 않았습니다.",
            "",
        ]
    return "\n".join(out)


def main():
    offline, live = load("offline"), load("bedrock")
    ablation_path = RESULTS / "ablation_offline.json"
    ablation = json.loads(ablation_path.read_text(encoding="utf-8")) if ablation_path.exists() else None
    parts = [
        "# SRE 에이전트 컨텍스트 엔지니어링 개선 전/후 측정 결과",
        "",
        "- 이전 코드: `sre_agent_before/` (원본 그대로 보존)",
        "- 개선 코드: `sre_agent/`",
        "- 측정 스크립트: `benchmarks/context_benchmark.py`, 보고서 생성: `benchmarks/make_report.py`",
        "- 원본 데이터: `benchmarks/results/*.json` (LLM 호출 단위 기록)",
        "",
        "**시나리오** — 한 세션에서 3턴 대화: ① web-service 5xx·지연 원인 조사 → ② DB 파드가 원인인지 후속 질문 → ③ 해결 런북·에스컬레이션 요청. "
        "도구는 Gateway와 같은 OpenAPI 스펙으로 만들고 실제 백엔드 FastAPI 앱이 응답하며, AgentCore Memory는 실제 전략 출력 형식(선호 JSON·시맨틱 텍스트·요약 XML)의 레코드 74건이 들어 있는 메모리 내 저장소로 대체했습니다.",
        "",
    ]
    if offline and live and BEFORE in live and AFTER in live:
        ob, oa = offline[BEFORE]["calls"], offline[AFTER]["calls"]
        lb, la = live[BEFORE]["calls"], live[AFTER]["calls"]
        lb1 = [c for c in lb if c["turn"] == 1]
        la1 = [c for c in la if c["turn"] == 1]
        est = lambda calls: sum(c["input_tokens_est"] for c in calls)  # noqa: E731
        real = lambda calls: sum(total_input(c) for c in calls)  # noqa: E731
        parts += [
            "## 요약",
            "",
            "| 측정 | 이전 | 개선 | 변화 |",
            "|---|---:|---:|---:|",
            row("통제 실험: LLM 입력 토큰 (근사, 3턴)", est(ob), est(oa)),
            row("통제 실험: 메모리 조회 API 호출", offline[BEFORE]["memory"]["retrieve_calls"], offline[AFTER]["memory"]["retrieve_calls"]),
            row("Bedrock 실측: 1턴 입력 토큰 (같은 에이전트 4개)", real(lb1), real(la1)),
            row("Bedrock 실측: 3턴 세션 전체 입력 토큰", real(lb), real(la)),
            row("Bedrock 실측: 3턴 세션 예상 비용 (USD)", cost(lb), cost(la), "${:.4f}"),
            row("Bedrock 실측: 실행 시간 (초)", live[BEFORE]["elapsed_seconds"], live[AFTER]["elapsed_seconds"], "{:,.1f}"),
            "",
            "가장 공정한 비교는 **통제 실험**(같은 결정을 강제)과 **Bedrock 1턴**(두 버전이 같은 에이전트를 호출)입니다. "
            "세션 전체 수치에는 2·3턴의 실행 경로 차이(이전 버전 2턴의 도구 호출 반복, 3턴 계획 실패 → 다른 에이전트 실행)도 함께 들어 있습니다(2-2 표).",
            "",
        ]
    if ablation:
        parts += [ablation_section(ablation, live), ""]
    if offline:
        parts += [offline_section(offline), ""]
    if live and BEFORE in live and AFTER in live:
        parts += [live_section(live), ""]
    parts += [(HERE / "NOTES.md").read_text(encoding="utf-8")] if (HERE / "NOTES.md").exists() else []
    (HERE / "RESULTS.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {HERE / 'RESULTS.md'}")


if __name__ == "__main__":
    main()

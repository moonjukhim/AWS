#!/usr/bin/env python3
"""Attribute the improvement to individual changes (ablation, offline mode).

Runs the improved package (`sre_agent`) with some of its changes reverted to the
original implementation taken from `sre_agent_before`, using the same scripted
LLM, tools and memory fixture as context_benchmark.py.

Two views:
  * cumulative - start with every change reverted, then add the changes back one
    at a time in CHANGES order; each step's delta is that change's contribution
    (the deltas sum exactly to the total, but depend on the order).
  * leave-one-out - the full improved version with only one change reverted;
    shows how much is lost if that single change were dropped.

Usage:
    python -X utf8 benchmarks/ablation.py
Writes benchmarks/results/ablation_offline.json
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import context_benchmark as cb  # noqa: E402

CHANGES = [
    ("planning", "계획 단계 재구성", "플래너 ReAct 루프·메모리 재조회 제거, 구조화 출력 1회 호출, 정적 system 분리, 압축 이력 전달"),
    ("memory", "메모리 선택", "인프라 지식 topK 50→10, 관련도 0.5 미만 제외, 응답마다 하던 선호 메모리 100건×2 조회 제거"),
    ("isolation", "에이전트 컨텍스트 격리", "전문 에이전트에 전체 대화 대신 system + 과제 메시지만 전달, 도구 트래픽을 공유 대화에 넣지 않음"),
    ("tool_cap", "도구 결과 상한", "ReAct 루프의 도구 결과를 4,000자로 제한 (pre_model_hook)"),
    ("tool_name", "검색 도구 이름 수정", "전역 검색 도구가 실제로 에이전트에 붙도록 이름 오타 수정"),
    ("caching", "프롬프트 캐싱", "정적 system에 cache_control 체크포인트"),
]
METRICS = [
    "llm_calls", "input_tokens_est", "max_input_tokens_est", "tool_result_tokens_est",
    "memory_retrieve_calls", "memory_records_returned", "est_cache_read_tokens",
]


def apply_reverts(reverts):
    """Patch `sre_agent` so the given changes use the original code. Returns an undo function."""
    import sre_agent.agent_nodes as nodes
    import sre_agent.memory.hooks as hooks
    import sre_agent.supervisor as sup
    import sre_agent_before.agent_nodes as nodes_b
    import sre_agent_before.memory.hooks as hooks_b
    import sre_agent_before.supervisor as sup_b
    from langgraph.prebuilt import create_react_agent
    from sre_agent.constants import SREConstants

    undo = []

    def patch(obj, name, value):
        old = getattr(obj, name)
        undo.append(lambda: setattr(obj, name, old))
        setattr(obj, name, value)

    if "planning" in reverts:
        original_plan = sup_b.SupervisorAgent.create_investigation_plan

        async def create_investigation_plan(self, state):
            # The original planner is a ReAct agent over the memory tools
            if not hasattr(self, "planning_agent"):
                self.planning_agent = (
                    create_react_agent(self.llm, self.memory_tools) if self.memory_tools else None
                )
            return await original_plan(self, state)

        patch(sup.SupervisorAgent, "create_investigation_plan", create_investigation_plan)
    if "memory" in reverts:
        patch(SREConstants.memory, "max_infrastructure_results", 50)
        patch(SREConstants.memory, "min_relevance_score", 0.0)
        patch(hooks.MemoryHookProvider, "on_agent_response", hooks_b.MemoryHookProvider.on_agent_response)
    if "isolation" in reverts:
        patch(nodes.BaseAgentNode, "__call__", nodes_b.BaseAgentNode.__call__)
        # The original __call__ builds its own SREMemoryClient from its module:
        # route it to the benchmark's fake client (set on `nodes` by run_version)
        patch(nodes_b, "SREMemoryClient", lambda *a, **k: nodes.SREMemoryClient(*a, **k))
    if "tool_cap" in reverts:
        patch(SREConstants.context, "max_tool_result_chars", 10**9)
    if "tool_name" in reverts:
        original_config = nodes._load_agent_config
        before_globals = nodes_b._load_agent_config().get("global_tools", [])
        patch(nodes, "_load_agent_config", lambda: {**original_config(), "global_tools": before_globals})
    if "caching" in reverts:
        patch(SREConstants.context, "enable_prompt_caching", False)

    def restore():
        for fn in reversed(undo):
            fn()

    return restore


async def run_variant(reverts, tools):
    restore = apply_reverts(set(reverts))
    try:
        run = await cb.run_version("sre_agent", "offline", "us-east-1", tools)
    finally:
        restore()
    summary = cb.summarize(run)
    by_role = {}
    for c in run["calls"]:
        by_role[c["role"]] = by_role.get(c["role"], 0) + c["input_tokens_est"]
    return {
        "reverted": sorted(reverts),
        **{m: summary[m] for m in METRICS},
        "input_by_role": by_role,
        "agents_invoked": [t["agents_invoked"] for t in run["turns"]],
    }


def block_real_memory():
    """Fail loudly instead of creating AgentCore Memory resources in AWS."""
    import sre_agent.memory.client as client_after
    import sre_agent_before.memory.client as client_before

    class NoRealMemoryClient:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("ablation must not create a real AgentCore MemoryClient")

    client_after.MemoryClient = NoRealMemoryClient
    client_before.MemoryClient = NoRealMemoryClient


def main():
    if sys.flags.utf8_mode == 0:
        raise SystemExit("Run with UTF-8 mode: python -X utf8 benchmarks/ablation.py")
    block_real_memory()
    tools = cb.build_gateway_tools()
    keys = [k for k, _, _ in CHANGES]

    async def go():
        cumulative = []
        for i in range(len(keys) + 1):
            variant = await run_variant(keys[i:], tools)
            variant["added"] = keys[i - 1] if i else None
            cumulative.append(variant)
            print(f"cumulative +{variant['added']}: input_est={variant['input_tokens_est']:,}", flush=True)
        leave_one_out = []
        for key in keys:
            variant = await run_variant([key], tools)
            variant["removed"] = key
            leave_one_out.append(variant)
            print(f"without {key}: input_est={variant['input_tokens_est']:,}", flush=True)
        return cumulative, leave_one_out

    cumulative, leave_one_out = asyncio.run(go())
    out = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "offline",
        "changes": [{"key": k, "label": label, "detail": detail} for k, label, detail in CHANGES],
        "cumulative": cumulative,
        "leave_one_out": leave_one_out,
    }
    path = cb.RESULTS_DIR / "ablation_offline.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()

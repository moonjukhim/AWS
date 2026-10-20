#!/usr/bin/env python3
"""
Before/after context-engineering benchmark for the SRE multi-agent system.

Runs the same multi-turn investigation session against two copies of the agent:
  - sre_agent_before : original code (kept unchanged)
  - sre_agent        : context-engineering improvements applied

Both versions run their real graph / supervisor / agent-node / memory-hook code.
Only the external services are replaced so the runs are comparable:
  - MCP Gateway tools -> built from backend/openapi_specs, answered in-process by the
                         real backend FastAPI apps (backend/servers/*_server.py)
  - AgentCore Memory  -> in-memory store pre-filled with records shaped like the
                         three AgentCore strategy outputs (preference JSON,
                         semantic plain text, summary XML)
  - LLM               -> mode "offline": scripted model making identical decisions
                         for both versions (deterministic, free)
                         mode "bedrock": the real Bedrock model (real usage + cache)

Every LLM call is recorded: what was sent (tools / system / messages) and, in
bedrock mode, the provider-reported input/output/cache tokens.

Usage:
    python benchmarks/context_benchmark.py --mode offline
    python benchmarks/context_benchmark.py --mode bedrock --region us-east-1
"""

import argparse
import asyncio
import copy
import hashlib
import importlib
import json
import logging
import sys
import time
import types
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SERVERS_DIR = ROOT / "backend" / "servers"
SPECS_DIR = ROOT / "backend" / "openapi_specs"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(ROOT))

import tiktoken  # noqa: E402
import yaml  # noqa: E402
from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402
from langchain_core.language_models.chat_models import BaseChatModel  # noqa: E402
from langchain_core.messages import (  # noqa: E402
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult  # noqa: E402
from langchain_core.tools import StructuredTool  # noqa: E402
from langchain_core.utils.function_calling import convert_to_openai_tool  # noqa: E402

VERSIONS = ["sre_agent_before", "sre_agent"]
API_KEY = "benchmark-api-key"
USER_ID = "bench-user"
ENCODER = tiktoken.get_encoding("cl100k_base")

# Minimum cacheable prefix for Claude Haiku 4.5 (Bedrock prompt caching docs / slide 24)
MIN_CACHE_TOKENS = 4096

# ---------------------------------------------------------------------------
# Scenario: one interactive session, three turns (history accumulates)
# ---------------------------------------------------------------------------
TURNS = [
    {
        "query": "The web-service in production is returning 5xx errors and latency is high. What is going on?",
        "plan": {
            "steps": [
                "Check web-service latency and error-rate metrics",
                "Analyze web-service error logs for the failure pattern",
                "Inspect web-service and database pods and recent cluster events",
            ],
            "agents_sequence": ["metrics_agent", "logs_agent", "kubernetes_agent"],
            "complexity": "simple",
            "auto_execute": True,
            "reasoning": "Symptoms span performance, application errors and infrastructure.",
        },
    },
    {
        "query": "Is the database pod the root cause? Check its events and memory usage.",
        "plan": {
            "steps": [
                "Inspect database pod status, events and resource usage",
                "Correlate database errors in the application logs",
            ],
            "agents_sequence": ["kubernetes_agent", "logs_agent"],
            "complexity": "simple",
            "auto_execute": True,
            "reasoning": "Follow-up focused on the database pod.",
        },
    },
    {
        "query": "Give me the runbook steps to remediate this and who I should escalate to.",
        "plan": {
            "steps": ["Find the remediation runbook and escalation procedure"],
            "agents_sequence": ["runbooks_agent"],
            "complexity": "simple",
            "auto_execute": True,
            "reasoning": "Operational procedure request.",
        },
    },
]

# Tool calls the scripted model makes for each specialist (identical in both versions)
AGENT_TOOL_SCRIPT = {
    "metrics-api": [
        ("get_performance_metrics", {"service": "web-service"}),
        ("get_error_rates", {"service": "web-service"}),
        ("get_resource_metrics", {"service": "web-service"}),
    ],
    "logs-api": [
        ("get_error_logs", {"service": "web-service"}),
        ("search_logs", {"pattern": "database"}),
        ("analyze_log_patterns", {}),
    ],
    "k8s-api": [
        ("get_pod_status", {"namespace": "production"}),
        ("get_cluster_events", {"namespace": "production"}),
        ("get_resource_usage", {"namespace": "production"}),
    ],
    "runbooks-api": [
        ("search_runbooks", {"query": "database"}),
        ("get_escalation_procedures", {}),
        ("get_common_resolutions", {}),
    ],
}

SEARCH_TOOL_NAME = "x_amz_bedrock_agentcore_search"


# ---------------------------------------------------------------------------
# Tools: OpenAPI specs -> LangChain tools answered by the real backend apps
# ---------------------------------------------------------------------------
def _prepare_logs_fixture() -> Path:
    """Rebuild backend/data/logs_data in a fixture dir.

    The *.log demo files are excluded by .gitignore, but their contents are kept in
    backend/data/all_data_dump.txt; extract them without touching backend/data.
    """
    source_dir = ROOT / "backend" / "data" / "logs_data"
    fixture_dir = FIXTURES_DIR / "logs_data"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    for json_file in source_dir.glob("*.json"):
        (fixture_dir / json_file.name).write_bytes(json_file.read_bytes())

    dump = (ROOT / "backend" / "data" / "all_data_dump.txt").read_text(encoding="utf-8")
    lines = dump.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("FILE: data/logs_data/") and lines[i].endswith(".log"):
            name = lines[i].split("/")[-1]
            body = []
            i += 2  # skip the ===== line under the header
            while i < len(lines) and not lines[i].startswith("Processing: "):
                body.append(lines[i])
                i += 1
            (fixture_dir / name).write_text("\n".join(body).strip() + "\n", encoding="utf-8")
        else:
            i += 1
    return fixture_dir


def _load_backend_apps() -> Dict[str, Any]:
    """Import backend FastAPI apps with the API-key lookup stubbed out."""
    stub = types.ModuleType("retrieve_api_key")
    stub.retrieve_api_key = lambda *_args, **_kwargs: API_KEY
    sys.modules["retrieve_api_key"] = stub
    sys.path.insert(0, str(SERVERS_DIR))
    from fastapi.testclient import TestClient

    apps = {}
    for target, module_name in [
        ("k8s-api", "k8s_server"),
        ("logs-api", "logs_server"),
        ("metrics-api", "metrics_server"),
        ("runbooks-api", "runbooks_server"),
    ]:
        module = importlib.import_module(module_name)
        if module_name == "logs_server":
            module.DATA_PATH = _prepare_logs_fixture()
        apps[target] = TestClient(module.app)
    return apps


def build_gateway_tools() -> List[StructuredTool]:
    """Recreate the Gateway's MCP tool list (target___operationId) from the OpenAPI specs."""
    clients = _load_backend_apps()
    spec_files = {
        "k8s-api": "k8s_api.yaml.template",
        "logs-api": "logs_api.yaml.template",
        "metrics-api": "metrics_api.yaml.template",
        "runbooks-api": "runbooks_api.yaml.template",
    }
    tools: List[StructuredTool] = []
    for target, filename in spec_files.items():
        spec = yaml.safe_load((SPECS_DIR / filename).read_text(encoding="utf-8"))
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                params = op.get("parameters", [])
                schema = {
                    "type": "object",
                    "properties": {
                        p["name"]: {
                            **p.get("schema", {"type": "string"}),
                            "description": p.get("description", ""),
                        }
                        for p in params
                    },
                    "required": [p["name"] for p in params if p.get("required")],
                }
                description = "\n".join(
                    s for s in [op.get("summary", ""), op.get("description", "")] if s
                )
                tools.append(
                    StructuredTool(
                        name=f"{target}___{op['operationId']}",
                        description=description,
                        args_schema=schema,
                        func=_make_tool_func(clients[target], path, params),
                    )
                )
    tools.append(
        StructuredTool(
            name=SEARCH_TOOL_NAME,
            description=(
                "A special tool that returns a trimmed down list of tools given a "
                "context. Use this tool only when there are many tools available and "
                "you want to get a subset that matches the provided context."
            ),
            args_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "search query"}
                },
                "required": ["query"],
            },
            func=lambda query="": json.dumps(
                [t.name for t in tools if query.lower() in t.name.lower()]
            ),
        )
    )
    return tools


def _make_tool_func(client, path: str, params: List[Dict[str, Any]]):
    path_params = {p["name"] for p in params if p.get("in") == "path"}

    def call(**kwargs) -> str:
        url = path
        for name in path_params:
            url = url.replace("{" + name + "}", str(kwargs.pop(name, "")))
        query = {k: v for k, v in kwargs.items() if v is not None}
        response = client.get(url, params=query, headers={"X-API-Key": API_KEY})
        return response.text

    return call


# ---------------------------------------------------------------------------
# Memory: in-memory AgentCore store with realistic record shapes
# ---------------------------------------------------------------------------
def _memory_fixture() -> Dict[str, List[Dict[str, Any]]]:
    created = datetime(2026, 9, 1, tzinfo=timezone.utc)
    services = [
        "web-service", "database", "api-gateway", "auth-service",
        "web-app", "redis-cache", "order-service", "notification-service",
        "inventory-service", "search-service",
    ]
    facts = [
        "{svc} depends on postgres-primary in namespace production; connection pool size is 20.",
        "{svc} p95 latency baseline is 180ms; alerts fire above 500ms for 5 minutes.",
        "{svc} was OOMKilled twice last month when memory limit was 512Mi; limit raised to 1Gi.",
        "{svc} error rate baseline is 0.3%; spikes usually follow a deployment rollout.",
        "{svc} runs 3 replicas behind the api-gateway with HPA min 3 max 10.",
    ]
    infra = []
    for i in range(60):
        svc = services[i % len(services)]
        infra.append(
            {
                "memoryRecordId": f"mem-infra-{i:03d}",
                "content": {"text": facts[i % len(facts)].format(svc=svc)},
                "namespaces": [f"/sre/infrastructure/{USER_ID}/sess-{i % 7}"],
                "memoryStrategyId": "infrastructure_knowledge-abc123",
                "createdAt": created,
                "score": round(0.95 - (i * 0.012), 3),
            }
        )
    prefs = [
        {"context": "Escalation", "preference": "Escalate database incidents to dba-oncall@example.com, then sre-lead@example.com after 15 minutes", "categories": ["escalation"]},
        {"context": "Notification", "preference": "Notify #sre-incidents Slack channel for P1/P2; email for P3", "categories": ["notification"]},
        {"context": "Workflow", "preference": "Always include kubectl commands in remediation steps", "categories": ["workflow"]},
        {"context": "Communication", "preference": "Executive summary first, technical details after", "categories": ["communication"]},
        {"context": "Notification", "preference": "Quiet hours 22:00-07:00 KST except P1", "categories": ["notification"]},
        {"context": "Workflow", "preference": "Prefer metrics evidence before log evidence in reports", "categories": ["workflow"]},
    ]
    preferences = [
        {
            "memoryRecordId": f"mem-pref-{i:03d}",
            "content": {"text": json.dumps(p)},
            "namespaces": [f"/sre/users/{USER_ID}/preferences"],
            "memoryStrategyId": "user_preferences-def456",
            "createdAt": created,
            "score": round(0.9 - i * 0.05, 3),
        }
        for i, p in enumerate(prefs)
    ]
    investigations = []
    for i in range(8):
        svc = services[i % len(services)]
        text = (
            f'<summary><topic name="{svc} incident {i + 1}">'
            f"Investigated elevated 5xx errors on {svc}. Metrics showed p95 latency rising "
            f"from 180ms to 2.4s. Logs contained repeated 'connection pool exhausted' and "
            f"'timeout waiting for postgres-primary' errors. Kubernetes events showed the "
            f"database pod restarting after OOMKilled. Resolution: increased database memory "
            f"limit to 2Gi, raised connection pool to 40, restarted {svc} pods. Escalated "
            f"to dba-oncall. Follow-up: add alert on pool saturation."
            f"</topic></summary>"
        )
        investigations.append(
            {
                "memoryRecordId": f"mem-inv-{i:03d}",
                "content": {"text": text},
                "namespaces": [f"/sre/investigations/{USER_ID}/sess-{i}"],
                "memoryStrategyId": "investigation_summaries-ghi789",
                "createdAt": created,
                "score": round(0.88 - i * 0.08, 3),
            }
        )
    return {"preferences": preferences, "infrastructure": infra, "investigations": investigations}


class FakeAgentCoreMemory:
    """Stands in for bedrock_agentcore.memory.MemoryClient (the inner client)."""

    def __init__(self):
        self.records = _memory_fixture()
        self.stats = {"retrieve_calls": 0, "records_returned": 0, "create_event_calls": 0}

    def retrieve_memories(self, memory_id, namespace, query, top_k=10, **_):
        self.stats["retrieve_calls"] += 1
        if namespace.startswith("/sre/users/"):
            pool = self.records["preferences"]
        elif namespace.startswith("/sre/infrastructure/"):
            pool = self.records["infrastructure"]
        elif namespace.startswith("/sre/investigations/"):
            pool = self.records["investigations"]
        else:
            pool = []
        result = copy.deepcopy(sorted(pool, key=lambda r: -r["score"])[:top_k])
        self.stats["records_returned"] += len(result)
        return result

    def create_event(self, **_):
        self.stats["create_event_calls"] += 1
        return {"eventId": f"evt-{uuid.uuid4().hex[:8]}"}


def make_fake_memory_client_cls(base_cls, store: FakeAgentCoreMemory):
    """Subclass the package's SREMemoryClient so its real methods run on the fake store."""

    class BenchmarkMemoryClient(base_cls):
        def __init__(self, *args, **kwargs):
            self.memory_id = "benchmark-memory"
            self.memory_name = "benchmark"
            self.region = kwargs.get("region", "us-east-1")
            self.client = store

    return BenchmarkMemoryClient


# ---------------------------------------------------------------------------
# LLM call recording
# ---------------------------------------------------------------------------
def _tok(text: str) -> int:
    return len(ENCODER.encode(text, disallowed_special=()))


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            parts.append(block.get("text") or json.dumps(block, default=str))
    return "\n".join(parts)


def _has_cache_marker(message: BaseMessage) -> bool:
    return isinstance(message.content, list) and any(
        isinstance(b, dict) and (b.get("cache_control") or b.get("cachePoint"))
        for b in message.content
    )


def _tool_names(tools: List[Dict[str, Any]]) -> List[str]:
    names = []
    for t in tools or []:
        names.append(t.get("name") or t.get("function", {}).get("name", "?"))
    return names


class CallRecorder(BaseCallbackHandler):
    """Records the size of every LLM request and (if reported) provider token usage."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
        self._by_run: Dict[Any, Dict[str, Any]] = {}
        self.turn = 0

    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        msgs: List[BaseMessage] = messages[0]
        params = kwargs.get("invocation_params") or {}
        tools = params.get("tools") or []
        system_msgs = [m for m in msgs if isinstance(m, SystemMessage)]
        other_msgs = [m for m in msgs if not isinstance(m, SystemMessage)]

        tools_tokens = _tok(json.dumps(tools, default=str)) if tools else 0
        system_tokens = sum(_tok(_content_text(m.content)) for m in system_msgs)
        message_tokens = 0
        tool_result_tokens = 0
        for m in other_msgs:
            n = _tok(_content_text(m.content))
            if isinstance(m, AIMessage) and m.tool_calls:
                n += _tok(json.dumps(m.tool_calls, default=str))
            if isinstance(m, ToolMessage):
                tool_result_tokens += n
            message_tokens += n

        cache_marked = any(_has_cache_marker(m) for m in system_msgs)
        prefix_text = json.dumps(tools, default=str) + "".join(
            _content_text(m.content) for m in system_msgs
        )
        call = {
            "turn": self.turn,
            "role": _classify_call(_tool_names(tools), system_msgs),
            "n_messages": len(msgs),
            "tools": len(tools),
            "tools_tokens": tools_tokens,
            "system_tokens": system_tokens,
            "message_tokens": message_tokens,
            "tool_result_tokens": tool_result_tokens,
            "input_tokens_est": tools_tokens + system_tokens + message_tokens,
            "cache_marked": cache_marked,
            "prefix_hash": hashlib.sha1(prefix_text.encode()).hexdigest()[:12],
            "prefix_tokens_est": tools_tokens + system_tokens,
        }
        self._by_run[run_id] = call
        self.calls.append(call)

    def on_llm_end(self, response, *, run_id, **kwargs):
        call = self._by_run.get(run_id)
        if call is None:
            return
        try:
            message = response.generations[0][0].message
            usage = getattr(message, "usage_metadata", None) or {}
        except (IndexError, AttributeError):
            usage = {}
        if usage:
            details = usage.get("input_token_details", {}) or {}
            call["api_input_tokens"] = usage.get("input_tokens", 0)
            call["api_output_tokens"] = usage.get("output_tokens", 0)
            call["api_cache_read"] = details.get("cache_read", 0) or 0
            call["api_cache_write"] = details.get("cache_creation", 0) or 0


def _classify_call(tool_names: List[str], system_msgs: List[SystemMessage]) -> str:
    if "InvestigationPlan" in tool_names or "retrieve_memory" in tool_names:
        return "supervisor_planning"
    for prefix, role in [
        ("k8s-api", "kubernetes_agent"),
        ("logs-api", "logs_agent"),
        ("metrics-api", "metrics_agent"),
        ("runbooks-api", "runbooks_agent"),
    ]:
        if any(n.startswith(prefix) for n in tool_names):
            return role
    system_text = "".join(_content_text(m.content) for m in system_msgs).lower()
    if "executive summar" in system_text:
        return "executive_summary"
    return "supervisor_other"


# ---------------------------------------------------------------------------
# Scripted LLM (offline mode)
# ---------------------------------------------------------------------------
def _current_turn(messages: List[BaseMessage]) -> Dict[str, Any]:
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            text = _content_text(m.content)
            for turn in reversed(TURNS):
                if turn["query"] in text:
                    return turn
    return TURNS[0]


def _tool_messages_since_last_human(messages: List[BaseMessage]) -> int:
    count = 0
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            break
        if isinstance(m, ToolMessage):
            count += 1
    return count


def _finding_text(agent_prefix: str, turn: Dict[str, Any]) -> str:
    calls = ", ".join(op for op, _ in AGENT_TOOL_SCRIPT[agent_prefix])
    return (
        f"## Findings ({agent_prefix})\n"
        f"Question: {turn['query']}\n\n"
        f"I called {calls}. The web-service p95 latency rose from about 180ms to over "
        "2 seconds and the 5xx error rate climbed above 8%, starting a few minutes after "
        "the database pod began restarting. Error logs repeat 'connection pool exhausted' "
        "and 'timeout waiting for postgres-primary'. The database pod in production shows "
        "OOMKilled restarts and memory usage close to its limit, which drops active "
        "connections and forces the web-service to queue requests.\n\n"
        "### Evidence\n"
        "- Latency and error spikes line up with database restarts\n"
        "- Connection pool saturation messages in web-service logs\n"
        "- Database pod memory near limit with repeated OOMKilled events\n\n"
        "### Recommended actions\n"
        "1. Raise the database memory limit and restart the pod\n"
        "2. Increase the web-service connection pool and add backoff\n"
        "3. Add an alert on connection pool saturation\n"
    )


class ScriptedChatModel(BaseChatModel):
    """Deterministic stand-in LLM: same decisions for both code versions."""

    @property
    def _llm_type(self) -> str:
        return "scripted-benchmark"

    def bind_tools(self, tools, tool_choice=None, **kwargs):
        formatted = [convert_to_openai_tool(t) for t in tools]
        return self.bind(tools=formatted, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        names = _tool_names(kwargs.get("tools") or [])
        turn = _current_turn(messages)
        message = self._respond(messages, names, turn)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _respond(self, messages, names, turn) -> AIMessage:
        def call(name, args):
            return {"name": name, "args": args, "id": f"call_{uuid.uuid4().hex[:10]}", "type": "tool_call"}

        if "InvestigationPlan" in names:
            return AIMessage(content="", tool_calls=[call("InvestigationPlan", turn["plan"])])

        if "retrieve_memory" in names:
            # Original planning prompt mandates three retrieve_memory calls first
            if _tool_messages_since_last_human(messages) == 0:
                return AIMessage(
                    content="",
                    tool_calls=[
                        call("retrieve_memory", {"memory_type": "preference", "query": "user settings communication escalation notification", "actor_id": USER_ID, "max_results": 5}),
                        call("retrieve_memory", {"memory_type": "infrastructure", "query": "web-service database", "actor_id": "sre-agent", "max_results": 10}),
                        call("retrieve_memory", {"memory_type": "investigation", "query": "web-service 5xx latency", "actor_id": USER_ID, "max_results": 5}),
                    ],
                )
            return AIMessage(content=json.dumps(turn["plan"]))

        agent_prefix = next(
            (p for p in AGENT_TOOL_SCRIPT if any(n.startswith(p) for n in names)), None
        )
        if agent_prefix:
            if _tool_messages_since_last_human(messages) == 0:
                return AIMessage(
                    content="",
                    tool_calls=[
                        call(f"{agent_prefix}___{op}", args)
                        for op, args in AGENT_TOOL_SCRIPT[agent_prefix]
                    ],
                )
            return AIMessage(content=_finding_text(agent_prefix, turn))

        return AIMessage(
            content=(
                "## Executive Summary\nThe web-service outage is driven by the "
                "production database pod running out of memory and restarting, which "
                "exhausts the web-service connection pool and produces 5xx errors.\n"
                "### Next Steps\n1. Raise database memory limit\n2. Increase pool size\n"
                "3. Escalate to dba-oncall per your escalation preference"
            )
        )


# ---------------------------------------------------------------------------
# Running one version
# ---------------------------------------------------------------------------
async def run_version(version: str, mode: str, region: str, tools) -> Dict[str, Any]:
    pkg = importlib.import_module(version)
    graph_builder = importlib.import_module(f"{version}.graph_builder")
    agent_nodes = importlib.import_module(f"{version}.agent_nodes")
    supervisor_mod = importlib.import_module(f"{version}.supervisor")
    formatter_mod = importlib.import_module(f"{version}.output_formatter")
    memory_client_mod = importlib.import_module(f"{version}.memory.client")
    logging.getLogger().setLevel(logging.WARNING)
    for name in list(logging.root.manager.loggerDict):
        logging.getLogger(name).setLevel(logging.WARNING)

    store = FakeAgentCoreMemory()
    fake_client_cls = make_fake_memory_client_cls(memory_client_mod.SREMemoryClient, store)
    agent_nodes.SREMemoryClient = fake_client_cls
    supervisor_mod.SREMemoryClient = fake_client_cls

    recorder = CallRecorder()
    real_factory = importlib.import_module(f"{version}.llm_utils").create_llm_with_error_handling

    def factory(provider="bedrock", **kwargs):
        if mode == "offline":
            return ScriptedChatModel(callbacks=[recorder])
        kwargs.setdefault("region_name", region)
        llm = real_factory(provider, **kwargs)
        llm.callbacks = list(llm.callbacks or []) + [recorder]
        return llm

    for module in (agent_nodes, supervisor_mod, formatter_mod):
        module.create_llm_with_error_handling = factory

    graph = graph_builder.build_multi_agent_graph(
        tools, llm_provider="bedrock", region_name=region
    )

    messages: List[BaseMessage] = []
    session_id = f"bench-{version}-{int(time.time())}"
    turn_summaries = []
    started = time.time()
    for index, turn in enumerate(TURNS, start=1):
        recorder.turn = index
        messages.append(HumanMessage(content=turn["query"]))
        state = {
            "messages": list(messages),
            "next": "supervisor",
            "agent_results": {},
            "current_query": turn["query"],
            "metadata": {},
            "requires_collaboration": False,
            "agents_invoked": [],
            "final_response": None,
            "auto_approve_plan": True,
            "user_id": USER_ID,
            "session_id": session_id,
        }
        result = await graph.ainvoke(state, config={"recursion_limit": 50})
        final_response = result.get("final_response") or ""
        messages.append(AIMessage(content=final_response))
        turn_summaries.append(
            {
                "turn": index,
                "agents_invoked": result.get("agents_invoked", []),
                "final_response_chars": len(final_response),
            }
        )
    elapsed = time.time() - started
    return {
        "version": version,
        "package_path": str(Path(pkg.__file__).parent),
        "mode": mode,
        "elapsed_seconds": round(elapsed, 1),
        "calls": recorder.calls,
        "turns": turn_summaries,
        "memory": store.stats,
    }


# ---------------------------------------------------------------------------
# Aggregation & report
# ---------------------------------------------------------------------------
def summarize(run: Dict[str, Any]) -> Dict[str, Any]:
    calls = run["calls"]
    seen_prefixes = set()
    est_cache_read = 0
    for c in calls:
        cacheable = c["cache_marked"] and c["prefix_tokens_est"] >= MIN_CACHE_TOKENS
        if cacheable and c["prefix_hash"] in seen_prefixes:
            c["est_cache_read"] = c["prefix_tokens_est"]
            est_cache_read += c["prefix_tokens_est"]
        else:
            c["est_cache_read"] = 0
        if cacheable:
            seen_prefixes.add(c["prefix_hash"])

    def total(key):
        return sum(c.get(key, 0) for c in calls)

    summary = {
        "llm_calls": len(calls),
        "input_tokens_est": total("input_tokens_est"),
        "max_input_tokens_est": max((c["input_tokens_est"] for c in calls), default=0),
        "tool_result_tokens_est": total("tool_result_tokens"),
        "cache_marked_calls": sum(1 for c in calls if c["cache_marked"]),
        "est_cache_read_tokens": est_cache_read,
        "memory_retrieve_calls": run["memory"]["retrieve_calls"],
        "memory_records_returned": run["memory"]["records_returned"],
        "memory_create_events": run["memory"]["create_event_calls"],
    }
    if any("api_input_tokens" in c for c in calls):
        summary.update(
            {
                "api_input_tokens": total("api_input_tokens"),
                "api_output_tokens": total("api_output_tokens"),
                "api_cache_read": total("api_cache_read"),
                "api_cache_write": total("api_cache_write"),
            }
        )
        # Bedrock reports input_tokens excluding cached tokens; total processed input:
        summary["api_total_input"] = (
            summary["api_input_tokens"] + summary["api_cache_read"] + summary["api_cache_write"]
        )
    by_role: Dict[str, Dict[str, int]] = {}
    for c in calls:
        key = f"T{c['turn']} {c['role']}"
        entry = by_role.setdefault(key, {"calls": 0, "input_tokens_est": 0, "max_input_est": 0})
        entry["calls"] += 1
        entry["input_tokens_est"] += c["input_tokens_est"]
        entry["max_input_est"] = max(entry["max_input_est"], c["input_tokens_est"])
        if "api_input_tokens" in c:
            entry["api_input_tokens"] = entry.get("api_input_tokens", 0) + c["api_input_tokens"] + c.get("api_cache_read", 0) + c.get("api_cache_write", 0)
    summary["by_turn_role"] = by_role
    return summary


def main() -> None:
    if sys.flags.utf8_mode == 0:
        # Both versions read prompt files with Path.read_text() (platform encoding);
        # on Korean Windows (cp949) the 22KB supervisor prompt silently falls back to
        # a one-line prompt. The agent normally runs in a Linux container (UTF-8).
        raise SystemExit("Run with UTF-8 mode: python -X utf8 benchmarks/context_benchmark.py ...")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["offline", "bedrock"], default="offline")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--versions", nargs="+", default=VERSIONS)
    args = parser.parse_args()

    tools = build_gateway_tools()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"context_benchmark_{args.mode}.json"
    # Merge into an existing result file so one version can be re-run on its own
    out = (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {"mode": args.mode, "runs": {}}
    )
    for version in args.versions:
        print(f"Running {version} ({args.mode}) ...", flush=True)
        run = asyncio.run(run_version(version, args.mode, args.region, tools))
        run["generated_at"] = datetime.now().isoformat(timespec="seconds")
        run["summary"] = summarize(run)
        out["runs"][version] = run
        s = run["summary"]
        print(
            f"  calls={s['llm_calls']} input_est={s['input_tokens_est']:,} "
            f"max_call={s['max_input_tokens_est']:,} memory_retrieves={s['memory_retrieve_calls']}"
            + (f" api_total_input={s['api_total_input']:,} cache_read={s['api_cache_read']:,}" if "api_total_input" in s else ""),
            flush=True,
        )
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()

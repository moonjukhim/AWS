#!/usr/bin/env python3
"""
Context engineering helpers: prompt caching, trimming and compact formatting.

These helpers keep LLM inputs small and cache-friendly:
- static system prompts get a cache checkpoint (static-first prompt layout)
- tool results are truncated before they re-enter the ReAct loop
- prior conversation turns are trimmed to a token budget
- memory records are filtered by relevance and rendered as compact text
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.utils import count_tokens_approximately, trim_messages

from .constants import SREConstants

logger = logging.getLogger(__name__)


def cached_system_message(text: str) -> SystemMessage:
    """Build a system message whose content is marked as a prompt-cache checkpoint.

    Everything up to and including this block (tool definitions + system prompt)
    becomes the cached prefix, so the text must not contain per-request data.
    """
    if not SREConstants.context.enable_prompt_caching:
        return SystemMessage(content=text)
    return SystemMessage(
        content=[{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]
    )


def truncate_tool_messages_hook(state: Dict[str, Any]) -> Dict[str, Any]:
    """pre_model_hook for create_react_agent: cap tool result size sent to the LLM.

    The full tool output stays in graph state; only the LLM input is trimmed.
    """
    max_chars = SREConstants.context.max_tool_result_chars
    trimmed: List[BaseMessage] = []
    for msg in state["messages"]:
        if isinstance(msg, ToolMessage) and isinstance(msg.content, str):
            if len(msg.content) > max_chars:
                msg = msg.model_copy(
                    update={
                        "content": msg.content[:max_chars]
                        + f"\n...[truncated {len(msg.content) - max_chars} chars]"
                    }
                )
        trimmed.append(msg)
    return {"llm_input_messages": trimmed}


def build_history_context(messages: List[BaseMessage], current_query: str) -> str:
    """Render earlier user/assistant turns within the configured token budget.

    Tool calls and tool results are dropped; only the conversational turns remain,
    newest first kept when the budget is exceeded.
    """
    turns: List[BaseMessage] = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            turns.append(msg)
        elif isinstance(msg, AIMessage) and not msg.tool_calls and msg.content:
            turns.append(msg)

    # The last human turn is the current query; it is passed separately
    if turns and isinstance(turns[-1], HumanMessage) and turns[-1].content == current_query:
        turns = turns[:-1]
    if not turns:
        return ""

    kept = trim_messages(
        turns,
        max_tokens=SREConstants.context.max_history_tokens,
        token_counter=count_tokens_approximately,
        strategy="last",
        start_on="human",
        allow_partial=False,
    )
    lines = []
    for msg in kept:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def filter_by_relevance(
    records: List[Dict[str, Any]], min_score: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Drop memory records below the relevance threshold (records without a score are kept)."""
    threshold = (
        SREConstants.memory.min_relevance_score if min_score is None else min_score
    )
    return [r for r in records if r.get("score", 1.0) >= threshold]


def memory_record_texts(records: List[Dict[str, Any]]) -> List[str]:
    """Extract only the text payload from memory records (no ids, namespaces or metadata)."""
    texts = []
    for record in records:
        content = record.get("content", {})
        if isinstance(content, dict) and content.get("text"):
            texts.append(content["text"])
        elif isinstance(content, str) and content:
            texts.append(content)
    return texts


def format_bullets(title: str, items: List[str]) -> str:
    """Render a titled bullet list, or an empty string when there is nothing to show."""
    if not items:
        return ""
    return f"\n{title}:\n" + "\n".join(f"- {item}" for item in items) + "\n"


def truncate_text(text: str, max_chars: int) -> str:
    """Shorten text to max_chars, marking the cut."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"

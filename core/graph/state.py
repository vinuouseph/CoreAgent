"""
CoreAgent-2 — Agent State Schema
TypedDict passed between every node in the graph and persisted by the checkpointer.
"""
from typing import Annotated, Any, Sequence, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def _append_lists(existing: list, new: list) -> list:
    """Reducer: append new items to existing list (used for trace)."""
    return existing + new


class AgentState(TypedDict):
    """Central state schema for the CoreAgent-2 LangGraph."""

    # Conversation history — `add_messages` reducer appends new messages
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Routing
    route: str                          # respond | search | tool_call

    # RAG state
    query: str                          # current / reformulated query
    documents: list[Document]           # retrieved context chunks
    docs_relevant: bool                 # grader verdict
    retry_count: int                    # Self-RAG loop counter

    # Tool execution state
    requires_approval: bool             # HITL flag
    pending_tool_calls: list[dict]      # tools awaiting execution

    # Observability — append-only trace list
    trace: Annotated[list[dict], _append_lists]

    # Session metadata (tokens, latency, costs …)
    metadata: dict[str, Any]

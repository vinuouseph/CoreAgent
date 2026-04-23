"""
CoreAgent-2 — Conditional Edge Functions
Routing logic used between nodes in the state graph.
"""
from core.graph.state import AgentState
from core.config import config


def route_query(state: AgentState) -> str:
    """Route from the Router node to the appropriate handler."""
    route = state.get("route", "respond")
    if route == "search":
        return "retriever"
    elif route == "tool_call":
        return "tool_executor"
    return "responder"


def grade_documents(state: AgentState) -> str:
    """Route from the Grader: generate if relevant, rewrite if not (with retry limit)."""
    is_relevant = state.get("docs_relevant", True)
    retry_count = state.get("retry_count", 0)

    if is_relevant:
        return "generator"
    elif retry_count < config.MAX_SELF_RAG_RETRIES:
        return "rewriter"
    else:
        # Exhausted retries — generate with whatever we have
        return "generator"

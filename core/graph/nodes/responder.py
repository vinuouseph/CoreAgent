"""
CoreAgent-2 — Responder Node
Handles simple conversational queries that don't need RAG or tools.
"""
import time
from langchain_core.messages import AIMessage, SystemMessage

from core.llm.provider import get_llm
from core.graph.state import AgentState


def responder_node(state: AgentState) -> dict:
    """Generate a direct conversational response."""
    start = time.time()
    messages = state.get("messages", [])

    llm = get_llm()

    formatted = [SystemMessage(content="You are a helpful, concise AI assistant called CoreAgent.")] + list(messages)

    try:
        response = llm.invoke(formatted)
    except Exception as e:
        response = AIMessage(content=f"I encountered an error: {e}")

    duration = int((time.time() - start) * 1000)
    return {
        "messages": [response],
        "trace": [{"node": "Responder", "action": "Direct conversational reply", "details": "", "duration_ms": duration}],
    }

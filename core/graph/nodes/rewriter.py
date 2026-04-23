"""
CoreAgent-2 — Query Rewriter Node
Reformulates the query after a failed retrieval attempt to improve Self-RAG quality.
"""
import time
from langchain_core.messages import HumanMessage

from core.llm.provider import get_llm
from core.graph.state import AgentState


def rewriter_node(state: AgentState) -> dict:
    """Rewrite the query for better semantic vector search."""
    start = time.time()
    query = state.get("query", "")
    retry_count = state.get("retry_count", 0)

    llm = get_llm(temperature=0)

    prompt = f"""You are a query rewriting assistant. The original query failed to retrieve relevant information.
Rewrite it to be more effective for semantic vector search.
Focus on key entities, remove filler, and add relevant synonyms.

Original Query: {query}

Provide ONLY the rewritten query text."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        rewritten = response.content.strip()
    except Exception:
        rewritten = query

    duration = int((time.time() - start) * 1000)
    return {
        "query": rewritten,
        "retry_count": retry_count + 1,
        "trace": [{"node": "Rewriter", "action": f"Reformulated (attempt {retry_count + 1})", "details": f"→ '{rewritten[:80]}'", "duration_ms": duration}],
    }

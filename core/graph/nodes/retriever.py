"""
CoreAgent-2 — Retriever Node
Fetches relevant documents from the ChromaDB Knowledge Vault.
"""
import time
from core.knowledge.vault import vault
from core.graph.state import AgentState


def retriever_node(state: AgentState) -> dict:
    """Query the Knowledge Vault for documents matching the current query."""
    start = time.time()
    query = state.get("query", "")

    if not query:
        messages = state.get("messages", [])
        if messages:
            query = messages[-1].content

    try:
        documents = vault.search(query=query)
        detail = f"Found {len(documents)} document(s)."
    except Exception as e:
        documents = []
        detail = f"Error: {e}"

    duration = int((time.time() - start) * 1000)
    return {
        "documents": documents,
        "trace": [{"node": "Retriever", "action": f"Searched for: '{query[:60]}'", "details": detail, "duration_ms": duration}],
    }

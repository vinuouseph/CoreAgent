"""
CoreAgent-2 — Generator Node
Produces the final RAG-grounded answer using retrieved context.
"""
import time
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from core.llm.provider import get_llm
from core.graph.state import AgentState


def generator_node(state: AgentState) -> dict:
    """Generate a final answer using the retrieved documents as grounded context."""
    start = time.time()
    query = state.get("query", "")
    documents = state.get("documents", [])

    if not documents:
        return {
            "messages": [AIMessage(content="I couldn't find any relevant information to answer your question.")],
            "trace": [{"node": "Generator", "action": "No context available", "details": "", "duration_ms": 0}],
        }

    llm = get_llm()

    docs_content = "\n\n".join(
        f"--- Source {i+1} ---\n{doc.page_content}" for i, doc in enumerate(documents)
    )

    system = """You are an intelligent assistant. Use the provided context to answer the user's question.
If you don't know the answer from the context, say so honestly.
Cite your sources when applicable."""

    user = f"""Question: {query}

Context:
{docs_content}"""

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    except Exception as e:
        response = AIMessage(content=f"Error generating answer: {e}")

    duration = int((time.time() - start) * 1000)
    return {
        "messages": [response],
        "trace": [{"node": "Generator", "action": f"Generated answer from {len(documents)} chunk(s)", "details": "", "duration_ms": duration}],
    }

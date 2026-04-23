"""
CoreAgent-2 — Self-RAG Grader Node
Evaluates whether retrieved documents are semantically relevant to the query.
"""
import time
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from core.llm.provider import get_llm
from core.graph.state import AgentState


class GradeDecision(BaseModel):
    """Binary relevance grade."""
    binary_score: str = Field(description="'yes' if documents are relevant, else 'no'.")


def grader_node(state: AgentState) -> dict:
    """Grade retrieved documents for relevance; triggers rewrite if irrelevant."""
    start = time.time()
    query = state.get("query", "")
    documents = state.get("documents", [])

    if not documents:
        return {
            "docs_relevant": False,
            "trace": [{"node": "Grader", "action": "No documents to grade.", "details": "", "duration_ms": 0}],
        }

    llm = get_llm(temperature=0).with_structured_output(GradeDecision)

    docs_content = "\n\n".join(doc.page_content for doc in documents)

    prompt = f"""You are a grader assessing the relevance of retrieved documents to a user question.

Retrieved documents:
{docs_content}

User question: {query}

If the documents contain keywords or semantic meaning related to the question, grade as relevant.
Respond with 'yes' or 'no'."""

    try:
        decision = llm.invoke([HumanMessage(content=prompt)])
        is_relevant = decision.binary_score.strip().lower() == "yes"
    except Exception:
        is_relevant = True  # Default to True to avoid infinite loops

    duration = int((time.time() - start) * 1000)
    return {
        "docs_relevant": is_relevant,
        "trace": [{"node": "Grader", "action": f"Verdict: {'✅ Relevant' if is_relevant else '❌ Irrelevant'}", "details": "", "duration_ms": duration}],
    }

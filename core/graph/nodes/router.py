"""
CoreAgent-2 — Router Node
Classifies user intent into respond | search | tool_call using structured LLM output.
"""
import time
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from core.llm.provider import get_llm
from core.graph.state import AgentState


class RouteDecision(BaseModel):
    """Structured routing output."""
    route: str = Field(
        description="Action to take: 'respond' (general chat), 'search' (knowledge base), or 'tool_call' (explicit action)."
    )
    extracted_query: str = Field(
        description="The core intent extracted from the user's message, optimised for search."
    )


def router_node(state: AgentState) -> dict:
    """Analyse the latest message and decide the next step."""
    start = time.time()
    messages = state.get("messages", [])

    if not messages:
        return {
            "route": "respond",
            "query": "",
            "trace": [{"node": "Router", "action": "No messages — defaulting to respond", "details": "", "duration_ms": 0}],
        }

    last_message = messages[-1]

    llm = get_llm(temperature=0).with_structured_output(RouteDecision)

    prompt = f"""You are an intelligent router for an AI agent. Analyse the user's latest input and choose the best action.

Options:
- 'search': The user asks for information that likely exists in a document or knowledge base.
- 'tool_call': The user explicitly requests an action (e.g., 'search the web', 'calculate this').
- 'respond': The user is chatting, greeting, or asking a generic question that doesn't need retrieval or tools.

User Input: {last_message.content}
"""

    try:
        decision = llm.invoke([HumanMessage(content=prompt)])
        route = decision.route
        query = decision.extracted_query
    except Exception as e:
        route, query = "respond", last_message.content

    duration = int((time.time() - start) * 1000)
    trace_item = {
        "node": "Router",
        "action": f"Routed → {route}",
        "details": f"Extracted query: {query}",
        "duration_ms": duration,
    }

    return {
        "route": route,
        "query": query,
        "retry_count": 0,
        "docs_relevant": True,
        "trace": [trace_item],
    }

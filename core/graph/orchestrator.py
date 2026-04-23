"""
CoreAgent-2 — LangGraph Orchestrator
Builds, compiles, and exposes the central StateGraph with:
  • Conditional routing (respond / search / tool_call)
  • Self-RAG loop (retriever → grader → rewriter ↺)
  • Human-in-the-Loop breakpoint before tool execution
  • SQLite checkpointer for persistent state
"""
from langgraph.graph import StateGraph, START, END

from core.graph.state import AgentState
from core.graph.nodes import (
    router_node,
    retriever_node,
    grader_node,
    rewriter_node,
    generator_node,
    responder_node,
    tool_executor_node,
)
from core.graph.edges.conditionals import route_query, grade_documents
from core.memory.checkpointer import get_checkpointer


def build_graph():
    """
    Construct and compile the CoreAgent-2 StateGraph.

    Graph topology:

        START ──► Router
                    ├──respond──► Responder ──► END
                    ├──search───► Retriever ──► Grader
                    │                           ├──relevant──► Generator ──► END
                    │                           └──irrelevant─► Rewriter ──► Retriever  (loop)
                    └──tool_call─► ToolExecutor (HITL interrupt) ──► Responder ──► END
    """

    builder = StateGraph(AgentState)

    # ── Nodes ────────────────────────────────────────────────────────────
    builder.add_node("router",        router_node)
    builder.add_node("retriever",     retriever_node)
    builder.add_node("grader",        grader_node)
    builder.add_node("rewriter",      rewriter_node)
    builder.add_node("generator",     generator_node)
    builder.add_node("responder",     responder_node)
    builder.add_node("tool_executor", tool_executor_node)

    # ── Edges ────────────────────────────────────────────────────────────
    builder.add_edge(START, "router")

    # Router → conditional fan-out
    builder.add_conditional_edges(
        "router",
        route_query,
        {"retriever": "retriever", "tool_executor": "tool_executor", "responder": "responder"},
    )

    # Self-RAG loop
    builder.add_edge("retriever", "grader")
    builder.add_conditional_edges(
        "grader",
        grade_documents,
        {"generator": "generator", "rewriter": "rewriter"},
    )
    builder.add_edge("rewriter", "retriever")

    # Terminal edges
    builder.add_edge("generator",     END)
    builder.add_edge("responder",     END)
    builder.add_edge("tool_executor", "responder")  # Feed tool results back through responder

    # ── Compile ──────────────────────────────────────────────────────────
    checkpointer = get_checkpointer()

    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["tool_executor"],  # HITL breakpoint
    )

    return graph


# ── Global graph singleton ───────────────────────────────────────────────
core_agent_graph = build_graph()

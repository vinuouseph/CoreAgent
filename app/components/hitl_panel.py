"""
CoreAgent-2 — HITL Panel Component
Human-in-the-Loop approval interface for high-stakes tool executions.
"""
import streamlit as st
from langgraph.types import Command

from core.graph.orchestrator import core_agent_graph


def render_hitl_panel():
    """
    Display pending HITL interrupts and allow approval/denial.
    Checks across all active thread IDs stored in session state.
    """
    st.header("Human-in-the-Loop")
    st.markdown("Review and approve or deny pending tool executions before they run.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Track thread IDs
    thread_ids = st.session_state.get("known_threads", ["user_session_001"])

    pending_count = 0

    for tid in thread_ids:
        config = {"configurable": {"thread_id": tid}}
        try:
            state = core_agent_graph.get_state(config)
        except Exception:
            continue

        if not state.values:
            continue

        requires_approval = state.values.get("requires_approval", False)
        pending_calls = state.values.get("pending_tool_calls", [])

        if not requires_approval and not pending_calls:
            continue

        pending_count += 1

        with st.expander(f"Thread `{tid}` — Pending Approval", expanded=True):
            if pending_calls:
                for call in pending_calls:
                    st.markdown(f"**Tool:** `{call.get('name', 'Unknown')}`")
                    st.json(call.get("args", {}))
            else:
                st.info("Graph interrupted before tool_executor (no explicit pending calls yet).")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Approve", key=f"approve_{tid}"):
                    with st.spinner("Resuming graph execution…"):
                        try:
                            core_agent_graph.invoke(Command(resume=True), config=config)
                            st.success("Execution resumed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Resume failed: {e}")
            with col2:
                if st.button(f"Deny", key=f"deny_{tid}"):
                    st.warning("Tool execution denied. (Feature: In production, this would cancel the node.)")

    if pending_count == 0:
        st.info("No pending approvals. All systems nominal.")

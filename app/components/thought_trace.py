"""
CoreAgent-2 — Thought Trace Component
Displays the agent's internal reasoning as a visual timeline.
"""
import streamlit as st


def render_thought_trace(trace_history: list[dict]):
    """
    Render the agent's reasoning trace as a collapsible timeline.
    Each entry has: node, action, details, duration_ms.
    """
    if not trace_history:
        return

    with st.expander("Agent Thought Trace", expanded=False):
        for i, step in enumerate(trace_history):
            node = step.get("node", "Unknown")
            action = step.get("action", "")
            details = step.get("details", "")
            duration = step.get("duration_ms", 0)

            # Timeline connector
            if i > 0:
                st.markdown(
                    "<div style='border-left:2px solid rgba(56,189,248,0.25); height:12px; margin-left:8px;'></div>",
                    unsafe_allow_html=True,
                )

            cols = st.columns([0.85, 0.15])
            with cols[0]:
                st.markdown(f"**`{node}`** &nbsp;→&nbsp; {action}")
                if details:
                    st.caption(f"&nbsp;&nbsp;└─ {details}")
            with cols[1]:
                if duration:
                    st.caption(f"`{duration}ms`")

"""
CoreAgent-2 — Analytics Panel Component
Performance monitoring with Plotly charts and session cost estimation.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from core.observability.logger import metrics


def render_analytics_panel():
    """Render performance monitoring dashboard."""
    st.header("Analytics & Governance")
    st.markdown("<br>", unsafe_allow_html=True)

    events = metrics.get_events()

    # ── KPI Cards ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    total_sessions = len(set(e.get("thread_id", "") for e in events)) if events else 0
    total_nodes = len(events)
    avg_latency = int(np.mean([e.get("duration_ms", 0) for e in events])) if events else 0
    error_count = sum(1 for e in events if e.get("status") == "ERROR")

    col1.metric("Active Sessions", f"{total_sessions}", help="Unique thread IDs seen")
    col2.metric("Node Executions", f"{total_nodes}", help="Total graph node invocations")
    col3.metric("Avg Latency", f"{avg_latency}ms", help="Average node execution time")
    col4.metric("Errors", f"{error_count}", delta=f"-{error_count}" if error_count == 0 else f"+{error_count}", delta_color="inverse")

    if not events:
        st.info("No execution data yet. Start chatting to generate metrics!")
        _render_demo_charts()
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Latency by Node ──────────────────────────────────────────────────
    df = pd.DataFrame(events)

    st.subheader("Node Latency Distribution")
    if "node" in df.columns and "duration_ms" in df.columns:
        fig = px.box(
            df, x="node", y="duration_ms",
            color="node",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"duration_ms": "Latency (ms)", "node": "Node"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8b949e",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Execution Timeline ───────────────────────────────────────────────
    st.subheader("Execution Timeline")
    if "timestamp" in df.columns:
        fig2 = px.scatter(
            df, x="timestamp", y="duration_ms",
            color="status",
            symbol="node",
            color_discrete_map={"SUCCESS": "#34d399", "ERROR": "#fb7185"},
            labels={"duration_ms": "Duration (ms)", "timestamp": "Time"},
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8b949e",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Clear button ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Metrics", key="clear_metrics"):
        metrics.clear()
        st.rerun()


def _render_demo_charts():
    """Show demo charts when no real data exists."""
    st.subheader("Sample: Token Usage Over Time")
    dates = pd.date_range(start="2026-04-01", periods=20)
    data = pd.DataFrame({
        "Date": dates,
        "Tokens": np.random.randint(1000, 5000, 20),
        "Cost ($)": np.round(np.random.uniform(0.01, 0.15, 20), 3),
    })

    fig = px.area(
        data, x="Date", y="Tokens",
        color_discrete_sequence=["#38bdf8"],
        labels={"Tokens": "Token Count"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e",
    )
    st.plotly_chart(fig, use_container_width=True)

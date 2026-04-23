"""
CoreAgent-2 — Log Viewer Component
Inspects node execution logs with filtering and payload expansion.
"""
import streamlit as st
import pandas as pd

from core.observability.logger import metrics


def render_log_viewer():
    """Render a filterable, color-coded log viewer."""
    st.header("Observability Logs")
    st.markdown("<br>", unsafe_allow_html=True)

    events = metrics.get_events(limit=200)

    if not events:
        st.info("No log entries yet. Execute some queries to populate the log.")
        st.markdown("""
        | Timestamp | Thread ID | Node | Status | Duration |
        | :--- | :--- | :--- | :--- | :--- |
        | — | — | — | — | — |
        """)
        return

    # ── Filters ──────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    all_nodes = sorted(set(e.get("node", "") for e in events))
    all_statuses = sorted(set(e.get("status", "") for e in events))
    all_threads = sorted(set(e.get("thread_id", "") for e in events))

    with col1:
        filter_node = st.multiselect("Filter by Node", options=all_nodes, default=all_nodes, key="log_node_filter")
    with col2:
        filter_status = st.multiselect("Filter by Status", options=all_statuses, default=all_statuses, key="log_status_filter")
    with col3:
        filter_thread = st.multiselect("Filter by Thread", options=all_threads, default=all_threads, key="log_thread_filter")

    # ── Table ────────────────────────────────────────────────────────────
    filtered = [
        e for e in events
        if e.get("node") in filter_node
        and e.get("status") in filter_status
        and e.get("thread_id") in filter_thread
    ]

    if filtered:
        df = pd.DataFrame(filtered)
        display_cols = [c for c in ["timestamp", "thread_id", "node", "status", "duration_ms", "error"] if c in df.columns]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": st.column_config.TextColumn("Time", width="small"),
                "thread_id": st.column_config.TextColumn("Thread", width="medium"),
                "node": st.column_config.TextColumn("Node", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "duration_ms": st.column_config.NumberColumn("Duration (ms)", width="small"),
                "error": st.column_config.TextColumn("Error", width="large"),
            },
        )

        # Expandable raw events
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Raw Event Payloads"):
            for i, event in enumerate(reversed(filtered[-10:])):
                st.json(event)
    else:
        st.warning("No events match the current filters.")

"""
CoreAgent-2 — Developer Dashboard
Admin control centre with tabbed layout for Knowledge Vault, HITL, Model Router, Analytics, and Logs.
"""
import streamlit as st

from app.components.knowledge_vault_ui import render_knowledge_vault_ui
from app.components.hitl_panel import render_hitl_panel
from app.components.model_router_ui import render_model_router_ui
from app.components.analytics_panel import render_analytics_panel
from app.components.log_viewer import render_log_viewer


def render_dev_dashboard():
    """Render the developer / admin dashboard."""
    st.title("Developer Dashboard")
    st.caption("Granular system control — manage knowledge, monitor performance, and configure models.")
    st.markdown("<br>", unsafe_allow_html=True)

    tabs = st.tabs([
        "Knowledge Vault",
        "Human-in-the-Loop",
        "Model Router",
        "Analytics",
        "Observability Logs",
    ])

    with tabs[0]:
        render_knowledge_vault_ui()

    with tabs[1]:
        render_hitl_panel()

    with tabs[2]:
        render_model_router_ui()

    with tabs[3]:
        render_analytics_panel()

    with tabs[4]:
        render_log_viewer()

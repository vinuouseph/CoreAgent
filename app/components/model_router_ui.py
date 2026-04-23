"""
CoreAgent-2 — Model Router UI Component
Dynamic model switching with live session state updates.
"""
import streamlit as st

from core.config import config


def render_model_router_ui():
    """Render dynamic model switching controls."""
    st.header("Model Router")
    st.markdown("Switch the LLM provider and model dynamically for the current session.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Provider Selection ───────────────────────────────────────────────
    if "active_provider" not in st.session_state:
        st.session_state.active_provider = config.DEFAULT_LLM_PROVIDER
    if "active_model" not in st.session_state:
        st.session_state.active_model = (
            config.TCS_GENAI_DEFAULT_CHAT_MODEL
            if config.DEFAULT_LLM_PROVIDER == "TCS_GENAI_LAB"
            else config.OLLAMA_DEFAULT_CHAT_MODEL
        )
    if "active_temperature" not in st.session_state:
        st.session_state.active_temperature = 0.2

    provider = st.radio(
        "Active Provider",
        options=["TCS_GENAI_LAB", "OLLAMA"],
        index=0 if st.session_state.active_provider == "TCS_GENAI_LAB" else 1,
        horizontal=True,
        key="model_provider_radio",
    )

    # ── Model Selection ──────────────────────────────────────────────────
    if provider == "TCS_GENAI_LAB":
        models = config.TCS_AVAILABLE_MODELS
        default_idx = models.index(st.session_state.active_model) if st.session_state.active_model in models else 0
    else:
        models = config.OLLAMA_AVAILABLE_MODELS
        default_idx = models.index(st.session_state.active_model) if st.session_state.active_model in models else 0

    selected_model = st.selectbox("Model", options=models, index=default_idx, key="model_select")

    # ── Parameters ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature", 0.0, 1.0,
            st.session_state.active_temperature, 0.05,
            key="temp_slider",
        )
    with col2:
        st.markdown("")  # spacing
        st.markdown(f"""
        **Current Config:**
        - Provider: `{provider}`
        - Model: `{selected_model}`
        - Temp: `{temperature}`
        """)

    # ── Apply ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Apply Changes", type="primary", key="apply_model"):
        st.session_state.active_provider = provider
        st.session_state.active_model = selected_model
        st.session_state.active_temperature = temperature
        st.success(f"Switched to **{provider}** / `{selected_model}` (temp={temperature})")
        st.info("New settings apply to the next message. Active conversations continue with the previous model.")

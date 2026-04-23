"""
CoreAgent-2 — Streamlit Entry Point
Configures the page, injects the theme, and routes between Chat and Dev Dashboard.
"""
import os
import streamlit as st


# ── Page Config (MUST be first Streamlit call) ───────────────────────────
st.set_page_config(
    page_title="CoreAgent-2",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Theme Injection ─────────────────────────────────────────────────────
def _load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles", "theme.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    _load_css()

    # ── Sidebar Branding ─────────────────────────────────────────────────
    st.sidebar.markdown(
        """
        <div style="text-align:center; padding: 0.5rem 0 1.5rem 0;">
            <div style="display: inline-block; width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #38bdf8, #a78bfa); margin-bottom: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(56, 189, 248, 0.25);">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
            </div>
            <h2 style="margin:0; padding:0; font-size:1.8rem;
                background: linear-gradient(135deg, #38bdf8, #a78bfa);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                letter-spacing: -0.02em; font-weight: 700;">
                CoreAgent
            </h2>
            <p style="margin:4px 0 0 0; font-size:0.8rem; color:#a1aab4; font-weight: 500;">v2.0 — Production Framework</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── Navigation ───────────────────────────────────────────────────────
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"

    if st.sidebar.button("Chat Experience", use_container_width=True):
        st.session_state.current_page = "chat"

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    dev_mode = st.sidebar.toggle("Developer Mode", value=False, key="dev_mode_toggle")

    if dev_mode:
        if st.sidebar.button("Admin Dashboard", use_container_width=True):
            st.session_state.current_page = "dev_dashboard"

    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by **LangGraph** • **ChromaDB** • **Streamlit**")

    # ── Page Routing ─────────────────────────────────────────────────────
    if st.session_state.current_page == "chat":
        from app.pages.chat import render_chat_page
        render_chat_page()
    elif st.session_state.current_page == "dev_dashboard" and dev_mode:
        from app.pages.dev_dashboard import render_dev_dashboard
        render_dev_dashboard()
    else:
        from app.pages.chat import render_chat_page
        st.session_state.current_page = "chat"
        render_chat_page()


if __name__ == "__main__":
    main()

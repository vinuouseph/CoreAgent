"""
CoreAgent-2 — Chat Page
Customer-facing chat experience with file upload, thought trace, and HITL.
"""
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from core.graph.orchestrator import core_agent_graph
from app.components.chat_interface import display_message_history
from app.components.thought_trace import render_thought_trace


def render_chat_page():
    """Render the main customer-facing chat interface."""
    st.title("CoreAgent Chat")
    st.caption("Your AI-powered assistant — ask anything, upload documents, and explore.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Thread management ────────────────────────────────────────────────
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

    # Track known threads for HITL panel
    if "known_threads" not in st.session_state:
        st.session_state.known_threads = []
    if st.session_state.thread_id not in st.session_state.known_threads:
        st.session_state.known_threads.append(st.session_state.thread_id)

    # New conversation button
    st.sidebar.markdown("---")
    if st.sidebar.button("New Conversation", use_container_width=True):
        st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.known_threads.append(st.session_state.thread_id)
        st.rerun()

    st.sidebar.caption(f"Thread: `{st.session_state.thread_id}`")

    # ── Get current graph state ──────────────────────────────────────────
    graph_config = {"configurable": {"thread_id": st.session_state.thread_id}}

    try:
        current_state = core_agent_graph.get_state(graph_config)
    except Exception:
        current_state = None

    if current_state and current_state.values:
        messages = list(current_state.values.get("messages", []))
        trace = current_state.values.get("trace", [])
        requires_approval = current_state.values.get("requires_approval", False)
    else:
        messages = []
        trace = []
        requires_approval = False

    # ── Render message history ───────────────────────────────────────────
    display_message_history(messages)

    # ── Thought Trace ────────────────────────────────────────────────────
    if trace:
        render_thought_trace(trace)

    # ── HITL check ───────────────────────────────────────────────────────
    if requires_approval:
        st.warning("Agent execution paused — a tool requires your approval.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve & Resume", type="primary"):
                with st.spinner("Resuming agent…"):
                    try:
                        core_agent_graph.invoke(Command(resume=True), config=graph_config)
                    except Exception as e:
                        st.error(f"Resume error: {e}")
                st.rerun()
        with col2:
            if st.button("Deny"):
                st.info("Tool execution denied.")
        st.stop()

    # ── Chat Input ───────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask me anything…", accept_file="multiple"):
        
        # 1. Process files if any were attached
        if getattr(prompt, "files", None):
            from core.knowledge.loaders import process_upload
            from core.knowledge.vault import vault
            
            with st.status("Ingesting uploaded files…", expanded=True) as file_status:
                total_chunks = 0
                for file in prompt.files:
                    try:
                        st.write(f"Reading `{file.name}` …")
                        docs = process_upload(file.getvalue(), file.name)
                        vault.add_documents("default_knowledge", docs)
                        total_chunks += len(docs)
                    except Exception as e:
                        st.error(f"Failed: {file.name} — {e}")
                file_status.update(label=f"Ingested {total_chunks} chunks into knowledge vault!", state="complete", expanded=False)

        # 2. Extract text or provide a default if only files were uploaded
        text_content = getattr(prompt, "text", "")
        if not text_content and getattr(prompt, "files", None):
            text_content = "I have uploaded some files. Please use them as context."
        elif not text_content:
            text_content = ""

        # Display user message immediately
        if text_content:
            with st.chat_message("user"):
                st.markdown(text_content)

            # Run agent
            with st.status("Agent is thinking…", expanded=True) as status:
                try:
                    st.write("Routing your query…")
                    result = core_agent_graph.invoke(
                        {"messages": [HumanMessage(content=text_content)]},
                        config=graph_config,
                    )
                    status.update(label="Done!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Agent error: {e}")
                    status.update(label="Error", state="error", expanded=False)

        st.rerun()

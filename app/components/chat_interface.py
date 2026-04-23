"""
CoreAgent-2 — Chat Interface Components
Renders LangChain message objects in Streamlit's chat UI.
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def render_message(msg):
    """Render a single LangChain message."""
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        if msg.content:
            with st.chat_message("assistant"):
                st.markdown(msg.content)

    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            with st.expander(f"Tool Result: {getattr(msg, 'name', 'Action')}", expanded=False):
                st.code(msg.content, language="text")


def display_message_history(messages):
    """Iterate through and display the full chat history."""
    for msg in messages:
        render_message(msg)

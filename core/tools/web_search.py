"""
CoreAgent-2 — Web Search Tool (Placeholder)
Demonstrates a tool that would require HITL approval.
"""
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the internet for real-time information.
    Use this when the user asks for current events or facts requiring the internet.
    """
    return f"[MOCK WEB SEARCH]: Results for '{query}'. In production, connect to Tavily or DuckDuckGo API."

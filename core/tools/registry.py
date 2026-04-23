"""
CoreAgent-2 — Tool Registry
Central registry for LangChain BaseTool instances with optional HITL flags.
"""
from langchain_core.tools import BaseTool


class ToolRegistry:
    """Manages available tools for the agent."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool, requires_approval: bool = False):
        tool.metadata = tool.metadata or {}
        tool.metadata["requires_approval"] = requires_approval
        self._tools[tool.name] = tool

    def get_tool_by_name(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_tool_names(self) -> list[str]:
        return list(self._tools.keys())


# Global registry singleton
registry = ToolRegistry()

"""
CoreAgent-2 — Tool Executor Node
Executes pending tool calls. Designed to be interrupted by HITL before execution.
"""
import time
from langchain_core.messages import ToolMessage

from core.graph.state import AgentState
from core.tools.registry import registry


def tool_executor_node(state: AgentState) -> dict:
    """Execute pending tools. This node is subject to interrupt_before for HITL."""
    start = time.time()

    pending_calls = state.get("pending_tool_calls", [])

    if not pending_calls:
        return {
            "trace": [{"node": "ToolExecutor", "action": "No pending tool calls", "details": "", "duration_ms": 0}],
        }

    results = []
    executed = []

    for call in pending_calls:
        tool_name = call.get("name")
        tool_args = call.get("args", {})

        tool = registry.get_tool_by_name(tool_name)
        if tool:
            try:
                result = tool.invoke(tool_args)
                results.append(
                    ToolMessage(content=str(result), tool_call_id=call.get("id", "default_id"))
                )
                executed.append(f"✅ {tool_name}")
            except Exception as e:
                results.append(
                    ToolMessage(content=f"Error: {e}", tool_call_id=call.get("id", "default_id"))
                )
                executed.append(f"❌ {tool_name}")
        else:
            executed.append(f"⚠️ {tool_name} (not found)")

    duration = int((time.time() - start) * 1000)
    return {
        "messages": results,
        "pending_tool_calls": [],
        "requires_approval": False,
        "trace": [{"node": "ToolExecutor", "action": f"Executed: {', '.join(executed)}", "details": "", "duration_ms": duration}],
    }

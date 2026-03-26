from __future__ import annotations

from typing import Optional

from app.planner.planner import Plan
from app.tools.router import ToolRouter, ToolCall
from app.tools.registry import ToolRegistry
from app.tools.builtins import register_builtin_tools


class ToolExecutor:
    def __init__(self, tool_router: Optional[ToolRouter] = None):
        if tool_router is None:
            registry = ToolRegistry()
            register_builtin_tools(registry)
            tool_router = ToolRouter(registry)
        self.tool_router = tool_router

    def execute_tool(self, tool_call: ToolCall) -> str:
        result = self.tool_router.execute_tool_call(tool_call)
        return str(result)

    def execute_plan(self, plan: Plan) -> Plan:
        # Planner already has execution logic; keep method for compatibility
        return plan

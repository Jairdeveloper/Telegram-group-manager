from __future__ import annotations

from typing import Optional

from app.policies.engine import PolicyEngine
from app.planner.planner import Planner, Plan
from app.tools.registry import ToolRegistry
from app.tools.router import ToolRouter
from app.tools.builtins import register_builtin_tools


class AgentPlanner:
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        policy_engine: Optional[PolicyEngine] = None,
    ):
        self.tool_registry = tool_registry or ToolRegistry()
        if not self.tool_registry.list_tools():
            register_builtin_tools(self.tool_registry)
        self.policy_engine = policy_engine or PolicyEngine()
        self.tool_router = ToolRouter(self.tool_registry, self.policy_engine)
        self.planner = Planner(self.tool_router)

    def create_plan(self, goal: str, context: dict) -> Plan:
        return self.planner.create_plan(goal, context)

    def execute_plan(self, plan_id: str) -> Plan:
        return self.planner.execute_plan_sync(plan_id)

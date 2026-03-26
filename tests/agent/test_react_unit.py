from dataclasses import dataclass

from app.agent.core import AgentCore, AgentContext
from app.agent.reasoning import ReasoningDecision, ReasoningAction
from app.agent.memory import MemorySystem


class FakeReasoner:
    def decide(self, message: str):
        return ReasoningDecision(action=ReasoningAction.PLAN, thought="needs_tools")

    def think(self, message: str, context: str = ""):
        return "thought"


@dataclass
class FakePlan:
    plan_id: str
    final_result: str


class FakePlanner:
    def __init__(self):
        self.plan = FakePlan(plan_id="plan-test", final_result="calculator: 4")

    def create_plan(self, goal: str, context: dict):
        return self.plan

    def execute_plan(self, plan_id: str):
        return self.plan


class FakeRepo:
    def save_message(self, *args, **kwargs):
        pass

    def get_history(self, *args, **kwargs):
        return []


def test_react_plan_flow_returns_tool_result(monkeypatch):
    monkeypatch.setenv("AGENT_REACT_ENABLED", "true")
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("RAG_ENABLED", "false")

    memory = MemorySystem(repository=FakeRepo())
    agent = AgentCore(
        memory=memory,
        reasoner=FakeReasoner(),
        planner=FakePlanner(),
        llm_enabled=False,
    )
    response = agent.process("calcula 2+2", AgentContext(chat_id=123))
    assert response.source == "react"
    assert "calculator: 4" in response.response

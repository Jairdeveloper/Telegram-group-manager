import pytest
from app.planner.planner import Planner, Plan, PlanStep, StepStatus
from app.tools.registry import ToolRegistry
from app.tools.router import ToolRouter
from app.tools.builtins import register_builtin_tools


def test_plan_step_creation():
    step = PlanStep(
        step_id="step_1",
        tool="calculator",
        parameters={"expression": "2+2"}
    )
    assert step.step_id == "step_1"
    assert step.tool == "calculator"
    assert step.status == StepStatus.PENDING


def test_plan_step_with_dependencies():
    step = PlanStep(
        step_id="step_2",
        tool="search",
        parameters={"query": "test"},
        depends_on=["step_1"]
    )
    assert "step_1" in step.depends_on


def test_plan_creation():
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={"expression": "2+2"})
    ]
    plan = Plan(plan_id="plan_1", goal="Calculate 2+2", steps=steps)
    
    assert plan.plan_id == "plan_1"
    assert plan.goal == "Calculate 2+2"
    assert len(plan.steps) == 1
    assert plan.status == StepStatus.PENDING


def test_plan_get_completed_steps():
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={}, status=StepStatus.COMPLETED),
        PlanStep(step_id="step_2", tool="search", parameters={}, status=StepStatus.FAILED),
    ]
    plan = Plan(plan_id="plan_1", goal="test", steps=steps)
    
    completed = plan.get_completed_steps()
    assert len(completed) == 1


def test_plan_get_step():
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={}),
    ]
    plan = Plan(plan_id="plan_1", goal="test", steps=steps)
    
    step = plan.get_step("step_1")
    assert step is not None
    assert step.tool == "calculator"


def test_planner_create_plan():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    plan = planner.create_plan("calculate 2 + 2", {"tenant_id": "default"})
    
    assert plan is not None
    assert plan.goal == "calculate 2 + 2"
    assert len(plan.steps) >= 1


def test_planner_create_plan_with_custom_steps():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={"expression": "10+5"}),
        PlanStep(step_id="step_2", tool="calculator", parameters={"expression": "20+5"}, depends_on=["step_1"]),
    ]
    
    plan = planner.create_plan_with_steps("custom plan", steps, {"tenant_id": "default"})
    
    assert plan is not None
    assert len(plan.steps) == 2
    assert plan.steps[1].depends_on == ["step_1"]


def test_planner_execute_plan():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    plan = planner.create_plan("calculate 5 + 3", {"tenant_id": "default"})
    
    executed_plan = planner.execute_plan_sync(plan.plan_id)
    
    assert executed_plan.status == StepStatus.COMPLETED
    assert executed_plan.final_result is not None


def test_planner_execute_plan_with_dependencies():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={"expression": "10+5"}),
        PlanStep(step_id="step_2", tool="calculator", parameters={"expression": "20+5"}, depends_on=["step_1"]),
    ]
    
    plan = planner.create_plan_with_steps("test deps", steps)
    executed_plan = planner.execute_plan_sync(plan.plan_id)
    
    assert executed_plan.status == StepStatus.COMPLETED


def test_planner_execute_plan_missing_tool():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    steps = [
        PlanStep(step_id="step_1", tool="nonexistent_tool", parameters={}),
    ]
    
    plan = planner.create_plan_with_steps("test", steps)
    executed_plan = planner.execute_plan_sync(plan.plan_id)
    
    assert executed_plan.status == StepStatus.FAILED
    assert executed_plan.steps[0].status == StepStatus.FAILED


def test_planner_get_plan():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    plan = planner.create_plan("test", {"tenant_id": "default"})
    
    retrieved = planner.get_plan(plan.plan_id)
    assert retrieved is not None
    assert retrieved.plan_id == plan.plan_id


def test_planner_list_plans():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    planner.create_plan("test1", {"tenant_id": "default"})
    planner.create_plan("test2", {"tenant_id": "default"})
    
    plans = planner.list_plans()
    assert len(plans) == 2


def test_planner_delete_plan():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    plan = planner.create_plan("test", {"tenant_id": "default"})
    assert planner.delete_plan(plan.plan_id) is True
    assert planner.get_plan(plan.plan_id) is None


def test_planner_clear_plans():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    planner.create_plan("test1", {"tenant_id": "default"})
    planner.create_plan("test2", {"tenant_id": "default"})
    
    planner.clear_plans()
    assert len(planner.list_plans()) == 0


def test_planner_llm_fallback():
    registry = ToolRegistry()
    router = ToolRouter(registry)
    planner = Planner(router)
    
    plan = planner.create_plan("hello", {"tenant_id": "default"})
    
    assert len(plan.steps) >= 1
    assert plan.steps[0].tool == "llm"


def test_planner_execute_with_error():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    router = ToolRouter(registry)
    planner = Planner(router)
    
    steps = [
        PlanStep(step_id="step_1", tool="calculator", parameters={"expression": "invalid"}),
    ]
    
    plan = planner.create_plan_with_steps("test error", steps)
    executed_plan = planner.execute_plan_sync(plan.plan_id)
    
    assert executed_plan.steps[0].status == StepStatus.FAILED
    assert "Error" in executed_plan.steps[0].result

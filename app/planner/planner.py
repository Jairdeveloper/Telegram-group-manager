from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    step_id: str
    tool: str
    parameters: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class Plan:
    plan_id: str
    goal: str
    steps: List[PlanStep]
    status: StepStatus = StepStatus.PENDING
    final_result: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_completed_steps(self) -> List[PlanStep]:
        return [s for s in self.steps if s.status == StepStatus.COMPLETED]
    
    def get_failed_steps(self) -> List[PlanStep]:
        return [s for s in self.steps if s.status == StepStatus.FAILED]
    
    def get_step(self, step_id: str) -> Optional[PlanStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None


class Planner:
    def __init__(self, tool_router):
        self.tool_router = tool_router
        self._plans: Dict[str, Plan] = {}
    
    def create_plan(self, user_goal: str, context: Dict[str, Any]) -> Plan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        steps = self._decompose_goal(user_goal, context)
        
        plan = Plan(
            plan_id=plan_id,
            goal=user_goal,
            steps=steps,
            context=context
        )
        self._plans[plan_id] = plan
        return plan
    
    def create_plan_with_steps(self, user_goal: str, steps: List[PlanStep], context: Dict[str, Any] = None) -> Plan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        plan = Plan(
            plan_id=plan_id,
            goal=user_goal,
            steps=steps,
            context=context or {}
        )
        self._plans[plan_id] = plan
        return plan
    
    def _decompose_goal(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        steps = []
        
        tools = self.tool_router.route(goal, context)
        
        for i, tool_call in enumerate(tools):
            step = PlanStep(
                step_id=f"step_{i + 1}",
                tool=tool_call.tool,
                parameters=tool_call.parameters
            )
            steps.append(step)
        
        if not steps:
            steps.append(PlanStep(
                step_id="step_1",
                tool="llm",
                parameters={"prompt": goal}
            ))
        
        return steps
    
    async def execute_plan(self, plan_id: str) -> Plan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        results = {}
        
        for step in plan.steps:
            if step.depends_on:
                deps_met = all(
                    results.get(dep_id) is not None 
                    for dep_id in step.depends_on
                )
                if not deps_met:
                    step.status = StepStatus.FAILED
                    step.error = "Dependencies not met"
                    continue
            
            step.status = StepStatus.RUNNING
            
            tool = self.tool_router.registry.get_tool(step.tool)
            if tool:
                try:
                    result = tool.handler(**step.parameters)
                    step.result = str(result)
                    results[step.step_id] = step.result
                    
                    if isinstance(result, str) and result.startswith("Error:"):
                        step.error = result
                        step.status = StepStatus.FAILED
                    else:
                        step.status = StepStatus.COMPLETED
                except Exception as e:
                    step.error = str(e)
                    step.result = f"Error: {str(e)}"
                    step.status = StepStatus.FAILED
            else:
                step.error = f"Tool {step.tool} not found"
                step.result = f"Tool {step.tool} not found"
                step.status = StepStatus.FAILED
        
        completed = [s for s in plan.steps if s.status == StepStatus.COMPLETED]
        if completed:
            plan.status = StepStatus.COMPLETED
            plan.final_result = "; ".join(
                f"{s.tool}: {s.result}" 
                for s in plan.steps 
                if s.status == StepStatus.COMPLETED
            )
        else:
            plan.status = StepStatus.FAILED
        
        return plan
    
    def execute_plan_sync(self, plan_id: str) -> Plan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        results = {}
        
        for step in plan.steps:
            if step.depends_on:
                deps_met = all(
                    results.get(dep_id) is not None 
                    for dep_id in step.depends_on
                )
                if not deps_met:
                    step.status = StepStatus.FAILED
                    step.error = "Dependencies not met"
                    continue
            
            step.status = StepStatus.RUNNING
            
            tool = self.tool_router.registry.get_tool(step.tool)
            if tool:
                try:
                    result = tool.handler(**step.parameters)
                    step.result = str(result)
                    results[step.step_id] = step.result
                    
                    if isinstance(result, str) and result.startswith("Error:"):
                        step.error = result
                        step.status = StepStatus.FAILED
                    else:
                        step.status = StepStatus.COMPLETED
                except Exception as e:
                    step.error = str(e)
                    step.result = f"Error: {str(e)}"
                    step.status = StepStatus.FAILED
            else:
                step.error = f"Tool {step.tool} not found"
                step.result = f"Tool {step.tool} not found"
                step.status = StepStatus.FAILED
        
        completed = [s for s in plan.steps if s.status == StepStatus.COMPLETED]
        if completed:
            plan.status = StepStatus.COMPLETED
            plan.final_result = "; ".join(
                f"{s.tool}: {s.result}" 
                for s in plan.steps 
                if s.status == StepStatus.COMPLETED
            )
        else:
            plan.status = StepStatus.FAILED
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)
    
    def list_plans(self) -> List[Plan]:
        return list(self._plans.values())
    
    def delete_plan(self, plan_id: str) -> bool:
        if plan_id in self._plans:
            del self._plans[plan_id]
            return True
        return False
    
    def clear_plans(self) -> None:
        self._plans.clear()

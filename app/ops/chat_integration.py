from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field

from app.policies.engine import PolicyEngine
from app.policies.models import Policy, PolicyRule, PolicyType, Action
from app.guardrails.middleware import apply_guardrails, filter_sensitive_data
from app.tools.registry import ToolRegistry
from app.tools.router import ToolRouter
from app.tools.builtins import register_builtin_tools
from app.planner.planner import Planner, Plan, StepStatus


@dataclass
class ChatContext:
    chat_id: int
    tenant_id: str = "default"
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatResponse:
    success: bool
    response: str
    blocked: bool = False
    blocked_reason: Optional[str] = None
    plan_id: Optional[str] = None
    tools_executed: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChatService:
    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        tool_registry: Optional[ToolRegistry] = None,
        planner: Optional[Planner] = None,
    ):
        self.policy_engine = policy_engine or PolicyEngine()
        self.tool_registry = tool_registry or ToolRegistry()
        self.planner = planner
        
        if not self.planner and self.tool_registry:
            tool_router = ToolRouter(self.tool_registry, self.policy_engine)
            self.planner = Planner(tool_router)
        
        if not self.tool_registry._tools:
            register_builtin_tools(self.tool_registry)
    
    def register_policy(self, policy: Policy) -> None:
        self.policy_engine.register_policy(policy)
    
    def handle_message(self, text: str, context: ChatContext) -> ChatResponse:
        return self._handle_message_sync(text, context)
    
    def _handle_message_sync(self, text: str, context: ChatContext) -> ChatResponse:
        guardrail_result = apply_guardrails(text)
        
        if not guardrail_result.allowed:
            return ChatResponse(
                success=False,
                response=f"Message blocked: {guardrail_result.reason}",
                blocked=True,
                blocked_reason=guardrail_result.reason,
            )
        
        action, msg = self.policy_engine.evaluate(
            context.tenant_id,
            {
                "chat_id": context.chat_id,
                "message": text,
                "tenant_id": context.tenant_id,
                "user_id": context.user_id,
            }
        )
        
        if action == Action.DENY:
            return ChatResponse(
                success=False,
                response=f"Request denied: {msg}",
                blocked=True,
                blocked_reason=msg,
            )
        
        elif action == Action.THROTTLE:
            return ChatResponse(
                success=False,
                response="Too many requests. Please wait.",
                blocked=True,
                blocked_reason="Rate limit exceeded",
            )
        
        if self.planner:
            plan = self.planner.create_plan(
                text,
                {
                    "tenant_id": context.tenant_id,
                    "chat_id": context.chat_id,
                    "user_id": context.user_id,
                }
            )
            
            executed_plan = self.planner.execute_plan_sync(plan.plan_id)
            
            response_text = executed_plan.final_result or "No response generated"
            
            output_guardrail = apply_guardrails(response_text)
            if not output_guardrail.allowed:
                response_text = "Response filtered due to sensitive content"
            
            return ChatResponse(
                success=True,
                response=response_text,
                plan_id=plan.plan_id,
                tools_executed=[s.tool for s in executed_plan.steps if s.status == StepStatus.COMPLETED],
                metadata={"plan_status": executed_plan.status.value},
            )
        
        return ChatResponse(
            success=True,
            response="Message processed",
        )
    
    async def handle_message_async(self, text: str, context: ChatContext) -> ChatResponse:
        guardrail_result = apply_guardrails(text)
        
        if not guardrail_result.allowed:
            return ChatResponse(
                success=False,
                response=f"Message blocked: {guardrail_result.reason}",
                blocked=True,
                blocked_reason=guardrail_result.reason,
            )
        
        action, msg = self.policy_engine.evaluate(
            context.tenant_id,
            {
                "chat_id": context.chat_id,
                "message": text,
                "tenant_id": context.tenant_id,
            }
        )
        
        if action == Action.DENY:
            return ChatResponse(
                success=False,
                response=f"Request denied: {msg}",
                blocked=True,
                blocked_reason=msg,
            )
        
        if self.planner:
            plan = self.planner.create_plan(
                text,
                {"tenant_id": context.tenant_id, "chat_id": context.chat_id}
            )
            
            executed_plan = await self.planner.execute_plan(plan.plan_id)
            
            response_text = executed_plan.final_result or "No response generated"
            
            output_guardrail = apply_guardrails(response_text)
            if not output_guardrail.allowed:
                response_text = "Response filtered due to sensitive content"
            
            return ChatResponse(
                success=True,
                response=response_text,
                plan_id=plan.plan_id,
                tools_executed=[s.tool for s in executed_plan.steps if s.status == StepStatus.COMPLETED],
            )
        
        return ChatResponse(success=True, response="Message processed")
    
    def get_policy_stats(self, tenant_id: str) -> Dict[str, Any]:
        policies = self.policy_engine.list_policies(tenant_id)
        return {
            "tenant_id": tenant_id,
            "policies_count": len(policies),
            "policies": [{"name": p.name, "enabled": p.enabled} for p in policies],
        }
    
    def reset_rate_limits(self, tenant_id: str, chat_id: int) -> None:
        for policy in self.policy_engine.list_policies(tenant_id):
            self.policy_engine.reset_rate_limit(policy.policy_id, str(chat_id))


_default_chat_service: Optional[ChatService] = None


def get_default_chat_service() -> ChatService:
    global _default_chat_service
    if _default_chat_service is None:
        _default_chat_service = ChatService()
    return _default_chat_service


def handle_chat_message(
    chat_id: int,
    text: str,
    tenant_id: str = "default",
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    service = get_default_chat_service()
    
    context = ChatContext(
        chat_id=chat_id,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    response = service.handle_message(text, context)
    
    return {
        "success": response.success,
        "response": response.response,
        "blocked": response.blocked,
        "blocked_reason": response.blocked_reason,
        "plan_id": response.plan_id,
        "tools_executed": response.tools_executed,
        "metadata": response.metadata,
    }

# Implementación Semana 6-8: Policy Engine + Planner

## Objetivo

Implementar un sistema de políticas y planificación que permita:
- Control de acceso y permisos por tenant
- Rate limiting y quotas
- Tool routing (enrutamiento a herramientas)
- Guardrails (filtros de contenido)
- Budgets (control de costos LLM)
- Planner básico para tareas multi-paso

## Estado Actual

- **Motor actual**: `chat_service/pattern_engine.py` (basado en reglas/keywords)
- **Sin**: Policy engine, tool routing, planner, budgets
- **IA**: Solo OpenAI/Ollama como orquestador

---

## Fase 1: Policy Engine - Estructura Base (Semana 6)

### Conceptos Clave

```
Policy → Rules → Actions
  ↓
RateLimit, Quota, AccessControl, ContentFilter
```

### Modelos de Policy

**`app/policies/models.py`**:
```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PolicyType(str, Enum):
    RATE_LIMIT = "rate_limit"
    QUOTA = "quota"
    ACCESS_CONTROL = "access_control"
    CONTENT_FILTER = "content_filter"
    BUDGET = "budget"

class Action(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    THROTTLE = "throttle"
    WARN = "warn"

class PolicyRule(BaseModel):
    policy_type: PolicyType
    name: str
    conditions: Dict[str, Any]  # json logic conditions
    action: Action
    message: Optional[str] = None
    priority: int = 0

class Policy(BaseModel):
    policy_id: str
    tenant_id: str
    name: str
    enabled: bool = True
    rules: List[PolicyRule]
    created_at: datetime = datetime.utcnow()
```

### Tipos de Policies

**`app/policies/types.py`**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: Optional[int] = None

@dataclass
class QuotaConfig:
    monthly_requests: int
    monthly_tokens: int

@dataclass
class BudgetConfig:
    monthly_limit_usd: float
    warning_threshold: float = 0.8

@dataclass
class ContentFilterConfig:
    blocked_keywords: List[str]
    blocked_patterns: List[str]
    max_message_length: int = 4000
    allow_urls: bool = True

@dataclass
class AccessControlConfig:
    allowed_chat_ids: Optional[List[int]] = None
    blocked_chat_ids: Optional[List[int]] = None
    require_approval: bool = False
```

---

## Fase 2: Policy Engine - Implementación (Semana 6)

### Motor de Políticas

**`app/policies/engine.py`**:
```python
from typing import Optional, List, Dict, Any
from app.policies.models import Policy, PolicyRule, Action, PolicyType
from app.policies.types import RateLimitConfig, QuotaConfig, BudgetConfig, ContentFilterConfig
from datetime import datetime, timedelta
import json

class PolicyEngine:
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
        self._rate_limit_store: Dict[str, List[datetime]] = {}
        self._quota_store: Dict[str, Dict[str, int]] = {}
    
    def register_policy(self, policy: Policy):
        self._policies[policy.policy_id] = policy
    
    def evaluate(self, tenant_id: str, context: Dict[str, Any]) -> tuple[Action, str]:
        """Returns (action, message)"""
        policies = [p for p in self._policies.values() 
                   if p.tenant_id == tenant_id and p.enabled]
        
        # Sort by priority (higher first)
        policies.sort(key=lambda p: max(r.priority for r in p.rules), reverse=True)
        
        for policy in policies:
            for rule in policy.rules:
                if self._evaluate_rule(rule, context):
                    return rule.action, rule.message or f"Policy {rule.name} triggered"
        
        return Action.ALLOW, ""
    
    def _evaluate_rule(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        if rule.policy_type == PolicyType.RATE_LIMIT:
            return self._check_rate_limit(rule, context)
        elif rule.policy_type == PolicyType.QUOTA:
            return self._check_quota(rule, context)
        elif rule.policy_type == PolicyType.CONTENT_FILTER:
            return self._check_content_filter(rule, context)
        elif rule.policy_type == PolicyType.BUDGET:
            return self._check_budget(rule, context)
        return False
    
    def _check_rate_limit(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        key = f"{rule.policy_id}:{context.get('chat_id', 'default')}"
        now = datetime.utcnow()
        
        if key not in self._rate_limit_store:
            self._rate_limit_store[key] = []
        
        # Clean old entries
        self._rate_limit_store[key] = [
            ts for ts in self._rate_limit_store[key]
            if now - ts < timedelta(minutes=1)
        ]
        
        limit = rule.conditions.get("requests_per_minute", 60)
        if len(self._rate_limit_store[key]) >= limit:
            return True
        
        self._rate_limit_store[key].append(now)
        return False
    
    def _check_quota(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        key = f"{rule.policy_id}:{context.get('tenant_id')}"
        month = datetime.utcnow().strftime("%Y-%m")
        
        if key not in self._quota_store:
            self._quota_store[key] = {"month": month, "requests": 0}
        
        quota = self._quota_store[key]
        if quota["month"] != month:
            quota["month"] = month
            quota["requests"] = 0
        
        limit = rule.conditions.get("monthly_requests", 10000)
        if quota["requests"] >= limit:
            return True
        
        quota["requests"] += 1
        return False
    
    def _check_content_filter(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        message = context.get("message", "").lower()
        blocked = rule.conditions.get("blocked_keywords", [])
        
        for keyword in blocked:
            if keyword.lower() in message:
                return True
        return False
    
    def _check_budget(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        # Simplified budget check
        spent = context.get("monthly_spent_usd", 0)
        limit = rule.conditions.get("monthly_limit_usd", 100)
        return spent >= limit
```

---

## Fase 3: Tool Routing (Semana 7)

### Definición de Tools

**`app/tools/registry.py`**:
```python
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class ToolType(str, Enum):
    SEARCH = "search"
    CALCULATOR = "calculator"
    WEATHER = "weather"
    DATABASE = "database"
    HTTP = "http"
    CUSTOM = "custom"

@dataclass
class Tool:
    name: str
    description: str
    tool_type: ToolType
    handler: Callable
    parameters: Dict[str, Any]
    requires_approval: bool = False

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())
    
    def find_tools(self, query: str) -> List[Tool]:
        """Find tools matching query based on description"""
        query_lower = query.lower()
        return [t for t in self._tools.values() 
                if query_lower in t.description.lower()]
```

### Router de Tools

**`app/tools/router.py`**:
```python
from typing import List, Optional, Dict, Any
from app.tools.registry import ToolRegistry, Tool
from app.policies.engine import PolicyEngine

class ToolRouter:
    def __init__(self, tool_registry: ToolRegistry, policy_engine: PolicyEngine):
        self.registry = tool_registry
        self.policy_engine = policy_engine
    
    def route(self, user_message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Returns list of tool calls to execute"""
        tools_to_call = []
        
        # Find matching tools
        matching_tools = self.registry.find_tools(user_message)
        
        for tool in matching_tools:
            # Check policy
            action, msg = self.policy_engine.evaluate(
                context.get("tenant_id", "default"),
                {"tool_name": tool.name, "action": "tool_call"}
            )
            
            if action == Action.ALLOW:
                tools_to_call.append({
                    "tool": tool.name,
                    "parameters": self._extract_parameters(tool, user_message)
                })
            elif action == Action.WARN:
                tools_to_call.append({
                    "tool": tool.name,
                    "parameters": self._extract_parameters(tool, user_message),
                    "warning": msg
                })
        
        return tools_to_call
    
    def _extract_parameters(self, tool: Tool, message: str) -> Dict[str, Any]:
        # Simple extraction - can be enhanced with LLM
        return {"raw_input": message}
```

### Ejemplo de Tool

**`app/tools/builtins.py`**:
```python
import math
from app.tools.registry import Tool, ToolType

def calculator_handler(expression: str) -> str:
    """Evaluate mathematical expression"""
    try:
        # Safe eval - only allow numbers and operators
        allowed = set("0123456789+-*/.() ")
        if any(c not in allowed for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def search_handler(query: str) -> str:
    """Search external API (placeholder)"""
    return f"Search results for: {query}"

# Register built-in tools
CALCULATOR_TOOL = Tool(
    name="calculator",
    description="Calculate mathematical expressions",
    tool_type=ToolType.CALCULATOR,
    handler=calculator_handler,
    parameters={"expression": "str"}
)

SEARCH_TOOL = Tool(
    name="search",
    description="Search the web for information",
    tool_type=ToolType.SEARCH,
    handler=search_handler,
    parameters={"query": "str"}
)
```

---

## Fase 4: Planner (Semana 7-8)

### Planner Básico

**`app/planner/planner.py`**:
```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

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
    depends_on: List[str] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    
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

class Planner:
    def __init__(self, tool_router):
        self.tool_router = tool_router
        self._plans: Dict[str, Plan] = {}
    
    def create_plan(self, user_goal: str, context: Dict[str, Any]) -> Plan:
        """Create execution plan from user goal"""
        plan_id = f"plan_{len(self._plans) + 1}"
        
        # Simple planning: decompose goal into tool calls
        steps = self._decompose_goal(user_goal, context)
        
        plan = Plan(plan_id=plan_id, goal=user_goal, steps=steps)
        self._plans[plan_id] = plan
        return plan
    
    def _decompose_goal(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Decompose goal into steps - simple implementation"""
        steps = []
        
        # Route to find tools
        tools = self.tool_router.route(goal, context)
        
        for i, tool_call in enumerate(tools):
            step = PlanStep(
                step_id=f"step_{i + 1}",
                tool=tool_call["tool"],
                parameters=tool_call.get("parameters", {})
            )
            steps.append(step)
        
        # If no tools found, create a single LLM step
        if not steps:
            steps.append(PlanStep(
                step_id="step_1",
                tool="llm",
                parameters={"prompt": goal}
            ))
        
        return steps
    
    async def execute_plan(self, plan_id: str) -> Plan:
        """Execute plan steps"""
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        results = {}
        
        for step in plan.steps:
            # Check dependencies
            if step.depends_on:
                deps_met = all(
                    results.get(dep_id) is not None 
                    for dep_id in step.depends_on
                )
                if not deps_met:
                    step.status = StepStatus.FAILED
                    continue
            
            step.status = StepStatus.RUNNING
            
            # Execute tool
            tool = self.tool_router.registry.get_tool(step.tool)
            if tool:
                try:
                    result = tool.handler(**step.parameters)
                    step.result = result
                    results[step.step_id] = result
                    step.status = StepStatus.COMPLETED
                except Exception as e:
                    step.result = f"Error: {str(e)}"
                    step.status = StepStatus.FAILED
            else:
                step.status = StepStatus.FAILED
                step.result = f"Tool {step.tool} not found"
        
        plan.status = StepStatus.COMPLETED
        plan.final_result = "; ".join(
            f"{s.tool}: {s.result}" 
            for s in plan.steps 
            if s.status == StepStatus.COMPLETED
        )
        
        return plan
    
    def get_plan(self, plan_id: str) -> Plan:
        return self._plans.get(plan_id)
```

---

## Fase 5: Guardrails (Semana 8)

### Sistema de Guardrails

**`app/guardrails/guardrail.py`**:
```python
from typing import List, Tuple, Optional
from dataclasses import dataclass
import re

@dataclass
class GuardrailResult:
    allowed: bool
    filtered_content: Optional[str]
    reason: Optional[str]
    rule_triggered: str

class Guardrails:
    def __init__(self):
        self._blocked_patterns = []
        self._allowed_patterns = []
    
    def add_blocked_pattern(self, pattern: str, description: str):
        self._blocked_patterns.append((re.compile(pattern, re.IGNORECASE), description))
    
    def add_allowed_pattern(self, pattern: str):
        self._allowed_patterns.append(re.compile(pattern, re.IGNORECASE))
    
    def check(self, content: str) -> GuardrailResult:
        # Check blocked patterns
        for pattern, description in self._blocked_patterns:
            match = pattern.search(content)
            if match:
                return GuardrailResult(
                    allowed=False,
                    filtered_content=None,
                    reason=f"Content matches blocked pattern: {description}",
                    rule_triggered=description
                )
        
        # If allowed patterns defined, content must match at least one
        if self._allowed_patterns:
            if not any(p.search(content) for p in self._allowed_patterns):
                return GuardrailResult(
                    allowed=False,
                    filtered_content=None,
                    reason="Content does not match allowed patterns",
                    rule_triggered="allowed_pattern"
                )
        
        return GuardrailResult(
            allowed=True,
            filtered_content=content,
            reason=None,
            rule_triggered=None
        )
    
    def filter(self, content: str, mask_char: str = "*") -> str:
        result = content
        for pattern, description in self._blocked_patterns:
            result = pattern.sub(mask_char * 10, result)
        return result
```

### Integration con Chat

**`app/guardrails/middleware.py`**:
```python
from app.guardrails.guardrail import Guardrails, GuardrailResult

# Default guardrails instance
_default_guardrails = Guardrails()

# Default blocked patterns (PII, etc.)
_default_guardrails.add_blocked_pattern(
    r'\b\d{3}-\d{2}-\d{4}\b', 
    "SSN"
)
_default_guardrails.add_blocked_pattern(
    r'\b\d{16}\b', 
    "Credit Card"
)
_default_guardrails.add_blocked_pattern(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "Email"
)

def apply_guardrails(content: str) -> GuardrailResult:
    return _default_guardrails.check(content)

def filter_sensitive_data(content: str) -> str:
    return _default_guardrails.filter(content)
```

---

## Fase 6: Integration (Semana 8)

### Flujo Completo

```
User Message
    ↓
Guardrails (PII filter)
    ↓
Policy Engine (rate limit, quota, access)
    ↓
Planner (create plan)
    ↓
Tool Router (find tools)
    ↓
Execute Tools
    ↓
LLM (generate response)
    ↓
Guardrails (output filter)
    ↓
Response
```

### Actualizar Chat Service

**`app/ops/services.py`** (actualizar `handle_chat_message`):
```python
from app.policies.engine import PolicyEngine
from app.guardrails.middleware import apply_guardrails, filter_sensitive_data
from app.planner.planner import Planner
from app.tools.router import ToolRouter

# Initialize components
policy_engine = PolicyEngine()
tool_router = ToolRouter(..., policy_engine)
planner = Planner(tool_router)

def handle_chat_message(chat_id: int, text: str, tenant_id: str = "default"):
    # 1. Apply input guardrails
    guardrail_result = apply_guardrails(text)
    if not guardrail_result.allowed:
        return {"response": f"Message blocked: {guardrail_result.reason}"}
    
    # 2. Check policies
    action, msg = policy_engine.evaluate(tenant_id, {
        "chat_id": chat_id,
        "message": text,
        "tenant_id": tenant_id
    })
    
    if action == Action.DENY:
        return {"response": f"Request denied: {msg}"}
    elif action == Action.THROTTLE:
        return {"response": "Too many requests. Please wait."}
    
    # 3. Create and execute plan
    plan = planner.create_plan(text, {"tenant_id": tenant_id, "chat_id": chat_id})
    # ... execute plan
    
    # 4. Apply output guardrails
    response = apply_guardrails(response)
    
    return {"response": response.filtered_content}
```

---

## Tests

**`tests/test_policy_engine.py`**:
```python
import pytest
from app.policies.engine import PolicyEngine, Action
from app.policies.models import Policy, PolicyRule, PolicyType

def test_rate_limit_allows_within_limit():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="test",
        tenant_id="tenant1",
        name="rate limit",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rpm",
            conditions={"requests_per_minute": 10},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    # First 10 should pass
    for i in range(10):
        action, _ = engine.evaluate("tenant1", {"chat_id": 123})
        assert action == Action.ALLOW
    
    # 11th should fail
    action, _ = engine.evaluate("tenant1", {"chat_id": 123})
    assert action == Action.DENY

def test_content_filter_blocks_keyword():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="filter",
        tenant_id="tenant1",
        name="content filter",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="blocked",
            conditions={"blocked_keywords": ["badword"]},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, msg = engine.evaluate("tenant1", {"message": "This contains badword"})
    assert action == Action.DENY
```

---

## Checklist de Release

- [ ] Policy engine base implementado
- [ ] Rate limiting funcionando
- [ ] Quota tracking implementado
- [ ] Content filter con PII
- [ ] Tool registry implementado
- [ ] Tool router funcionando
- [ ] Planner básico implementado
- [ ] Guardrails de entrada y salida
- [ ] Integración con chat service
- [ ] Tests pasando
- [ ] Documentación actualizada

'/mnt/c/Users/1973b/zpa/Projects/manufacturing/robot/01_IMPLEMENTACION_SEMANA_6_8_POLICY_PLANNER.md' Examina el archivo adjuntado y crea una vision general del proyecto respecto a esta implementacion crea un archivo .md que describa lo observado en el analisis del proyecto respecto a la implementacion de esta features
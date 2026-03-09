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
    conditions: Dict[str, Any]
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

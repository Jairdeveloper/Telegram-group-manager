"""Audit models for multi-tenant enterprise."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict, List
from enum import Enum


class AuditEventType(str, Enum):
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    API_KEY_CREATE = "api_key.create"
    API_KEY_REVOKE = "api_key.revoke"
    CHAT_MESSAGE = "chat.message"
    CHAT_MESSAGE_BLOCKED = "chat.message_blocked"
    POLICY_VIOLATION = "policy.violation"
    BILLING_CHANGE = "billing.change"
    TENANT_CREATE = "tenant.create"
    TENANT_UPDATE = "tenant.update"
    CONFIG_CHANGE = "config.change"


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")
    tenant_id: str
    event_type: AuditEventType
    actor_id: Optional[str] = None
    actor_type: str = "system"
    resource_type: str = ""
    resource_id: Optional[str] = None
    action: str = ""
    result: str = "success"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditQuery(BaseModel):
    tenant_id: str
    event_types: Optional[List[AuditEventType]] = None
    actor_id: Optional[str] = None
    resource_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    API_USER = "api_user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: f"usr_{datetime.utcnow().timestamp()}")
    tenant_id: str
    email: str
    username: str
    hashed_password: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False


class ApiKey(BaseModel):
    key_id: str = Field(default_factory=lambda: f"key_{datetime.utcnow().timestamp()}")
    tenant_id: str
    name: str
    key_hash: str
    permissions: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LoginAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: f"att_{datetime.utcnow().timestamp()}")
    user_id: str
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuthSession(BaseModel):
    session_id: str
    user_id: str
    tenant_id: str
    role: UserRole
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

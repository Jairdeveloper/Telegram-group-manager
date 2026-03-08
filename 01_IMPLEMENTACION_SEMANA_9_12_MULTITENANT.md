# Implementación Semana 9-12: Multi-tenant Enterprise

## Objetivo

Transformar la aplicación en una plataforma enterprise multi-tenant con:
- Autenticación y autorización robusta
- Aislamiento completo de datos por tenant
- Cuotas y facturación
- Auditoría completa
- Observabilidad avanzada
- Portal de administración

## Estado Actual

- **Sin**: Autenticación, multi-tenant real, auditoría, portal admin
- **Tenants**: Solo campo `tenant_id` en modelos (Semana 4-5)
- **Auth**: Solo `ADMIN_CHAT_IDS` en Telegram

---

## Fase 1: Autenticación y Autorización (Semana 9)

### Modelos de Usuario y Auth

**`app/auth/models.py`**:
```python
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

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
    user_id: str
    tenant_id: str
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False

class ApiKey(BaseModel):
    key_id: str
    tenant_id: str
    name: str
    key_hash: str
    permissions: List[str]
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    created_at: datetime = datetime.utcnow()

class LoginAttempt(BaseModel):
    attempt_id: str
    user_id: str
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime = datetime.utcnow()
```

### Proveedor de Auth

**`app/auth/provider.py`**:
```python
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
from app.auth.models import User, UserRole, ApiKey
from app.database.repositories import UserRepository

class AuthProvider:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self._sessions: Dict[str, Dict] = {}
    
    def authenticate(self, username: str, password: str, tenant_id: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username, tenant_id)
        if not user:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.user_repo.update(user)
        
        return user
    
    def create_session(self, user: User, ip: str, user_agent: str) -> str:
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            "user_id": user.user_id,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "ip": ip,
            "user_agent": user_agent,
            "created_at": datetime.utcnow()
        }
        return session_id
    
    def verify_session(self, session_id: str) -> Optional[Dict]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Check expiry (24h)
        if datetime.utcnow() - session["created_at"] > timedelta(hours=24):
            del self._sessions[session_id]
            return None
        
        return session
    
    def create_api_key(self, tenant_id: str, name: str, permissions: List[str], 
                      expires_days: Optional[int] = None) -> tuple[ApiKey, str]:
        key_id = secrets.token_hex(8)
        key_value = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(key_value)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key = ApiKey(
            key_id=key_id,
            tenant_id=tenant_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at,
            last_used=None
        )
        
        self.user_repo.save_api_key(api_key)
        return api_key, key_value
    
    def verify_api_key(self, key_value: str, tenant_id: str) -> Optional[ApiKey]:
        key_hash = self._hash_key(key_value)
        api_key = self.user_repo.get_api_key_by_hash(key_hash, tenant_id)
        
        if not api_key:
            return None
        
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key.last_used = datetime.utcnow()
        self.user_repo.update_api_key(api_key)
        
        return api_key
    
    @staticmethod
    def _hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, hashed: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
```

### Middleware de Auth

**`app/auth/middleware.py`**:
```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    # Try session first, then API key
    token = credentials.credentials
    
    # Check session
    session = auth_provider.verify_session(token)
    if session:
        return session
    
    # Check API key
    api_key = auth_provider.verify_api_key(token)
    if api_key:
        return {
            "tenant_id": api_key.tenant_id,
            "permissions": api_key.permissions,
            "type": "api_key"
        }
    
    raise HTTPException(status_code=401, detail="Invalid or expired token")

async def require_role(allowed_roles: List[str]):
    async def role_checker(user: Dict = Depends(get_current_user)):
        user_role = user.get("role", "user")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
```

---

## Fase 2: Aislamiento de Datos (Semana 9-10)

### Repository con Tenant ID

**`app/database/repositories.py`**:
```python
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from app.database.models import Conversation, Tenant, User, ApiKey as ApiKeyModel

class TenantRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get(self, tenant_id: str) -> Optional[Tenant]:
        return self.session.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    
    def create(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        self.session.commit()
        return tenant
    
    def list_all(self) -> List[Tenant]:
        return self.session.query(Tenant).all()

class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def save_message(self, tenant_id: str, session_id: str, user_message: str, 
                    bot_response: str, metadata: dict = None):
        # AUTO-ENFORCE TENANT ISOLATION
        conv = Conversation(
            tenant_id=tenant_id,  # Always set from authenticated context
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            metadata=metadata or {}
        )
        self.session.add(conv)
        self.session.commit()
    
    def get_history(self, tenant_id: str, session_id: str, limit: int = 50) -> List[Conversation]:
        # AUTO-ENFORCE TENANT ISOLATION
        return self.session.query(Conversation).filter(
            Conversation.tenant_id == tenant_id,
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    def get_all_sessions(self, tenant_id: str) -> List[str]:
        # AUTO-ENFORCE TENANT ISOLATION
        results = self.session.query(Conversation.session_id).filter(
            Conversation.tenant_id == tenant_id
        ).distinct().all()
        return [r.session_id for r in results]

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_username(self, username: str, tenant_id: str) -> Optional[User]:
        return self.session.query(User).filter(
            User.username == username,
            User.tenant_id == tenant_id
        ).first()
    
    def save(self, user: User):
        self.session.add(user)
        self.session.commit()
    
    def get_api_key_by_hash(self, key_hash: str, tenant_id: str) -> Optional[ApiKeyModel]:
        return self.session.query(ApiKeyModel).filter(
            ApiKeyModel.key_hash == key_hash,
            ApiKeyModel.tenant_id == tenant_id
        ).first()
```

---

## Fase 3: Cuotas y Facturación (Semana 10)

### Modelos de Facturación

**`app/billing/models.py`**:
```python
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class BillingPeriod(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"

class Plan(BaseModel):
    plan_id: str
    name: str
    plan_type: PlanType
    billing_period: BillingPeriod
    price_usd: float
    features: dict
    
    # Limits
    monthly_requests: int
    monthly_tokens: int
    max_sessions: int
    max_users: int
    custom_branding: bool = False

class Subscription(BaseModel):
    subscription_id: str
    tenant_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False

class Usage(BaseModel):
    usage_id: str
    tenant_id: str
    month: str  # YYYY-MM
    requests_count: int = 0
    tokens_used: int = 0
    api_calls: int = 0
    computed_cost: float = 0.0
```

### Servicio de Facturación

**`app/billing/service.py`**:
```python
from typing import Dict, Optional
from datetime import datetime
from app.billing.models import Plan, Subscription, Usage, SubscriptionStatus, PlanType

PLANS = {
    PlanType.FREE: Plan(
        plan_id="free",
        name="Free",
        plan_type=PlanType.FREE,
        billing_period=BillingPeriod.MONTHLY,
        price_usd=0,
        features={"support": "community", "analytics": False},
        monthly_requests=100,
        monthly_tokens=10000,
        max_sessions=1,
        max_users=1
    ),
    PlanType.STARTER: Plan(
        plan_id="starter",
        name="Starter",
        plan_type=PlanType.STARTER,
        billing_period=BillingPeriod.MONTHLY,
        price_usd=29,
        features={"support": "email", "analytics": True},
        monthly_requests=1000,
        monthly_tokens=100000,
        max_sessions=5,
        max_users=5
    ),
    PlanType.PROFESSIONAL: Plan(
        plan_id="professional",
        name="Professional",
        plan_type=PlanType.PROFESSIONAL,
        billing_period=BillingPeriod.MONTHLY,
        price_usd=99,
        features={"support": "priority", "analytics": True, "api": True},
        monthly_requests=10000,
        monthly_tokens=1000000,
        max_sessions=50,
        max_users=25
    ),
    PlanType.ENTERPRISE: Plan(
        plan_id="enterprise",
        name="Enterprise",
        plan_type=PlanType.ENTERPRISE,
        billing_period=BillingPeriod.MONTHLY,
        price_usd=0,  # Custom pricing
        features={"support": "24/7", "analytics": True, "api": True, "sla": True},
        monthly_requests=-1,  # Unlimited
        monthly_tokens=-1,
        max_sessions=-1,
        max_users=-1,
        custom_branding=True
    ),
}

class BillingService:
    def __init__(self, usage_repo, subscription_repo):
        self.usage_repo = usage_repo
        self.subscription_repo = subscription_repo
    
    def check_limit(self, tenant_id: str, limit_type: str) -> tuple[bool, str]:
        """Check if tenant has exceeded a limit"""
        subscription = self.subscription_repo.get_active(tenant_id)
        if not subscription:
            plan = PLANS[PlanType.FREE]
        else:
            plan = PLANS[subscription.plan_id]
        
        usage = self.usage_repo.get_current(tenant_id)
        
        if limit_type == "requests":
            if plan.monthly_requests > 0 and usage.requests_count >= plan.monthly_requests:
                return False, f"Monthly request limit ({plan.monthly_requests}) exceeded"
        
        elif limit_type == "tokens":
            if plan.monthly_tokens > 0 and usage.tokens_used >= plan.monthly_tokens:
                return False, f"Monthly token limit ({plan.monthly_tokens}) exceeded"
        
        elif limit_type == "sessions":
            if plan.max_sessions > 0:
                # Check active sessions
                pass  # Implementation
        
        return True, ""
    
    def track_usage(self, tenant_id: str, requests: int = 1, tokens: int = 0):
        """Track usage for a tenant"""
        usage = self.usage_repo.get_current(tenant_id)
        usage.requests_count += requests
        usage.tokens_used += tokens
        
        # Calculate cost
        subscription = self.subscription_repo.get_active(tenant_id)
        if not subscription:
            plan = PLANS[PlanType.FREE]
        else:
            plan = PLANS[subscription.plan_id]
        
        # Overage pricing
        overage_requests = max(0, usage.requests_count - plan.monthly_requests)
        overage_tokens = max(0, usage.tokens_used - plan.monthly_tokens)
        
        usage.computed_cost = (
            plan.price_usd +
            (overage_requests * 0.001) +  # $0.001 per overage request
            (overage_tokens * 0.0001)       # $0.0001 per overage token
        )
        
        self.usage_repo.save(usage)
    
    def get_tenant_usage(self, tenant_id: str) -> Usage:
        return self.usage_repo.get_current(tenant_id)
    
    def get_available_plans(self) -> list[Plan]:
        return list(PLANS.values())
```

---

## Fase 4: Auditoría (Semana 10-11)

### Modelo de Auditoría

**`app/audit/models.py`**:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict
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
    event_id: str
    tenant_id: str
    event_type: AuditEventType
    actor_id: Optional[str]  # Who performed the action
    actor_type: str  # user, api_key, system
    resource_type: str
    resource_id: Optional[str]
    action: str
    result: str  # success, failure
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.utcnow()

class AuditQuery(BaseModel):
    tenant_id: str
    event_types: Optional[List[AuditEventType]]
    actor_id: Optional[str]
    resource_id: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    limit: int = 100
```

### Servicio de Auditoría

**`app/audit/service.py`**:
```python
from typing import List, Optional
from datetime import datetime
from app.audit.models import AuditEvent, AuditEventType, AuditQuery
import secrets

class AuditService:
    def __init__(self, audit_repo):
        self.audit_repo = audit_repo
    
    def log(self, tenant_id: str, event_type: AuditEventType, 
            actor_id: Optional[str] = None, actor_type: str = "system",
            resource_type: str = "", resource_id: Optional[str] = None,
            action: str = "", result: str = "success",
            ip_address: Optional[str] = None, user_agent: Optional[str] = None,
            metadata: dict = None):
        
        event = AuditEvent(
            event_id=secrets.token_hex(16),
            tenant_id=tenant_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        self.audit_repo.save(event)
    
    def query(self, query: AuditQuery) -> List[AuditEvent]:
        return self.audit_repo.query(
            tenant_id=query.tenant_id,
            event_types=query.event_types,
            actor_id=query.actor_id,
            resource_id=query.resource_id,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit
        )
    
    def get_user_activity(self, tenant_id: str, user_id: str, 
                         limit: int = 50) -> List[AuditEvent]:
        return self.audit_repo.query(
            tenant_id=tenant_id,
            actor_id=user_id,
            limit=limit
        )
```

---

## Fase 5: Observabilidad (Semana 11)

### Métricas Enterprise

**`app/monitoring/metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# Tenant-level metrics
TENANT_REQUESTS = Counter(
    'tenant_requests_total',
    'Total requests per tenant',
    ['tenant_id', 'endpoint', 'status']
)

TENANT_LATENCY = Histogram(
    'tenant_request_latency_seconds',
    'Request latency per tenant',
    ['tenant_id', 'endpoint']
)

TENANT_TOKENS = Counter(
    'tenant_tokens_total',
    'Tokens used per tenant',
    ['tenant_id', 'model']
)

TENANT_ACTIVE_SESSIONS = Gauge(
    'tenant_active_sessions',
    'Active sessions per tenant',
    ['tenant_id']
)

TENANT_COST = Gauge(
    'tenant_monthly_cost_usd',
    'Monthly accumulated cost per tenant',
    ['tenant_id']
)

TENANT_USAGE_PERCENT = Gauge(
    'tenant_usage_percent',
    'Percentage of plan limit used',
    ['tenant_id', 'resource_type']
)

# System metrics
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Overall request latency')
ACTIVE_USERS = Gauge('active_users', 'Active users in last hour')
ERROR_RATE = Counter('errors_total', 'Total errors', ['type', 'endpoint'])
```

### Health Checks Enterprise

**`app/monitoring/health.py`**:
```python
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ComponentHealth:
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    details: Dict[str, Any]

class HealthCheck:
    def __init__(self, db_repo, redis_client, external_apis: Dict[str, str]):
        self.db_repo = db_repo
        self.redis_client = redis_client
        self.external_apis = external_apis
    
    async def check_all(self) -> Dict[str, ComponentHealth]:
        results = {}
        
        # Database
        results["database"] = await self._check_database()
        
        # Redis
        results["redis"] = await self._check_redis()
        
        # External APIs
        for name, url in self.external_apis.items():
            results[f"api_{name}"] = await self._check_api(name, url)
        
        return results
    
    async def _check_database(self) -> ComponentHealth:
        import time
        start = time.time()
        try:
            # Simple query to check DB
            self.db_repo.execute("SELECT 1")
            latency = (time.time() - start) * 1000
            return ComponentHealth("database", "healthy", latency, {})
        except Exception as e:
            return ComponentHealth("database", "unhealthy", 0, {"error": str(e)})
    
    async def _check_redis(self) -> ComponentHealth:
        import time
        start = time.time()
        try:
            self.redis_client.ping()
            latency = (time.time() - start) * 1000
            return ComponentHealth("redis", "healthy", latency, {})
        except Exception as e:
            return ComponentHealth("redis", "unhealthy", 0, {"error": str(e)})
```

---

## Fase 6: Portal de Administración (Semana 11-12)

### Endpoints del Portal

**`app/admin/routes.py`**:
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.auth.middleware import get_current_user, require_role
from app.billing.service import BillingService
from app.audit.service import AuditService
from app.monitoring.health import HealthCheck

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/tenants")
async def list_tenants(
    user: Dict = Depends(require_role(["admin"]))
):
    """List all tenants - admin only"""
    return {"tenants": tenant_repo.list_all()}

@router.get("/tenants/{tenant_id}/usage")
async def tenant_usage(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin", "manager"]))
):
    """Get tenant usage statistics"""
    usage = billing_service.get_tenant_usage(tenant_id)
    return usage

@router.get("/tenants/{tenant_id}/audit")
async def tenant_audit(
    tenant_id: str,
    limit: int = 100,
    user: Dict = Depends(require_role(["admin"]))
):
    """Get tenant audit log"""
    events = audit_service.query(AuditQuery(tenant_id=tenant_id, limit=limit))
    return {"events": events}

@router.get("/health")
async def system_health(user: Dict = Depends(require_role(["admin"]))):
    """System health check"""
    return await health_check.check_all()

@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    reason: str,
    user: Dict = Depends(require_role(["admin"]))
):
    """Suspend a tenant"""
    tenant_repo.suspend(tenant_id, reason)
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.TENANT_UPDATE,
        actor_id=user["user_id"],
        action="suspend",
        metadata={"reason": reason}
    )
    return {"status": "suspended"}

@router.get("/billing/plans")
async def list_plans():
    """List available plans"""
    return {"plans": billing_service.get_available_plans()}
```

---

## Fase 7: API Pública Multi-tenant (Semana 12)

### API con Auth

**`app/api/enterprise_routes.py`**:
```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth.middleware import get_current_user
from app.billing.service import BillingService
from app.database.repositories import ConversationRepository

router = APIRouter(prefix="/api/v1", tags=["enterprise"])

@router.post("/chat")
async def chat(
    message: str,
    session_id: str,
    user: Dict = Depends(get_current_user)
):
    # Extract tenant from auth context
    tenant_id = user["tenant_id"]
    
    # Check limits
    allowed, msg = billing_service.check_limit(tenant_id, "requests")
    if not allowed:
        raise HTTPException(429, detail=msg)
    
    # Process message
    response = process_message(tenant_id, session_id, message)
    
    # Track usage
    billing_service.track_usage(tenant_id, requests=1)
    
    # Audit
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.CHAT_MESSAGE,
        actor_id=user.get("user_id") or user.get("key_id"),
        actor_type=user.get("type", "user"),
        resource_type="session",
        resource_id=session_id
    )
    
    return response

@router.get("/history/{session_id}")
async def history(
    session_id: str,
    limit: int = 50,
    user: Dict = Depends(get_current_user)
):
    tenant_id = user["tenant_id"]
    messages = conversation_repo.get_history(tenant_id, session_id, limit)
    return {"session_id": session_id, "messages": messages}
```

---

## Checklist de Release

- [ ] Modelos de usuario y auth implementados
- [ ] Proveedor de auth con sesiones y API keys
- [ ] Middleware de autenticación FastAPI
- [ ] Aislamiento de datos por tenant en repositories
- [ ] Sistema de planes y suscripciones
- [ ] Tracking de uso y costos
- [ ] Servicio de auditoría implementado
- [ ] Logs de auditoría consultables
- [ ] Métricas Prometheus por tenant
- [ ] Health checks enterprise
- [ ] Portal de administración con endpoints
- [ ] API pública con auth y rate limiting
- [ ] Tests de seguridad pasando
- [ ] Documentación de API actualizada

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────────┐
│                     Portal Admin                             │
│  (Gestión de tenants, usuarios, facturación, auditoría)     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    API Gateway                               │
│  (Auth, Rate Limit, Tenant Routing)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Core Services                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Policy     │  │  Planner    │  │  Chat Service       │ │
│  │  Engine     │  │             │  │  (Rules + LLM)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Billing    │  │  Audit     │  │  Monitoring         │ │
│  │  Service    │  │  Service   │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   PostgreSQL                                 │
│  (Tenants, Users, Conversations, Audit, Billing)            │
└─────────────────────────────────────────────────────────────┘
```

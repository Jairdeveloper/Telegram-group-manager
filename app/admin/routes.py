"""Admin routes for multi-tenant enterprise portal."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from datetime import datetime

from app.auth.middleware import get_current_user, require_role
from app.billing import get_billing_service, PlanType, BillingPeriod
from app.audit import get_audit_service, AuditEventType, AuditQuery
from app.monitoring import get_health_check
from app.database.repositories import (
    get_tenant_repository,
    get_user_repository,
    TenantRepository,
)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/tenants")
async def list_tenants(
    user: Dict = Depends(require_role(["admin"])),
    tenant_repo: TenantRepository = Depends(get_tenant_repository)
) -> Dict:
    """List all tenants - admin only."""
    tenants = tenant_repo.list_all()
    return {
        "tenants": [
            {
                "tenant_id": t.tenant_id,
                "name": t.name,
                "is_active": t.is_active == 1 if isinstance(t.is_active, int) else t.is_active,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "settings": t.settings
            }
            for t in tenants
        ]
    }


@router.get("/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin"])),
    tenant_repo: TenantRepository = Depends(get_tenant_repository)
) -> Dict:
    """Get tenant details - admin only."""
    tenant = tenant_repo.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return {
        "tenant_id": tenant.tenant_id,
        "name": tenant.name,
        "is_active": tenant.is_active == 1 if isinstance(tenant.is_active, int) else tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "settings": tenant.settings
    }


@router.get("/tenants/{tenant_id}/usage")
async def tenant_usage(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin", "manager"])),
    billing_service=Depends(get_billing_service)
) -> Dict:
    """Get tenant usage statistics."""
    usage = billing_service.get_tenant_usage(tenant_id)
    return {
        "tenant_id": tenant_id,
        "month": usage.month,
        "requests_count": usage.requests_count,
        "tokens_used": usage.tokens_used,
        "computed_cost": usage.computed_cost
    }


@router.get("/tenants/{tenant_id}/users")
async def tenant_users(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin", "manager"])),
    user_repo=Depends(get_user_repository)
) -> Dict:
    """Get tenant users."""
    users = user_repo.list_users(tenant_id)
    return {
        "users": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    }


@router.get("/tenants/{tenant_id}/audit")
async def tenant_audit(
    tenant_id: str,
    limit: int = 100,
    user: Dict = Depends(require_role(["admin"])),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Get tenant audit log."""
    events = audit_service.query(AuditQuery(tenant_id=tenant_id, limit=limit))
    return {
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value if hasattr(e.event_type, 'value') else e.event_type,
                "actor_id": e.actor_id,
                "action": e.action,
                "result": e.result,
                "ip_address": e.ip_address,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None
            }
            for e in events
        ]
    }


@router.get("/health")
async def system_health(
    user: Dict = Depends(require_role(["admin"]))
) -> Dict:
    """System health check."""
    health_check = get_health_check()
    results = await health_check.check_all()
    return {
        "components": {
            name: {
                "status": comp.status,
                "latency_ms": comp.latency_ms,
                "details": comp.details
            }
            for name, comp in results.items()
        }
    }


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    reason: str,
    user: Dict = Depends(require_role(["admin"])),
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Suspend a tenant."""
    success = tenant_repo.suspend(tenant_id, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.TENANT_UPDATE,
        actor_id=user.get("user_id"),
        action="suspend",
        metadata={"reason": reason}
    )
    
    return {"status": "suspended", "tenant_id": tenant_id}


@router.post("/tenants/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin"])),
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Activate a suspended tenant."""
    success = tenant_repo.activate(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.TENANT_UPDATE,
        actor_id=user.get("user_id"),
        action="activate"
    )
    
    return {"status": "activated", "tenant_id": tenant_id}


@router.post("/tenants")
async def create_tenant(
    name: str,
    user: Dict = Depends(require_role(["admin"])),
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Create a new tenant."""
    import secrets
    from app.database.models import Tenant
    
    tenant_id = f"tenant_{secrets.token_hex(8)}"
    tenant = Tenant(
        tenant_id=tenant_id,
        name=name,
        settings={},
        is_active=1
    )
    
    tenant_repo.create(tenant)
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.TENANT_CREATE,
        actor_id=user.get("user_id"),
        action="create",
        metadata={"name": name}
    )
    
    return {
        "tenant_id": tenant_id,
        "name": name,
        "status": "created"
    }


@router.get("/billing/plans")
async def list_plans(
    user: Dict = Depends(require_role(["admin", "manager"])),
    billing_service=Depends(get_billing_service)
) -> Dict:
    """List available billing plans."""
    plans = billing_service.get_available_plans()
    return {
        "plans": [
            {
                "plan_id": p.plan_id,
                "name": p.name,
                "plan_type": p.plan_type.value if hasattr(p.plan_type, 'value') else p.plan_type,
                "price_usd": p.price_usd,
                "monthly_requests": p.monthly_requests,
                "monthly_tokens": p.monthly_tokens,
                "max_sessions": p.max_sessions,
                "max_users": p.max_users,
                "features": p.features
            }
            for p in plans
        ]
    }


@router.post("/tenants/{tenant_id}/subscription")
async def create_subscription(
    tenant_id: str,
    plan_type: str,
    billing_period: str = "monthly",
    user: Dict = Depends(require_role(["admin"])),
    billing_service=Depends(get_billing_service),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Create subscription for tenant."""
    try:
        plan = PlanType(plan_type)
        period = BillingPeriod(billing_period)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan_type or billing_period")
    
    subscription = billing_service.create_subscription(tenant_id, plan, period)
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.BILLING_CHANGE,
        actor_id=user.get("user_id"),
        action="create_subscription",
        metadata={"plan_type": plan_type, "billing_period": billing_period}
    )
    
    return {
        "subscription_id": subscription.subscription_id,
        "plan_id": subscription.plan_id,
        "status": subscription.status.value if hasattr(subscription.status, 'value') else subscription.status,
        "current_period_end": subscription.current_period_end.isoformat()
    }


@router.post("/tenants/{tenant_id}/subscription/cancel")
async def cancel_subscription(
    tenant_id: str,
    user: Dict = Depends(require_role(["admin"])),
    billing_service=Depends(get_billing_service),
    audit_service=Depends(get_audit_service)
) -> Dict:
    """Cancel tenant subscription."""
    success = billing_service.cancel_subscription(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.BILLING_CHANGE,
        actor_id=user.get("user_id"),
        action="cancel_subscription"
    )
    
    return {"status": "cancelled"}

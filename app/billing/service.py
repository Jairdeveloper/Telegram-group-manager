"""Billing service for quotas and usage tracking."""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import secrets

from app.billing.models import (
    Plan, Subscription, Usage, PlanType, BillingPeriod, SubscriptionStatus
)


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
        price_usd=0,
        features={"support": "24/7", "analytics": True, "api": True, "sla": True},
        monthly_requests=-1,
        monthly_tokens=-1,
        max_sessions=-1,
        max_users=-1,
        custom_branding=True
    ),
}


class UsageRepository(ABC):
    """Abstract base class for usage tracking."""

    @abstractmethod
    def get_current(self, tenant_id: str) -> Usage:
        """Get current month's usage."""
        pass

    @abstractmethod
    def get_by_month(self, tenant_id: str, month: str) -> Optional[Usage]:
        """Get usage for specific month."""
        pass

    @abstractmethod
    def save(self, usage: Usage) -> None:
        """Save usage record."""
        pass

    @abstractmethod
    def reset_month(self, tenant_id: str, month: str) -> None:
        """Reset usage for new month."""
        pass


class SubscriptionRepository(ABC):
    """Abstract base class for subscription management."""

    @abstractmethod
    def get_active(self, tenant_id: str) -> Optional[Subscription]:
        """Get active subscription for tenant."""
        pass

    @abstractmethod
    def get(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        pass

    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        """Save subscription."""
        pass

    @abstractmethod
    def update(self, subscription: Subscription) -> None:
        """Update subscription."""
        pass


class InMemoryUsageRepository(UsageRepository):
    """In-memory implementation of UsageRepository."""

    def __init__(self):
        self._usage: Dict[str, Usage] = {}

    def _get_key(self, tenant_id: str, month: str) -> str:
        return f"{tenant_id}:{month}"

    def get_current(self, tenant_id: str) -> Usage:
        month = datetime.utcnow().strftime("%Y-%m")
        key = self._get_key(tenant_id, month)
        
        if key not in self._usage:
            self._usage[key] = Usage(
                tenant_id=tenant_id,
                month=month,
                requests_count=0,
                tokens_used=0,
                api_calls=0,
                computed_cost=0.0
            )
        
        return self._usage[key]

    def get_by_month(self, tenant_id: str, month: str) -> Optional[Usage]:
        key = self._get_key(tenant_id, month)
        return self._usage.get(key)

    def save(self, usage: Usage) -> None:
        key = self._get_key(usage.tenant_id, usage.month)
        self._usage[key] = usage

    def reset_month(self, tenant_id: str, month: str) -> None:
        key = self._get_key(tenant_id, month)
        self._usage[key] = Usage(
            tenant_id=tenant_id,
            month=month,
            requests_count=0,
            tokens_used=0,
            api_calls=0,
            computed_cost=0.0
        )


class InMemorySubscriptionRepository(SubscriptionRepository):
    """In-memory implementation of SubscriptionRepository."""

    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}

    def get_active(self, tenant_id: str) -> Optional[Subscription]:
        for sub in self._subscriptions.values():
            if sub.tenant_id == tenant_id and sub.status == SubscriptionStatus.ACTIVE:
                return sub
        return None

    def get(self, subscription_id: str) -> Optional[Subscription]:
        return self._subscriptions.get(subscription_id)

    def save(self, subscription: Subscription) -> None:
        self._subscriptions[subscription.subscription_id] = subscription

    def update(self, subscription: Subscription) -> None:
        if subscription.subscription_id in self._subscriptions:
            self._subscriptions[subscription.subscription_id] = subscription


class BillingService:
    """Service for managing billing and quotas."""

    def __init__(
        self,
        usage_repo: Optional[UsageRepository] = None,
        subscription_repo: Optional[SubscriptionRepository] = None
    ):
        self.usage_repo = usage_repo or InMemoryUsageRepository()
        self.subscription_repo = subscription_repo or InMemorySubscriptionRepository()

    def get_plan(self, plan_type: PlanType) -> Plan:
        return PLANS[plan_type]

    def get_plan_by_id(self, plan_id: str) -> Optional[Plan]:
        for plan in PLANS.values():
            if plan.plan_id == plan_id:
                return plan
        return None

    def check_limit(self, tenant_id: str, limit_type: str) -> tuple[bool, str]:
        subscription = self.subscription_repo.get_active(tenant_id)
        
        if subscription:
            plan = self.get_plan_by_id(subscription.plan_id)
        else:
            plan = PLANS[PlanType.FREE]

        usage = self.usage_repo.get_current(tenant_id)

        if limit_type == "requests":
            if plan.monthly_requests > 0 and usage.requests_count >= plan.monthly_requests:
                return False, f"Monthly request limit ({plan.monthly_requests}) exceeded"
        
        elif limit_type == "tokens":
            if plan.monthly_tokens > 0 and usage.tokens_used >= plan.monthly_tokens:
                return False, f"Monthly token limit ({plan.monthly_tokens}) exceeded"
        
        elif limit_type == "sessions":
            if plan.max_sessions > 0:
                active_sessions = self._get_active_sessions(tenant_id)
                if active_sessions >= plan.max_sessions:
                    return False, f"Active session limit ({plan.max_sessions}) exceeded"
        
        elif limit_type == "users":
            if plan.max_users > 0:
                user_count = self._get_user_count(tenant_id)
                if user_count >= plan.max_users:
                    return False, f"User limit ({plan.max_users}) exceeded"

        return True, ""

    def _get_active_sessions(self, tenant_id: str) -> int:
        from app.auth.provider import auth_provider
        return auth_provider.get_active_sessions_count(tenant_id)

    def _get_user_count(self, tenant_id: str) -> int:
        from app.database.repositories import get_user_repository
        user_repo = get_user_repository()
        return len(user_repo.list_users(tenant_id))

    def track_usage(self, tenant_id: str, requests: int = 1, tokens: int = 0):
        usage = self.usage_repo.get_current(tenant_id)
        usage.requests_count += requests
        usage.tokens_used += tokens

        subscription = self.subscription_repo.get_active(tenant_id)
        
        if subscription:
            plan = self.get_plan_by_id(subscription.plan_id)
        else:
            plan = PLANS[PlanType.FREE]

        overage_requests = max(0, usage.requests_count - max(0, plan.monthly_requests))
        overage_tokens = max(0, usage.tokens_used - max(0, plan.monthly_tokens))

        usage.computed_cost = (
            plan.price_usd +
            (overage_requests * 0.001) +
            (overage_tokens * 0.0001)
        )

        self.usage_repo.save(usage)

    def get_tenant_usage(self, tenant_id: str) -> Usage:
        return self.usage_repo.get_current(tenant_id)

    def get_tenant_usage_by_month(self, tenant_id: str, month: str) -> Optional[Usage]:
        return self.usage_repo.get_by_month(tenant_id, month)

    def get_available_plans(self) -> List[Plan]:
        return list(PLANS.values())

    def create_subscription(
        self,
        tenant_id: str,
        plan_type: PlanType,
        billing_period: BillingPeriod = BillingPeriod.MONTHLY
    ) -> Subscription:
        plan = PLANS[plan_type]
        
        now = datetime.utcnow()
        if billing_period == BillingPeriod.MONTHLY:
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)

        subscription = Subscription(
            subscription_id=f"sub_{secrets.token_hex(8)}",
            tenant_id=tenant_id,
            plan_id=plan.plan_id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=period_end
        )

        self.subscription_repo.save(subscription)
        
        self.usage_repo.reset_month(tenant_id, now.strftime("%Y-%m"))

        return subscription

    def cancel_subscription(self, tenant_id: str) -> bool:
        subscription = self.subscription_repo.get_active(tenant_id)
        if subscription:
            subscription.cancel_at_period_end = True
            self.subscription_repo.update(subscription)
            return True
        return False


_billing_service: Optional[BillingService] = None


def get_billing_service() -> BillingService:
    global _billing_service
    if _billing_service is None:
        _billing_service = BillingService()
    return _billing_service


def set_billing_service(service: BillingService) -> None:
    global _billing_service
    _billing_service = service

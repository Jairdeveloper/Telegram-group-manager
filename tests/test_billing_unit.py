"""Tests for billing module."""
import pytest
from datetime import datetime
from app.billing.models import PlanType, BillingPeriod, SubscriptionStatus, Plan, Subscription, Usage
from app.billing.service import BillingService, InMemoryUsageRepository, InMemorySubscriptionRepository, PLANS


class TestBillingModels:
    def test_plan_type_enum(self):
        assert PlanType.FREE.value == "free"
        assert PlanType.STARTER.value == "starter"
        assert PlanType.PROFESSIONAL.value == "professional"
        assert PlanType.ENTERPRISE.value == "enterprise"

    def test_billing_period_enum(self):
        assert BillingPeriod.MONTHLY.value == "monthly"
        assert BillingPeriod.YEARLY.value == "yearly"

    def test_subscription_status_enum(self):
        assert SubscriptionStatus.ACTIVE.value == "active"
        assert SubscriptionStatus.PAST_DUE.value == "past_due"
        assert SubscriptionStatus.CANCELLED.value == "cancelled"
        assert SubscriptionStatus.TRIALING.value == "trialing"

    def test_plan_model(self):
        plan = Plan(
            plan_id="test",
            name="Test Plan",
            plan_type=PlanType.PROFESSIONAL,
            billing_period=BillingPeriod.MONTHLY,
            price_usd=99,
            features={"test": True},
            monthly_requests=1000,
            monthly_tokens=100000,
            max_sessions=10,
            max_users=5
        )
        assert plan.plan_id == "test"
        assert plan.price_usd == 99

    def test_usage_model(self):
        usage = Usage(
            tenant_id="tenant_1",
            month="2026-03",
            requests_count=100,
            tokens_used=1000,
            computed_cost=10.0
        )
        assert usage.tenant_id == "tenant_1"
        assert usage.requests_count == 100


class TestPlans:
    def test_free_plan(self):
        plan = PLANS[PlanType.FREE]
        assert plan.plan_id == "free"
        assert plan.price_usd == 0
        assert plan.monthly_requests == 100

    def test_starter_plan(self):
        plan = PLANS[PlanType.STARTER]
        assert plan.plan_id == "starter"
        assert plan.price_usd == 29

    def test_professional_plan(self):
        plan = PLANS[PlanType.PROFESSIONAL]
        assert plan.plan_id == "professional"
        assert plan.price_usd == 99

    def test_enterprise_plan(self):
        plan = PLANS[PlanType.ENTERPRISE]
        assert plan.plan_id == "enterprise"
        assert plan.monthly_requests == -1  # Unlimited


class TestBillingService:
    @pytest.fixture
    def billing_service(self):
        usage_repo = InMemoryUsageRepository()
        subscription_repo = InMemorySubscriptionRepository()
        return BillingService(usage_repo, subscription_repo)

    def test_get_plan(self, billing_service):
        plan = billing_service.get_plan(PlanType.FREE)
        assert plan.plan_id == "free"

    def test_get_plan_by_id(self, billing_service):
        plan = billing_service.get_plan_by_id("professional")
        assert plan is not None
        assert plan.plan_id == "professional"

    def test_get_plan_by_id_not_found(self, billing_service):
        plan = billing_service.get_plan_by_id("nonexistent")
        assert plan is None

    def test_check_limit_requests_within_limit(self, billing_service):
        allowed, msg = billing_service.check_limit("tenant_1", "requests")
        assert allowed is True
        assert msg == ""

    def test_check_limit_requests_exceeded(self, billing_service):
        billing_service.track_usage("tenant_1", requests=150)
        
        allowed, msg = billing_service.check_limit("tenant_1", "requests")
        assert allowed is False
        assert "exceeded" in msg

    def test_check_limit_tokens_within_limit(self, billing_service):
        allowed, msg = billing_service.check_limit("tenant_1", "tokens")
        assert allowed is True

    def test_check_limit_tokens_exceeded(self, billing_service):
        billing_service.track_usage("tenant_1", tokens=20000)
        
        allowed, msg = billing_service.check_limit("tenant_1", "tokens")
        assert allowed is False
        assert "exceeded" in msg

    def test_track_usage(self, billing_service):
        billing_service.track_usage("tenant_1", requests=10, tokens=100)
        
        usage = billing_service.get_tenant_usage("tenant_1")
        assert usage.requests_count == 10
        assert usage.tokens_used == 100

    def test_track_usage_calculates_cost(self, billing_service):
        billing_service.track_usage("tenant_1", requests=200, tokens=20000)
        
        usage = billing_service.get_tenant_usage("tenant_1")
        assert usage.computed_cost > 0

    def test_get_available_plans(self, billing_service):
        plans = billing_service.get_available_plans()
        assert len(plans) == 4
        plan_ids = [p.plan_id for p in plans]
        assert "free" in plan_ids
        assert "starter" in plan_ids
        assert "professional" in plan_ids
        assert "enterprise" in plan_ids

    def test_create_subscription(self, billing_service):
        subscription = billing_service.create_subscription(
            "tenant_1",
            PlanType.PROFESSIONAL,
            BillingPeriod.MONTHLY
        )
        
        assert subscription.tenant_id == "tenant_1"
        assert subscription.plan_id == "professional"
        assert subscription.status == SubscriptionStatus.ACTIVE

    def test_cancel_subscription(self, billing_service):
        billing_service.create_subscription("tenant_1", PlanType.STARTER)
        
        result = billing_service.cancel_subscription("tenant_1")
        assert result is True
        
        subscription = billing_service.subscription_repo.get_active("tenant_1")
        assert subscription.cancel_at_period_end is True

    def test_cancel_subscription_not_found(self, billing_service):
        result = billing_service.cancel_subscription("nonexistent")
        assert result is False


class TestTenantUsage:
    @pytest.fixture
    def billing_service(self):
        return BillingService(InMemoryUsageRepository(), InMemorySubscriptionRepository())

    def test_usage_isolation_between_tenants(self, billing_service):
        billing_service.track_usage("tenant_1", requests=100)
        billing_service.track_usage("tenant_2", requests=50)
        
        usage_1 = billing_service.get_tenant_usage("tenant_1")
        usage_2 = billing_service.get_tenant_usage("tenant_2")
        
        assert usage_1.requests_count == 100
        assert usage_2.requests_count == 50

    def test_usage_persists_per_month(self, billing_service):
        billing_service.track_usage("tenant_1", requests=50)
        
        usage = billing_service.get_tenant_usage("tenant_1")
        assert usage.month == datetime.utcnow().strftime("%Y-%m")

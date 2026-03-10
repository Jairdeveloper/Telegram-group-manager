"""Billing models for multi-tenant enterprise."""
from enum import Enum
from pydantic import BaseModel, Field
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
    features: dict = Field(default_factory=dict)
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
    usage_id: str = Field(default_factory=lambda: f"use_{datetime.utcnow().timestamp()}")
    tenant_id: str
    month: str
    requests_count: int = 0
    tokens_used: int = 0
    api_calls: int = 0
    computed_cost: float = 0.0

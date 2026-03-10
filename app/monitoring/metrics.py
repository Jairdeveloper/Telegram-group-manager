"""Metrics for multi-tenant enterprise monitoring."""
from typing import Optional
from datetime import datetime

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MockMetric:
    """Mock metric when prometheus is not available."""
    def labels(self, **kwargs):
        return self
    
    def inc(self, *args, **kwargs):
        pass
    
    def observe(self, *args, **kwargs):
        pass
    
    def set(self, *args, **kwargs):
        pass


def _get_metric(real_metric, mock_metric):
    """Get real metric if available, otherwise mock."""
    if PROMETHEUS_AVAILABLE:
        return real_metric
    return mock_metric


TENANT_REQUESTS = _get_metric(
    Counter(
        'tenant_requests_total',
        'Total requests per tenant',
        ['tenant_id', 'endpoint', 'status']
    ),
    MockMetric()
)

TENANT_LATENCY = _get_metric(
    Histogram(
        'tenant_request_latency_seconds',
        'Request latency per tenant',
        ['tenant_id', 'endpoint']
    ),
    MockMetric()
)

TENANT_TOKENS = _get_metric(
    Counter(
        'tenant_tokens_total',
        'Tokens used per tenant',
        ['tenant_id', 'model']
    ),
    MockMetric()
)

TENANT_ACTIVE_SESSIONS = _get_metric(
    Gauge(
        'tenant_active_sessions',
        'Active sessions per tenant',
        ['tenant_id']
    ),
    MockMetric()
)

TENANT_COST = _get_metric(
    Gauge(
        'tenant_monthly_cost_usd',
        'Monthly accumulated cost per tenant',
        ['tenant_id']
    ),
    MockMetric()
)

TENANT_USAGE_PERCENT = _get_metric(
    Gauge(
        'tenant_usage_percent',
        'Percentage of plan limit used',
        ['tenant_id', 'resource_type']
    ),
    MockMetric()
)

REQUEST_LATENCY = _get_metric(
    Histogram('request_latency_seconds', 'Overall request latency'),
    MockMetric()
)

ACTIVE_USERS = _get_metric(
    Gauge('active_users', 'Active users in last hour'),
    MockMetric()
)

ERROR_RATE = _get_metric(
    Counter('errors_total', 'Total errors', ['type', 'endpoint']),
    MockMetric()
)


class MetricsService:
    """Service for recording tenant metrics."""

    def __init__(self):
        self._tenant_sessions: dict = {}

    def record_request(self, tenant_id: str, endpoint: str, status: int):
        """Record a request for a tenant."""
        TENANT_REQUESTS.labels(
            tenant_id=tenant_id,
            endpoint=endpoint,
            status=str(status)
        ).inc()

    def record_latency(self, tenant_id: str, endpoint: str, latency_seconds: float):
        """Record request latency for a tenant."""
        TENANT_LATENCY.labels(
            tenant_id=tenant_id,
            endpoint=endpoint
        ).observe(latency_seconds)
        
        REQUEST_LATENCY.observe(latency_seconds)

    def record_tokens(self, tenant_id: str, model: str, tokens: int):
        """Record token usage for a tenant."""
        TENANT_TOKENS.labels(
            tenant_id=tenant_id,
            model=model
        ).inc(tokens)

    def update_active_sessions(self, tenant_id: str, count: int):
        """Update active session count for a tenant."""
        TENANT_ACTIVE_SESSIONS.labels(tenant_id=tenant_id).set(count)

    def update_monthly_cost(self, tenant_id: str, cost_usd: float):
        """Update monthly cost for a tenant."""
        TENANT_COST.labels(tenant_id=tenant_id).set(cost_usd)

    def update_usage_percent(self, tenant_id: str, resource_type: str, percent: float):
        """Update usage percentage for a tenant."""
        TENANT_USAGE_PERCENT.labels(
            tenant_id=tenant_id,
            resource_type=resource_type
        ).set(percent)

    def record_error(self, error_type: str, endpoint: str):
        """Record an error."""
        ERROR_RATE.labels(type=error_type, endpoint=endpoint).inc()

    def increment_active_users(self):
        """Increment active users gauge."""
        ACTIVE_USERS.inc()

    def decrement_active_users(self):
        """Decrement active users gauge."""
        ACTIVE_USERS.dec()


_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service

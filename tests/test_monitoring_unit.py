"""Tests for monitoring module."""
import pytest
from app.monitoring.metrics import MetricsService, get_metrics_service
from app.monitoring.health import HealthCheck, ComponentHealth, ReadinessCheck, LivenessCheck


class TestMetricsService:
    @pytest.fixture
    def metrics_service(self):
        return MetricsService()

    def test_record_request(self, metrics_service):
        metrics_service.record_request("tenant_1", "/api/chat", 200)
        metrics_service.record_request("tenant_1", "/api/chat", 500)
        metrics_service.record_request("tenant_2", "/api/history", 200)
        
        # Should not raise exceptions
        assert True

    def test_record_latency(self, metrics_service):
        metrics_service.record_latency("tenant_1", "/api/chat", 0.125)
        metrics_service.record_latency("tenant_1", "/api/chat", 0.250)
        
        assert True

    def test_record_tokens(self, metrics_service):
        metrics_service.record_tokens("tenant_1", "gpt-4", 100)
        metrics_service.record_tokens("tenant_1", "gpt-3.5", 50)
        
        assert True

    def test_update_active_sessions(self, metrics_service):
        metrics_service.update_active_sessions("tenant_1", 5)
        metrics_service.update_active_sessions("tenant_1", 10)
        
        assert True

    def test_update_monthly_cost(self, metrics_service):
        metrics_service.update_monthly_cost("tenant_1", 99.0)
        metrics_service.update_monthly_cost("tenant_2", 29.0)
        
        assert True

    def test_update_usage_percent(self, metrics_service):
        metrics_service.update_usage_percent("tenant_1", "requests", 75.5)
        metrics_service.update_usage_percent("tenant_1", "tokens", 50.0)
        
        assert True

    def test_record_error(self, metrics_service):
        metrics_service.record_error("rate_limit", "/api/chat")
        metrics_service.record_error("internal_error", "/api/history")
        
        assert True


class TestComponentHealth:
    def test_component_health_creation(self):
        health = ComponentHealth(
            name="database",
            status="healthy",
            latency_ms=5.2,
            details={"connections": 10}
        )
        
        assert health.name == "database"
        assert health.status == "healthy"
        assert health.latency_ms == 5.2

    def test_component_health_unhealthy(self):
        health = ComponentHealth(
            name="redis",
            status="unhealthy",
            latency_ms=0,
            details={"error": "Connection refused"}
        )
        
        assert health.status == "unhealthy"


class TestHealthCheck:
    @pytest.fixture
    def health_check(self):
        return HealthCheck()

    def test_check_all_returns_dict(self, health_check):
        import asyncio
        results = asyncio.run(health_check.check_all())
        
        assert isinstance(results, dict)
        assert "database" in results
        assert "redis" in results
        assert "overall" in results

    def test_check_database_healthy(self, health_check):
        import asyncio
        result = asyncio.run(health_check._check_database())
        
        assert result.name == "database"
        assert result.status in ["healthy", "degraded"]

    def test_check_redis_healthy(self, health_check):
        import asyncio
        result = asyncio.run(health_check._check_redis())
        
        assert result.name == "redis"
        assert result.status in ["healthy", "degraded"]

    def test_overall_healthy(self, health_check):
        import asyncio
        results = asyncio.run(health_check.check_all())
        
        assert results["overall"].name == "overall"


class TestReadinessCheck:
    def test_is_ready(self):
        import asyncio
        ready = asyncio.run(ReadinessCheck.is_ready())
        assert ready is True


class TestLivenessCheck:
    def test_is_alive(self):
        import asyncio
        alive = asyncio.run(LivenessCheck.is_alive())
        assert alive is True


class TestMetricsServiceSingleton:
    def test_get_metrics_service_returns_singleton(self):
        service1 = get_metrics_service()
        service2 = get_metrics_service()
        
        assert service1 is service2

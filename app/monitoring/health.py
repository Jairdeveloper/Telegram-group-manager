"""Health checks for multi-tenant enterprise monitoring."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    name: str
    status: str
    latency_ms: float
    details: Dict[str, Any]


class HealthCheck:
    """Service for checking system health."""

    def __init__(
        self,
        db_session=None,
        redis_client=None,
        external_apis: Optional[Dict[str, str]] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.external_apis = external_apis or {}

    async def check_all(self) -> Dict[str, ComponentHealth]:
        """Check health of all components."""
        results = {}

        results["database"] = await self._check_database()
        results["redis"] = await self._check_redis()

        for name, url in self.external_apis.items():
            results[f"api_{name}"] = await self._check_api(name, url)

        overall = "healthy"
        if any(c.status == "unhealthy" for c in results.values()):
            overall = "unhealthy"
        elif any(c.status == "degraded" for c in results.values()):
            overall = "degraded"

        results["overall"] = ComponentHealth(
            name="overall",
            status=overall,
            latency_ms=0,
            details={"components": len(results) - 1}
        )

        return results

    async def _check_database(self) -> ComponentHealth:
        """Check database connectivity."""
        start = time.time()
        try:
            if self.db_session is not None:
                self.db_session.execute("SELECT 1")
                latency = (time.time() - start) * 1000
                return ComponentHealth("database", "healthy", latency, {})
            latency = (time.time() - start) * 1000
            return ComponentHealth("database", "degraded", latency, {"error": "No DB session provided"})
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Database health check failed: {e}")
            return ComponentHealth("database", "unhealthy", latency, {"error": str(e)})

    async def _check_redis(self) -> ComponentHealth:
        """Check Redis connectivity."""
        start = time.time()
        try:
            if self.redis_client is not None:
                self.redis_client.ping()
                latency = (time.time() - start) * 1000
                return ComponentHealth("redis", "healthy", latency, {})
            latency = (time.time() - start) * 1000
            return ComponentHealth("redis", "degraded", latency, {"error": "No Redis client provided"})
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth("redis", "unhealthy", latency, {"error": str(e)})

    async def _check_api(self, name: str, url: str) -> ComponentHealth:
        """Check external API connectivity."""
        start = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    latency = (time.time() - start) * 1000
                    if response.status < 400:
                        return ComponentHealth(
                            f"api_{name}",
                            "healthy",
                            latency,
                            {"status": response.status}
                        )
                    else:
                        return ComponentHealth(
                            f"api_{name}",
                            "degraded",
                            latency,
                            {"status": response.status}
                        )
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"API {name} health check failed: {e}")
            return ComponentHealth(
                f"api_{name}",
                "unhealthy",
                latency,
                {"error": str(e)}
            )


class ReadinessCheck:
    """Simple readiness check for Kubernetes."""

    @staticmethod
    async def is_ready() -> bool:
        """Check if service is ready to accept traffic."""
        return True


class LivenessCheck:
    """Simple liveness check for Kubernetes."""

    @staticmethod
    async def is_alive() -> bool:
        """Check if service is alive."""
        return True


_health_check: Optional[HealthCheck] = None


def get_health_check(
    db_session=None,
    redis_client=None,
    external_apis: Optional[Dict[str, str]] = None
) -> HealthCheck:
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck(db_session, redis_client, external_apis)
    return _health_check


def set_health_check(check: HealthCheck) -> None:
    global _health_check
    _health_check = check

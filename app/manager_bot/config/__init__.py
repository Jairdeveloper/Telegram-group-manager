"""Compatibility config package (aliases to _config)."""

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import (
    ConfigStorage,
    InMemoryConfigStorage,
    PostgresConfigStorage,
    RedisConfigStorage,
    get_config_storage,
    reset_config_storage,
)
from app.manager_bot._config.rate_limiter import RateLimiter, CacheMetrics, CachedConfigStorage

__all__ = [
    "GroupConfig",
    "ConfigStorage",
    "InMemoryConfigStorage",
    "PostgresConfigStorage",
    "RedisConfigStorage",
    "get_config_storage",
    "reset_config_storage",
    "RateLimiter",
    "CacheMetrics",
    "CachedConfigStorage",
]


"""Rate limiting for callback security."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from app.manager_bot.config.group_config import GroupConfig
    from app.manager_bot.config.storage import ConfigStorage


@dataclass
class RateLimitEntry:
    """Rate limit entry for a user."""
    count: int
    reset_time: float


class RateLimiter:
    """
    Rate limiter for callbacks to prevent abuse.
    
    Implements sliding window rate limiting.
    """

    def __init__(
        self,
        max_calls: int = 30,
        window_seconds: int = 60,
    ):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._limits: Dict[str, RateLimitEntry] = {}

    def is_allowed(self, user_id: int, action: str = "default") -> bool:
        """Check if action is allowed for user."""
        current_time = time.time()
        key = f"{user_id}:{action}"
        
        entry = self._limits.get(key)
        
        if entry is None or current_time > entry.reset_time:
            self._limits[key] = RateLimitEntry(
                count=1,
                reset_time=current_time + self.window_seconds
            )
            return True
        
        if entry.count >= self.max_calls:
            return False
        
        entry.count += 1
        return True

    def get_remaining(self, user_id: int, action: str = "default") -> int:
        """Get remaining calls for user."""
        key = f"{user_id}:{action}"
        entry = self._limits.get(key)
        
        if entry is None:
            return self.max_calls
        
        current_time = time.time()
        if current_time > entry.reset_time:
            return self.max_calls
        
        return max(0, self.max_calls - entry.count)

    def reset(self, user_id: int, action: Optional[str] = None) -> None:
        """Reset rate limit for user."""
        if action:
            key = f"{user_id}:{action}"
            self._limits.pop(key, None)
        else:
            keys_to_remove = [k for k in self._limits.keys() if k.startswith(f"{user_id}:")]
            for k in keys_to_remove:
                del self._limits[k]

    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            k for k, v in self._limits.items() 
            if current_time > v.reset_time
        ]
        for k in expired_keys:
            del self._limits[k]


@dataclass
class CacheMetrics:
    """Metrics for cache performance."""
    hits: int = 0
    misses: int = 0
    errors: int = 0
    
    @property
    def total(self) -> int:
        return self.hits + self.misses
    
    @property
    def hit_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.hits / self.total
    
    def to_dict(self) -> Dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "total": self.total,
            "hit_rate": f"{self.hit_rate:.2%}"
        }


class CachedConfigStorage:
    """
    Wrapper that adds caching to ConfigStorage.
    
    Provides:
    - In-memory L1 cache
    - Metrics tracking
    - Cache invalidation
    """
    
    def __init__(
        self, 
        storage: "ConfigStorage",
        l1_ttl: int = 300,
    ):
        self._storage = storage
        self._l1_cache: Dict[int, "GroupConfig"] = {}
        self._l1_ttl = l1_ttl
        self._metrics = CacheMetrics()
        self._cache_times: Dict[int, float] = {}
    
    async def get(self, chat_id: int) -> Optional["GroupConfig"]:
        """Get config with L1 cache."""
        current_time = time.time()
        
        if chat_id in self._l1_cache:
            cache_time = self._cache_times.get(chat_id, 0)
            if current_time - cache_time < self._l1_ttl:
                self._metrics.hits += 1
                return self._l1_cache[chat_id]
        
        self._metrics.misses += 1
        config = await self._storage.get(chat_id)
        
        if config:
            self._l1_cache[chat_id] = config
            self._cache_times[chat_id] = current_time
        
        return config
    
    async def set(self, config: "GroupConfig") -> None:
        """Set config and invalidate cache."""
        await self._storage.set(config)
        self._l1_cache[config.chat_id] = config
        self._cache_times[config.chat_id] = time.time()
    
    async def delete(self, chat_id: int) -> None:
        """Delete config and invalidate cache."""
        await self._storage.delete(chat_id)
        self._l1_cache.pop(chat_id, None)
        self._cache_times.pop(chat_id, None)
    
    async def list_groups(self) -> list[int]:
        """List groups."""
        return await self._storage.list_groups()
    
    def invalidate(self, chat_id: int) -> None:
        """Manually invalidate cache for chat."""
        self._l1_cache.pop(chat_id, None)
        self._cache_times.pop(chat_id, None)
    
    def get_metrics(self) -> Dict:
        """Get cache metrics."""
        return self._metrics.to_dict()
    
    def clear_cache(self) -> None:
        """Clear L1 cache."""
        self._l1_cache.clear()
        self._cache_times.clear()

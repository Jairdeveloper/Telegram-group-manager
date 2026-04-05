"""Rate limiting queue management."""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass

from app.config.redis import get_redis_connection


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    max_requests: int
    window_seconds: int


class RateLimitConfig:
    """Default rate limit configurations."""
    
    CALLBACK = RateLimitConfig(max_requests=10, window_seconds=60)
    MESSAGE = RateLimitConfig(max_requests=30, window_seconds=60)
    COMMAND = RateLimitConfig(max_requests=20, window_seconds=60)


class RateLimitQueueManager:
    """Manager for rate limiting using token bucket algorithm."""
    
    def __init__(self):
        self.redis = get_redis_connection()
    
    def _get_key(self, key_type: str, user_id: int, chat_id: int) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{key_type}:{chat_id}:{user_id}"
    
    def is_allowed(
        self,
        key_type: str,
        user_id: int,
        chat_id: int,
        config: RateLimitConfig,
    ) -> bool:
        """Check if request is allowed under rate limit."""
        key = self._get_key(key_type, user_id, chat_id)
        
        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, config.window_seconds, 1)
            return True
        
        current_count = int(current)
        if current_count >= config.max_requests:
            return False
        
        self.redis.incr(key)
        return True
    
    def get_remaining(
        self,
        key_type: str,
        user_id: int,
        chat_id: int,
        config: RateLimitConfig,
    ) -> int:
        """Get remaining requests in current window."""
        key = self._get_key(key_type, user_id, chat_id)
        current = self.redis.get(key)
        
        if current is None:
            return config.max_requests
        
        current_count = int(current)
        return max(0, config.max_requests - current_count)
    
    def reset(
        self,
        key_type: str,
        user_id: int,
        chat_id: int,
    ) -> bool:
        """Reset rate limit for user/chat."""
        key = self._get_key(key_type, user_id, chat_id)
        return bool(self.redis.delete(key))


_rate_limit_manager = None


def get_rate_limit_manager() -> RateLimitQueueManager:
    """Get or create RateLimitQueueManager singleton."""
    global _rate_limit_manager
    if _rate_limit_manager is None:
        _rate_limit_manager = RateLimitQueueManager()
    return _rate_limit_manager

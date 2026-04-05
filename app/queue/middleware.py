"""Middleware for automatic queue selection based on rate limiting."""

import time
import logging
from typing import Optional, Callable, Any, Dict
from functools import wraps
from dataclasses import dataclass
from enum import Enum

from app.queue.rate_limiter import RateLimitQueueManager, RateLimitConfig, get_rate_limit_manager


logger = logging.getLogger(__name__)


class QueuePriority(Enum):
    """Queue priority levels."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class QueueSelectionResult:
    """Result of queue selection."""
    queue: str
    allowed: bool
    remaining: int
    retry_after: Optional[int] = None
    priority: QueuePriority = QueuePriority.NORMAL


class RateLimitMiddleware:
    """Middleware for rate limiting and queue selection."""
    
    def __init__(self, manager: Optional[RateLimitQueueManager] = None):
        self.manager = manager or get_rate_limit_manager()
        self._backoff_config = {
            "initial_delay": 1,
            "max_delay": 60,
            "multiplier": 2,
        }
    
    def check_and_select_queue(
        self,
        key_type: str,
        user_id: int,
        chat_id: int,
    ) -> QueueSelectionResult:
        """Check rate limit and select appropriate queue."""
        config = self._get_config_for_type(key_type)
        
        is_allowed = self.manager.is_allowed(
            key_type=key_type,
            user_id=user_id,
            chat_id=chat_id,
            config=config,
        )
        
        remaining = self.manager.get_remaining(
            key_type=key_type,
            user_id=user_id,
            chat_id=chat_id,
            config=config,
        )
        
        if not is_allowed:
            return QueueSelectionResult(
                queue="retry",
                allowed=False,
                remaining=0,
                retry_after=config.window_seconds,
                priority=QueuePriority.LOW,
            )
        
        priority = self._determine_priority(remaining, config)
        queue = self._get_queue_for_priority(priority)
        
        return QueueSelectionResult(
            queue=queue,
            allowed=True,
            remaining=remaining,
            priority=priority,
        )
    
    def _get_config_for_type(self, key_type: str) -> RateLimitConfig:
        """Get rate limit config for operation type."""
        configs = {
            "callback": RateLimitConfig(max_requests=10, window_seconds=60),
            "message": RateLimitConfig(max_requests=30, window_seconds=60),
            "command": RateLimitConfig(max_requests=20, window_seconds=60),
            "analysis": RateLimitConfig(max_requests=5, window_seconds=60),
            "db": RateLimitConfig(max_requests=10, window_seconds=60),
        }
        return configs.get(key_type, RateLimitConfig(max_requests=20, window_seconds=60))
    
    def _determine_priority(
        self,
        remaining: int,
        config: RateLimitConfig,
    ) -> QueuePriority:
        """Determine queue priority based on remaining requests."""
        ratio = remaining / config.max_requests
        
        if ratio > 0.7:
            return QueuePriority.HIGH
        elif ratio > 0.3:
            return QueuePriority.NORMAL
        else:
            return QueuePriority.LOW
    
    def _get_queue_for_priority(self, priority: QueuePriority) -> str:
        """Get queue name for priority level."""
        mapping = {
            QueuePriority.HIGH: "high",
            QueuePriority.NORMAL: "default",
            QueuePriority.LOW: "low",
        }
        return mapping[priority]
    
    def calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        delay = self._backoff_config["initial_delay"]
        max_delay = self._backoff_config["max_delay"]
        multiplier = self._backoff_config["multiplier"]
        
        for _ in range(attempt):
            delay = min(delay * multiplier, max_delay)
        
        return delay
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status."""
        return {
            "status": "operational",
            "queues": ["high", "default", "low", "nlp", "heavy", "maintenance"],
            "rate_limiting": "enabled",
        }


def rate_limited(
    key_type: str,
    user_id_param: str = "user_id",
    chat_id_param: str = "chat_id",
):
    """Decorator for rate limiting function calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.webhook.infrastructure import get_current_update
            
            try:
                update = get_current_update()
                user_id = getattr(update.effective_user, "id", 0) if update else 0
                chat_id = getattr(update.effective_chat, "id", 0) if update else 0
            except:
                user_id = kwargs.get(user_id_param, 0)
                chat_id = kwargs.get(chat_id_param, 0)
            
            manager = get_rate_limit_manager()
            config = RateLimitConfig(max_requests=20, window_seconds=60)
            
            if not manager.is_allowed(key_type, user_id, chat_id, config):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                raise RateLimitExceededError(
                    f"Rate limit exceeded for {key_type}",
                    retry_after=config.window_seconds,
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimitExceededError(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


_rate_limit_middleware = None


def get_rate_limit_middleware() -> RateLimitMiddleware:
    """Get or create rate limit middleware singleton."""
    global _rate_limit_middleware
    if _rate_limit_middleware is None:
        _rate_limit_middleware = RateLimitMiddleware()
    return _rate_limit_middleware

"""Tests for queue rate limiting."""

import time
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any


class TestRateLimitQueueManager:
    """Tests for RateLimitQueueManager."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection."""
        with patch("app.queue.rate_limiter.get_redis_connection") as mock:
            mock_conn = MagicMock()
            mock_conn.get.return_value = None
            mock.return_value = mock_conn
            yield mock_conn

    def test_is_allowed_first_request(self, mock_redis):
        """Test first request is allowed."""
        from app.queue import RateLimitQueueManager, RateLimitConfig

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        result = manager.is_allowed("message", user_id=123, chat_id=456, config=config)

        assert result is True
        mock_redis.setex.assert_called_once()

    def test_is_allowed_under_limit(self, mock_redis):
        """Test request under limit is allowed."""
        mock_redis.get.return_value = "5"
        
        from app.queue import RateLimitQueueManager, RateLimitConfig

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        result = manager.is_allowed("message", user_id=123, chat_id=456, config=config)

        assert result is True
        mock_redis.incr.assert_called_once()

    def test_is_allowed_at_limit(self, mock_redis):
        """Test request at limit is denied."""
        mock_redis.get.return_value = "10"
        
        from app.queue import RateLimitQueueManager, RateLimitConfig

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        result = manager.is_allowed("message", user_id=123, chat_id=456, config=config)

        assert result is False

    def test_get_remaining(self, mock_redis):
        """Test getting remaining requests."""
        mock_redis.get.return_value = "5"
        
        from app.queue import RateLimitQueueManager, RateLimitConfig

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        remaining = manager.get_remaining("message", user_id=123, chat_id=456, config=config)

        assert remaining == 5

    def test_get_remaining_no_key(self, mock_redis):
        """Test getting remaining when no key exists."""
        mock_redis.get.return_value = None
        
        from app.queue import RateLimitQueueManager, RateLimitConfig

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        remaining = manager.get_remaining("message", user_id=123, chat_id=456, config=config)

        assert remaining == 10

    def test_reset(self, mock_redis):
        """Test resetting rate limit."""
        mock_redis.delete.return_value = 1
        
        from app.queue import RateLimitQueueManager

        manager = RateLimitQueueManager()
        manager.redis = mock_redis
        
        result = manager.reset("message", user_id=123, chat_id=456)

        assert result is True
        mock_redis.delete.assert_called_once()


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        with patch("app.queue.middleware.get_rate_limit_manager") as mock_manager:
            mock_mgr = MagicMock()
            mock_mgr.is_allowed.return_value = True
            mock_mgr.get_remaining.return_value = 5
            mock_manager.return_value = mock_mgr
            
            from app.queue import RateLimitMiddleware
            return RateLimitMiddleware(manager=mock_mgr)

    def test_check_and_select_queue_allowed(self, middleware):
        """Test queue selection when allowed."""
        result = middleware.check_and_select_queue(
            key_type="message",
            user_id=123,
            chat_id=456,
        )

        assert result.allowed is True
        assert result.queue in ["high", "default", "low"]

    def test_check_and_select_queue_not_allowed(self, middleware):
        """Test queue selection when not allowed."""
        middleware.manager.is_allowed.return_value = False
        
        result = middleware.check_and_select_queue(
            key_type="message",
            user_id=123,
            chat_id=456,
        )

        assert result.allowed is False
        assert result.queue == "retry"
        assert result.retry_after is not None

    def test_calculate_backoff(self, middleware):
        """Test exponential backoff calculation."""
        delay_1 = middleware.calculate_backoff(1)
        delay_2 = middleware.calculate_backoff(2)
        delay_3 = middleware.calculate_backoff(3)

        assert delay_1 < delay_2 < delay_3


class TestQueueMonitor:
    """Tests for QueueMonitor."""

    @pytest.fixture
    def monitor(self):
        """Create monitor instance."""
        with patch("app.queue.monitor.get_redis_connection") as mock_redis:
            mock_conn = MagicMock()
            mock_redis.return_value = mock_conn
            
            from app.queue import QueueMonitor
            return QueueMonitor()

    def test_get_queue_status(self, monitor):
        """Test getting queue status."""
        with patch("app.queue.monitor.get_celery_app") as mock_app:
            mock_inspect = MagicMock()
            mock_inspect.stats.return_value = {
                "worker1": {"celery": {"default": {"pending": 10, "active": 5}}}
            }
            
            mock_app.return_value.control.inspect.return_value = mock_inspect
            
            status = monitor.get_queue_status("default")
            
            assert status.name == "default"

    def test_get_congestion_alerts(self, monitor):
        """Test getting congestion alerts."""
        status = monitor.get_congestion_alerts()
        
        assert isinstance(status, list)


class TestRateLimitConfig:
    """Tests for RateLimitConfig."""

    def test_default_configs(self):
        """Test default rate limit configs."""
        from app.queue import RateLimitConfig

        assert RateLimitConfig.CALLBACK.max_requests == 10
        assert RateLimitConfig.CALLBACK.window_seconds == 60
        assert RateLimitConfig.MESSAGE.max_requests == 30
        assert RateLimitConfig.COMMAND.max_requests == 20

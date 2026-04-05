"""Integration tests for Redis connection."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from app.config.redis import (
    RedisConnectionManager,
    RedisConfig,
    get_redis_manager,
    get_redis_config,
)


class TestRedisConnectionManager:
    """Test RedisConnectionManager."""

    @pytest.fixture
    def manager(self):
        """Create a RedisConnectionManager instance."""
        with patch("app.config.redis.redis.Redis"):
            manager = RedisConnectionManager(
                host="localhost",
                port=6379,
                db=0,
                max_connections=10,
            )
            return manager

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.host == "localhost"
        assert manager.port == 6379
        assert manager.db == 0

    def test_url_without_password(self, manager):
        """Test URL generation without password."""
        assert manager.url == "redis://localhost:6379/0"

    def test_url_with_password(self):
        """Test URL generation with password."""
        with patch("app.config.redis.redis.Redis"):
            manager = RedisConnectionManager(
                host="localhost",
                port=6379,
                db=0,
                password="secret",
            )
            assert manager.url == "redis://:secret@localhost:6379/0"

    def test_get_connection(self, manager):
        """Test getting a connection."""
        mock_conn = Mock()
        with patch.object(manager, "initialize_pool") as mock_init:
            mock_init.return_value = Mock()
            with patch("app.config.redis.redis.Redis") as mock_redis:
                conn = manager.get_connection()
                assert conn is not None

    def test_singleton(self):
        """Test singleton pattern."""
        with patch("app.config.redis.redis.Redis"):
            instance1 = RedisConnectionManager.get_instance()
            instance2 = RedisConnectionManager.get_instance()
            assert instance1 is instance2

    def test_reset_instance(self):
        """Test resetting singleton."""
        with patch("app.config.redis.redis.Redis"):
            RedisConnectionManager.reset_instance()
            instance = RedisConnectionManager.get_instance()
            assert instance is not None

    def test_health_check_healthy(self, manager):
        """Test health check when healthy."""
        mock_conn = Mock()
        mock_conn.ping.return_value = True
        mock_conn.info.side_effect = [
            {"connected_clients": 5},
            {"used_memory_human": "1mb", "used_memory_peak_human": "2mb"},
        ]

        with patch.object(manager, "get_connection", return_value=mock_conn):
            health = manager.health_check()
            assert health["status"] == "healthy"
            assert health["ping"] is True

    def test_health_check_unhealthy(self, manager):
        """Test health check when unhealthy."""
        from redis.exceptions import RedisError

        with patch.object(manager, "get_connection") as mock_get:
            mock_get.side_effect = RedisError("Connection refused")

            health = manager.health_check()
            assert health["status"] == "unhealthy"
            assert "error" in health

    def test_close(self, manager):
        """Test closing connections."""
        with patch("app.config.redis.redis.Redis"):
            manager._pool = Mock()
            manager._connection = Mock()
            manager.close()
            assert manager._pool is None
            assert manager._connection is None


class TestRedisConfig:
    """Test RedisConfig for legacy compatibility."""

    def test_url_generation(self):
        """Test URL generation."""
        config = RedisConfig(host="testhost", port=6380, db=1)
        assert config.url == "redis://testhost:6380/1"

    def test_url_with_password(self):
        """Test URL with password."""
        config = RedisConfig(host="testhost", port=6380, db=1, password="pass")
        assert config.url == "redis://:pass@testhost:6380/1"

    def test_get_connection(self):
        """Test getting connection."""
        with patch("app.config.redis.redis.Redis") as mock_redis:
            config = RedisConfig()
            conn = config.get_connection()
            mock_redis.assert_called_once()


class TestRedisFunctions:
    """Test module-level functions."""

    def test_get_redis_config_singleton(self):
        """Test get_redis_config returns singleton."""
        with patch("app.config.redis.redis.Redis"):
            config1 = get_redis_config()
            config2 = get_redis_config()
            assert config1 is config2

    def test_get_redis_manager_singleton(self):
        """Test get_redis_manager returns singleton."""
        with patch("app.config.redis.redis.Redis"):
            RedisConnectionManager.reset_instance()
            manager1 = get_redis_manager()
            manager2 = get_redis_manager()
            assert manager1 is manager2

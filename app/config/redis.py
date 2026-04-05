"""Redis configuration for async processing."""

import os
import logging
import contextlib
from typing import Optional, Dict, Any

import redis
from redis import ConnectionPool, Redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError


logger = logging.getLogger(__name__)


class RedisConnectionManager:
    """Manages Redis connections with connection pooling."""

    _instance: Optional["RedisConnectionManager"] = None

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = None,
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        socket_keepalive: bool = True,
        health_check_interval: int = 30,
    ):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_keepalive = socket_keepalive
        self.health_check_interval = health_check_interval

        self._pool: Optional[ConnectionPool] = None
        self._connection: Optional[Redis] = None

    @property
    def url(self) -> str:
        """Get Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    def initialize_pool(self) -> ConnectionPool:
        """Initialize the connection pool."""
        if self._pool is None:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                socket_keepalive=self.socket_keepalive,
                decode_responses=True,
                health_check_interval=self.health_check_interval,
            )
            logger.info(f"Redis connection pool initialized: {self.host}:{self.port}/{self.db}")
        return self._pool

    def get_connection(self) -> Redis:
        """Get a Redis connection from the pool."""
        if self._pool is None:
            self.initialize_pool()
        return Redis(connection_pool=self._pool)

    @contextlib.contextmanager
    def connection(self):
        """Context manager for Redis connections."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            pass

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        try:
            conn = self.get_connection()
            start = conn.ping()
            info = conn.info("stats")
            memory = conn.info("memory")

            return {
                "status": "healthy" if start else "unhealthy",
                "ping": start,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": memory.get("used_memory_human", "N/A"),
                "used_memory_peak_human": memory.get("used_memory_peak_human", "N/A"),
            }
        except RedisError as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics."""
        try:
            conn = self.get_connection()
            info = conn.info()
            return {
                "version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory"),
                "used_memory_peak": info.get("used_memory_peak"),
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace": self._get_keyspace_info(conn),
            }
        except RedisError as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"error": str(e)}

    def _get_keyspace_info(self, conn: Redis) -> Dict[str, int]:
        """Get keyspace information."""
        try:
            info = conn.info("keyspace")
            keyspace = {}
            for key, value in info.items():
                if key.startswith("db"):
                    keyspace[key] = value
            return keyspace
        except RedisError:
            return {}

    def close(self):
        """Close all connections and the pool."""
        if self._connection:
            self._connection.close()
            self._connection = None
        if self._pool:
            self._pool.disconnect()
            self._pool = None
        logger.info("Redis connection pool closed")

    @classmethod
    def get_instance(cls) -> "RedisConnectionManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None


class RedisConfig:
    """Redis configuration manager (legacy compatibility)."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = None,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.decode_responses = decode_responses

    @property
    def url(self) -> str:
        """Get Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    def get_connection(self) -> redis.Redis:
        """Create Redis connection."""
        return redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses,
        )


_redis_config = None
_redis_manager = None


def get_redis_config() -> RedisConfig:
    """Get or create RedisConfig singleton."""
    global _redis_config
    if _redis_config is None:
        _redis_config = RedisConfig()
    return _redis_config


def get_redis_connection() -> redis.Redis:
    """Get Redis connection."""
    return get_redis_config().get_connection()


def get_redis_manager() -> RedisConnectionManager:
    """Get RedisConnectionManager singleton."""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisConnectionManager.get_instance()
    return _redis_manager

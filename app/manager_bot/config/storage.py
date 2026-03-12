"""Configuration storage implementations."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.manager_bot.config.group_config import GroupConfig

logger = logging.getLogger(__name__)


class ConfigStorage(ABC):
    """Abstract interface for group configuration storage."""

    @abstractmethod
    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        """Get configuration for a chat."""
        pass

    @abstractmethod
    async def set(self, config: GroupConfig) -> None:
        """Set configuration for a chat."""
        pass

    @abstractmethod
    async def delete(self, chat_id: int) -> None:
        """Delete configuration for a chat."""
        pass

    @abstractmethod
    async def list_groups(self) -> List[int]:
        """List all configured group chat IDs."""
        pass


class InMemoryConfigStorage(ConfigStorage):
    """In-memory implementation for development/testing."""

    def __init__(self):
        self._configs: Dict[int, GroupConfig] = {}

    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        return self._configs.get(chat_id)

    async def set(self, config: GroupConfig) -> None:
        self._configs[config.chat_id] = config

    async def delete(self, chat_id: int) -> None:
        self._configs.pop(chat_id, None)

    async def list_groups(self) -> List[int]:
        return list(self._configs.keys())


class PostgresConfigStorage(ConfigStorage):
    """PostgreSQL implementation using SQLAlchemy."""

    def __init__(self, database_url: str):
        self._database_url = database_url
        self._engine = None

    def _get_engine(self):
        """Lazy initialization of SQLAlchemy engine."""
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(
                self._database_url, 
                pool_pre_ping=True
            )
        return self._engine

    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        try:
            from sqlalchemy import text
            engine = self._get_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT config_data FROM group_configs WHERE chat_id = :chat_id"),
                    {"chat_id": chat_id}
                ).fetchone()
                if result:
                    data = json.loads(result[0])
                    return GroupConfig.from_dict(data)
        except Exception as e:
            logger.error(f"Error fetching config for {chat_id}: {e}")
        return None

    async def set(self, config: GroupConfig) -> None:
        try:
            from sqlalchemy import text
            engine = self._get_engine()
            data = json.dumps(config.to_dict())
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO group_configs (chat_id, config_data, updated_at)
                        VALUES (:chat_id, :data, NOW())
                        ON CONFLICT (chat_id) 
                        DO UPDATE SET config_data = :data, updated_at = NOW()
                    """),
                    {"chat_id": config.chat_id, "data": data}
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving config for {config.chat_id}: {e}")
            raise

    async def delete(self, chat_id: int) -> None:
        try:
            from sqlalchemy import text
            engine = self._get_engine()
            with engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM group_configs WHERE chat_id = :chat_id"),
                    {"chat_id": chat_id}
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error deleting config for {chat_id}: {e}")

    async def list_groups(self) -> List[int]:
        try:
            from sqlalchemy import text
            engine = self._get_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT chat_id FROM group_configs")
                ).fetchall()
                return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            return []


class RedisConfigStorage(ConfigStorage):
    """Redis implementation for caching."""

    def __init__(self, redis_url: str, ttl: int = 3600):
        self._redis_url = redis_url
        self._ttl = ttl
        self._redis = None

    def _get_redis(self):
        """Lazy initialization of Redis client."""
        if self._redis is None:
            import redis.asyncio as redis
            self._redis = redis.from_url(self._redis_url)
        return self._redis

    def _key(self, chat_id: int) -> str:
        return f"group_config:{chat_id}"

    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        try:
            redis = self._get_redis()
            data = await redis.get(self._key(chat_id))
            if data:
                parsed = json.loads(data)
                return GroupConfig.from_dict(parsed)
        except Exception as e:
            logger.error(f"Error fetching config from Redis for {chat_id}: {e}")
        return None

    async def set(self, config: GroupConfig) -> None:
        try:
            redis = self._get_redis()
            data = json.dumps(config.to_dict())
            await redis.set(self._key(config.chat_id), data, ex=self._ttl)
        except Exception as e:
            logger.error(f"Error saving config to Redis for {config.chat_id}: {e}")

    async def delete(self, chat_id: int) -> None:
        try:
            redis = self._get_redis()
            await redis.delete(self._key(chat_id))
        except Exception as e:
            logger.error(f"Error deleting config from Redis for {chat_id}: {e}")

    async def list_groups(self) -> List[int]:
        try:
            redis = self._get_redis()
            keys = []
            async for key in redis.scan_iter("group_config:*"):
                keys.append(key)
            return [int(key.decode().split(":")[1]) for key in keys]
        except Exception as e:
            logger.error(f"Error listing groups from Redis: {e}")
            return []


_config_storage: Optional[ConfigStorage] = None


def get_config_storage(
    storage_type: str = "memory",
    database_url: Optional[str] = None,
    redis_url: Optional[str] = None,
    redis_ttl: int = 3600
) -> ConfigStorage:
    """Factory function to get config storage instance."""
    global _config_storage

    if _config_storage is not None:
        return _config_storage

    if storage_type == "memory":
        _config_storage = InMemoryConfigStorage()
    elif storage_type == "postgres" and database_url:
        _config_storage = PostgresConfigStorage(database_url)
    elif storage_type == "redis" and redis_url:
        _config_storage = RedisConfigStorage(redis_url, redis_ttl)
    else:
        logger.warning(f"Unknown storage type '{storage_type}', using in-memory")
        _config_storage = InMemoryConfigStorage()

    return _config_storage


def reset_config_storage() -> None:
    """Reset the global config storage instance."""
    global _config_storage
    _config_storage = None

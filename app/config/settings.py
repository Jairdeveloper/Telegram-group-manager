"""Centralized settings for API, webhook and worker runtimes."""

from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """Settings used by the chatbot API/monolith runtime."""

    app_name: str = "ChatBot Evolution"
    app_version: str = "2.1"
    debug: bool = False
    database_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_bool(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() == "true"
        return bool(value)

    def is_postgres_enabled(self) -> bool:
        """Check if PostgreSQL is configured."""
        return self.database_url is not None and self.database_url.startswith("postgresql")

    def is_storage_disabled(self) -> bool:
        """Check if storage is disabled (JSON mode)."""
        return self.database_url is None or self.database_url == "no-db"


class WebhookSettings(BaseSettings):
    """Settings used by Telegram webhook runtime."""

    telegram_bot_token: Optional[str] = None
    webhook_token: Optional[str] = None
    chatbot_api_url: str = "http://127.0.0.1:8000/api/v1/chat"
    redis_url: Optional[str] = None
    process_async: bool = True
    dedup_ttl: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("process_async", mode="before")
    @classmethod
    def parse_process_async_bool(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes")
        return bool(value)

    def require_bot_token(self) -> str:
        """Return token or raise when webhook runtime requires it."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return self.telegram_bot_token

    def get_webhook_token(self) -> Optional[str]:
        """Return webhook token if configured, otherwise None."""
        return self.webhook_token


class WorkerSettings(BaseSettings):
    """Settings used by the RQ worker runtime."""

    redis_url: str = "redis://redis:6379/0"
    queue_name: str = "telegram_tasks"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def queue_names(self) -> list[str]:
        return [self.queue_name]


def load_api_settings() -> ApiSettings:
    return ApiSettings()


def load_webhook_settings() -> WebhookSettings:
    return WebhookSettings()


def load_worker_settings() -> WorkerSettings:
    return WorkerSettings()


class EnterpriseSettings(BaseSettings):
    """Settings used by EnterpriseRobot modules."""

    enterprise_enabled: bool = True
    enterprise_moderation_enabled: bool = True
    default_tenant_id: str = "default"
    enterprise_default_timezone: str = "UTC"
    enterprise_owner_ids: str = ""
    enterprise_sardegna_ids: str = ""
    enterprise_feature_fun: bool = True
    enterprise_feature_reactions: bool = True
    enterprise_feature_anilist: bool = True
    enterprise_feature_wallpaper: bool = True
    enterprise_feature_gettime: bool = True
    enterprise_anilist_url: str = ""
    enterprise_anilist_timeout: int = 5
    enterprise_spamwatch_url: str = ""
    enterprise_spamwatch_token: str = ""
    enterprise_spamwatch_timeout: int = 3
    enterprise_sibyl_url: str = ""
    enterprise_sibyl_token: str = ""
    enterprise_sibyl_timeout: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def owner_ids(self) -> list[int]:
        return _parse_id_list(self.enterprise_owner_ids)

    @property
    def sardegna_ids(self) -> list[int]:
        return _parse_id_list(self.enterprise_sardegna_ids)


def _parse_id_list(raw: str) -> list[int]:
    ids: list[int] = []
    for token in (raw or "").split(","):
        token = token.strip()
        if not token:
            continue
        if token.lstrip("-").isdigit():
            ids.append(int(token))
    return ids


def load_enterprise_settings() -> EnterpriseSettings:
    return EnterpriseSettings()

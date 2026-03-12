import uuid
from pathlib import Path

import pytest

from app.config.settings import (
    WebhookSettings,
    load_api_settings,
    load_webhook_settings,
    load_worker_settings,
)


def _make_local_tmpdir():
    base = Path(__file__).resolve().parent / "_tmp_settings"
    base.mkdir(exist_ok=True)
    temp_dir = base / str(uuid.uuid4())
    temp_dir.mkdir()
    return temp_dir


def test_webhook_settings_defaults(monkeypatch):
    monkeypatch.chdir(_make_local_tmpdir())
    monkeypatch.delenv("CHATBOT_API_URL", raising=False)
    monkeypatch.delenv("PROCESS_ASYNC", raising=False)
    monkeypatch.delenv("DEDUP_TTL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)

    settings = load_webhook_settings()

    assert settings.chatbot_api_url == "http://127.0.0.1:8000/api/v1/chat"
    assert settings.process_async is True
    assert settings.dedup_ttl == 86400
    assert settings.redis_url is None


def test_settings_parse_bool_and_int(monkeypatch):
    monkeypatch.setenv("PROCESS_ASYNC", "0")
    monkeypatch.setenv("DEDUP_TTL", "120")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_PORT", "9001")

    webhook_settings = load_webhook_settings()
    api_settings = load_api_settings()

    assert webhook_settings.process_async is False
    assert webhook_settings.dedup_ttl == 120
    assert api_settings.debug is True
    assert api_settings.api_port == 9001


def test_webhook_required_token_validation(monkeypatch):
    monkeypatch.chdir(_make_local_tmpdir())
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    settings = WebhookSettings(telegram_bot_token="")

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        settings.require_bot_token()


def test_worker_settings_defaults(monkeypatch):
    monkeypatch.chdir(_make_local_tmpdir())
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("QUEUE_NAME", raising=False)

    settings = load_worker_settings()

    assert settings.redis_url == "redis://redis:6379/0"
    assert settings.queue_name == "telegram_tasks"
    assert settings.queue_names == ["telegram_tasks"]

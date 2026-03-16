import uuid
from pathlib import Path

import pytest

from app.config import settings as cfg_settings


def _make_local_tmpdir():
    base = Path(__file__).resolve().parent / "_tmp_settings"
    base.mkdir(exist_ok=True)
    temp_dir = base / str(uuid.uuid4())
    temp_dir.mkdir()
    return temp_dir


def _clear_settings_cache():
    cfg_settings._webhook_settings = None


def test_webhook_settings_defaults(monkeypatch):
    _clear_settings_cache()
    monkeypatch.chdir(_make_local_tmpdir())
    monkeypatch.delenv("CHATBOT_API_URL", raising=False)
    monkeypatch.delenv("PROCESS_ASYNC", raising=False)
    monkeypatch.delenv("DEDUP_TTL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)

    test_settings = cfg_settings.load_webhook_settings()

    assert test_settings.chatbot_api_url == "http://127.0.0.1:8000/api/v1/chat"
    assert test_settings.process_async is True
    assert test_settings.dedup_ttl == 86400
    assert test_settings.redis_url is None


def test_settings_parse_bool_and_int(monkeypatch):
    _clear_settings_cache()
    monkeypatch.setenv("PROCESS_ASYNC", "0")
    monkeypatch.setenv("DEDUP_TTL", "120")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_PORT", "9001")

    webhook_settings = cfg_settings.load_webhook_settings()
    api_settings = cfg_settings.load_api_settings()

    assert webhook_settings.process_async is False
    assert webhook_settings.dedup_ttl == 120
    assert api_settings.debug is True
    assert api_settings.api_port == 9001


def test_webhook_required_token_validation(monkeypatch):
    _clear_settings_cache()
    monkeypatch.chdir(_make_local_tmpdir())
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    test_settings = cfg_settings.WebhookSettings(telegram_bot_token="")

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        test_settings.require_bot_token()


def test_worker_settings_defaults(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("QUEUE_NAME", raising=False)

    test_settings = cfg_settings.load_worker_settings()

    assert test_settings.redis_url == "redis://redis:6379/0"
    assert test_settings.queue_name == "telegram_tasks"
    assert test_settings.queue_names == ["telegram_tasks"]

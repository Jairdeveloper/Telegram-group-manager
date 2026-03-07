import os

import pytest
from fastapi.testclient import TestClient

os.environ["DEDUP_TTL"] = "86400"

import app.webhook.entrypoint as twp
from app.webhook.infrastructure import InMemoryDedupStore


def _sample_update(update_id: int = 1):
    return {
        "update_id": update_id,
        "message": {
            "chat": {"id": 12345, "type": "private"},
            "text": "hola",
        },
    }


@pytest.fixture(autouse=True)
def _force_inmemory_dedup(monkeypatch):
    monkeypatch.setattr(twp, "DEDUP_STORE", InMemoryDedupStore(memory_store=set()))


def test_webhook_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    client = TestClient(twp.app)
    response = client.post("/webhook/invalid-token", json=_sample_update())
    assert response.status_code == 403


def test_webhook_accepts_valid_token_and_processes(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)

    calls = {"count": 0}

    def fake_process(update):
        calls["count"] += 1
        assert update["message"]["chat"]["id"] == 12345

    monkeypatch.setattr(twp, "process_update_sync", fake_process)
    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=10))

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert calls["count"] == 1


def test_webhook_deduplicates_update_id(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)

    calls = {"count": 0}

    def fake_process(update):
        calls["count"] += 1

    monkeypatch.setattr(twp, "process_update_sync", fake_process)
    client = TestClient(twp.app)
    payload = _sample_update(update_id=77)

    first = client.post("/webhook/valid-token", json=payload)
    second = client.post("/webhook/valid-token", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["count"] == 1


def test_webhook_async_enqueue_failure_falls_back_to_sync(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", True)

    class _QueueRaises:
        def enqueue_process_update(self, *, update):
            raise RuntimeError("enqueue failed")

    monkeypatch.setattr(twp, "TASK_QUEUE", _QueueRaises())

    calls = {"count": 0}

    def fake_process(update):
        calls["count"] += 1

    monkeypatch.setattr(twp, "process_update_sync", fake_process)
    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=90))

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert calls["count"] == 1


class _ChatServiceRaises:
    def __call__(self, chat_id: int, text: str):
        raise TimeoutError("timeout")


class _ChatServiceReturnsReply:
    def __init__(self, reply: str):
        self.reply = reply

    def __call__(self, chat_id: int, text: str):
        return {"response": self.reply}


class _TelegramRecorder:
    def __init__(self, should_raise: bool = False):
        self.calls = []
        self.should_raise = should_raise

    def send_message(self, *, chat_id: int, text: str):
        self.calls.append({"chat_id": chat_id, "text": text})
        if self.should_raise:
            raise RuntimeError("send failed")
        return {"status_code": 200, "text": "ok"}


def test_webhook_returns_500_when_bot_token_missing(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", None)
    client = TestClient(twp.app)

    response = client.post("/webhook/any-token", json=_sample_update(update_id=80))

    assert response.status_code == 500
    assert response.json()["detail"] == "BOT_TOKEN not configured"


def test_webhook_chat_service_exception_returns_ok_and_internal_error_reply(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)
    monkeypatch.setattr(twp, "handle_chat_message", _ChatServiceRaises())
    telegram = _TelegramRecorder()
    monkeypatch.setattr(twp, "TELEGRAM_CLIENT", telegram)
    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=81))

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert telegram.calls[0]["text"] == "(internal error)"


def test_webhook_chat_message_uses_shared_service_reply(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)
    monkeypatch.setattr(twp, "handle_chat_message", _ChatServiceReturnsReply("service:ok"))
    telegram = _TelegramRecorder()
    monkeypatch.setattr(twp, "TELEGRAM_CLIENT", telegram)
    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=82))

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert telegram.calls[0]["text"] == "service:ok"


def test_webhook_telegram_send_failure_still_returns_ok(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)
    monkeypatch.setattr(twp, "handle_chat_message", _ChatServiceReturnsReply("service:ok"))
    monkeypatch.setattr(twp, "TELEGRAM_CLIENT", _TelegramRecorder(should_raise=True))
    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=83))

    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def _fake_ops_handler(chat_id: int, command: str, args=(), **_kwargs):
    return {
        "status": "ok",
        "command": command,
        "response_text": f"ops:{command}",
    }


def test_webhook_processes_ops_commands_via_shared_service(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)
    monkeypatch.setattr(twp, "handle_ops_command", _fake_ops_handler)
    telegram = _TelegramRecorder()
    monkeypatch.setattr(twp, "TELEGRAM_CLIENT", telegram)
    client = TestClient(twp.app)
    payload = {
        "update_id": 84,
        "message": {"chat": {"id": 12345, "type": "private"}, "text": "/logs"},
    }

    response = client.post("/webhook/valid-token", json=payload)

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert telegram.calls[0]["text"] == "ops:/logs"

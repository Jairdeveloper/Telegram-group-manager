import asyncio
from types import SimpleNamespace

import app.ops.checks as checks
import app.telegram_ops.entrypoint as entrypoint


class _DummyAckMessage:
    def __init__(self):
        self.edit_calls = []

    async def edit_text(self, text, **kwargs):
        self.edit_calls.append({"text": text, "kwargs": kwargs})


class _DummyMessage:
    def __init__(self):
        self.reply_calls = []
        self.ack = _DummyAckMessage()

    async def reply_text(self, text, **kwargs):
        self.reply_calls.append({"text": text, "kwargs": kwargs})
        return self.ack


class _DummyUpdate:
    def __init__(self, chat_id=123):
        self.effective_chat = SimpleNamespace(id=chat_id)
        self.message = _DummyMessage()


class _DummyResponse:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text

    def json(self):
        return {"ok": True}


class _FakeAsyncClient:
    calls = []

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.calls.append({"url": url, "json": json})
        return _DummyResponse()


def test_format_e2e_response_is_plain_text():
    result = entrypoint.format_e2e_response(
        {
            "run_id": "abc12345",
            "timestamp": "2026-03-06T12:00:00Z",
            "checks": {
                "api_health": {"status": "OK"},
                "api_chat": {"status": "FAIL", "error": "bad_[markdown](chars)"},
            },
            "overall": "FAIL",
        }
    )

    assert "E2E Check (run_id: abc12345)" in result
    assert "[OK] api_health: OK" in result
    assert "[FAIL] api_chat: FAIL" in result
    assert "bad_[markdown](chars)" in result


def test_e2e_command_returns_result_without_markdown(monkeypatch):
    events = []

    async def fake_rate_limit(_chat_id):
        return True

    async def fake_run():
        return {
            "timestamp": "2026-03-06T12:00:00Z",
            "checks": {"api_health": {"status": "OK"}},
            "overall": "OK",
        }

    monkeypatch.setattr(entrypoint, "check_rate_limit", fake_rate_limit)
    monkeypatch.setattr(entrypoint, "run_e2e_check", fake_run)
    monkeypatch.setattr(entrypoint, "record_event", lambda **kwargs: events.append(kwargs))

    update = _DummyUpdate()
    context = SimpleNamespace(args=[])

    asyncio.run(entrypoint.e2e_command(update, context))

    assert update.message.reply_calls[0]["text"].startswith("E2E check iniciado...")
    assert update.message.reply_calls[0]["kwargs"] == {}
    assert update.message.ack.edit_calls[0]["kwargs"] == {}
    assert "[OK] api_health: OK" in update.message.ack.edit_calls[0]["text"]
    assert [event["event"] for event in events] == ["ops.e2e.requested", "ops.e2e.completed"]


def test_e2e_command_handles_internal_exception(monkeypatch):
    events = []

    async def fake_rate_limit(_chat_id):
        return True

    async def fake_run():
        raise RuntimeError("boom_[x]")

    monkeypatch.setattr(entrypoint, "check_rate_limit", fake_rate_limit)
    monkeypatch.setattr(entrypoint, "run_e2e_check", fake_run)
    monkeypatch.setattr(entrypoint, "record_event", lambda **kwargs: events.append(kwargs))

    update = _DummyUpdate()
    context = SimpleNamespace(args=[])

    asyncio.run(entrypoint.e2e_command(update, context))

    text = update.message.ack.edit_calls[0]["text"]
    assert "E2E check failed" in text
    assert "boom_[x]" in text
    assert [event["event"] for event in events] == ["ops.e2e.requested", "ops.e2e.failed"]


def test_check_webhook_local_uses_unique_update_id(monkeypatch):
    _FakeAsyncClient.calls = []
    monkeypatch.setattr(checks.httpx, "AsyncClient", _FakeAsyncClient)

    first = asyncio.run(checks.check_webhook_local())
    second = asyncio.run(checks.check_webhook_local())

    assert first["status"] == "OK"
    assert second["status"] == "OK"
    assert len(_FakeAsyncClient.calls) == 2
    assert _FakeAsyncClient.calls[0]["json"]["update_id"] != _FakeAsyncClient.calls[1]["json"]["update_id"]

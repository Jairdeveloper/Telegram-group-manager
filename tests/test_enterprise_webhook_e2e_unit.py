import asyncio

from app.webhook.handlers import process_update_impl


class _DummyLogger:
    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None

    def exception(self, *_args, **_kwargs):
        return None


class _FakeTelegramClientRecorder:
    def __init__(self):
        self.calls = []

    def send_message(self, *, chat_id: int, text: str):
        self.calls.append({"chat_id": chat_id, "text": text})
        return {"status_code": 200, "text": "ok"}


class _FakeChatServiceStatic:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls = []

    def __call__(self, chat_id: int, text: str):
        self.calls.append({"chat_id": chat_id, "text": text})
        return {"response": self.reply}


def test_enterprise_fun_command_responds(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_FUN", "1")
    telegram = _FakeTelegramClientRecorder()

    asyncio.run(
        process_update_impl(
            {"message": {"chat": {"id": 5001}, "text": "/fun", "from": {"id": 10}}},
            telegram_client=telegram,
            logger=_DummyLogger(),
        )
    )

    assert telegram.calls
    assert "Modulo fun deshabilitado" not in telegram.calls[0]["text"]


def test_enterprise_anilist_disabled(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_ANILIST", "0")
    telegram = _FakeTelegramClientRecorder()

    asyncio.run(
        process_update_impl(
            {"message": {"chat": {"id": 5002}, "text": "/anilist eva", "from": {"id": 11}}},
            telegram_client=telegram,
            logger=_DummyLogger(),
        )
    )

    assert telegram.calls
    assert telegram.calls[0]["text"] == "Modulo anilist deshabilitado."


def test_enterprise_blacklist_blocks_chat_message(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_MODERATION_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "42")
    telegram = _FakeTelegramClientRecorder()
    chat_service = _FakeChatServiceStatic("chat-ok")

    asyncio.run(
        process_update_impl(
            {"message": {"chat": {"id": 6001}, "text": "/blacklist add spam", "from": {"id": 42}}},
            telegram_client=telegram,
            logger=_DummyLogger(),
            handle_chat_message_fn=chat_service,
        )
    )

    telegram.calls.clear()
    chat_service.calls.clear()

    asyncio.run(
        process_update_impl(
            {"message": {"chat": {"id": 6001}, "text": "spam detected", "from": {"id": 43}}},
            telegram_client=telegram,
            logger=_DummyLogger(),
            handle_chat_message_fn=chat_service,
        )
    )

    assert chat_service.calls == []
    assert telegram.calls
    assert "Mensaje bloqueado" in telegram.calls[0]["text"]

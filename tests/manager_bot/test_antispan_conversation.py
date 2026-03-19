import asyncio

from app.manager_bot._menu_service import get_conversation_state
from app.manager_bot._config.storage import get_config_storage, reset_config_storage
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


def test_antispan_duration_updates_config():
    reset_config_storage()
    storage = get_config_storage("memory")
    conversation = get_conversation_state()
    user_id = 99
    chat_id = 9100

    conversation.set_state(user_id, chat_id, "waiting_antispan_telegram_mute_duration")

    telegram = _FakeTelegramClientRecorder()
    update = {"message": {"chat": {"id": chat_id}, "text": "45 minutes", "from": {"id": user_id}}}

    asyncio.run(
        process_update_impl(
            update,
            telegram_client=telegram,
            logger=_DummyLogger(),
        )
    )

    async def _fetch():
        return await storage.get(chat_id)

    config = asyncio.run(_fetch())
    assert config is not None
    assert config.antispan_telegram_mute_duration_sec == 2700
    assert config.antispan_telegram_action == "mute"
    assert conversation.get_state(user_id, chat_id) is None


def test_antispan_exceptions_add_updates_config():
    reset_config_storage()
    storage = get_config_storage("memory")
    conversation = get_conversation_state()
    user_id = 101
    chat_id = 9101

    conversation.set_state(user_id, chat_id, "waiting_antispan_telegram_exceptions_add")

    telegram = _FakeTelegramClientRecorder()
    update = {
        "message": {
            "chat": {"id": chat_id},
            "text": "@canal1\nhttps://t.me/joinchat/abc",
            "from": {"id": user_id},
        }
    }

    asyncio.run(
        process_update_impl(
            update,
            telegram_client=telegram,
            logger=_DummyLogger(),
        )
    )

    async def _fetch():
        return await storage.get(chat_id)

    config = asyncio.run(_fetch())
    assert config is not None
    assert "@canal1" in config.antispan_telegram_exceptions
    assert "https://t.me/joinchat/abc" in config.antispan_telegram_exceptions
    assert conversation.get_state(user_id, chat_id) is None

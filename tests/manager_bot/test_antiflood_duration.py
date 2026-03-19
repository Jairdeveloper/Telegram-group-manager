import asyncio

from app.manager_bot._menu_service import get_conversation_state
from app.manager_bot._config.storage import get_config_storage, reset_config_storage
from app.manager_bot._utils.duration_parser import parse_duration_to_seconds
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


def test_parse_duration_to_seconds():
    assert parse_duration_to_seconds("3 minutes 10 seconds") == 190
    assert parse_duration_to_seconds("2h") == 7200
    assert parse_duration_to_seconds("1 day 2 hours") == 93600
    assert parse_duration_to_seconds("invalid") is None


def test_antiflood_warn_duration_updates_config():
    reset_config_storage()
    storage = get_config_storage("memory")
    conversation = get_conversation_state()
    user_id = 42
    chat_id = 9001

    conversation.set_state(user_id, chat_id, "waiting_antiflood_warn_duration")

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
    assert config.antiflood_warn_duration_sec == 2700
    assert conversation.get_state(user_id, chat_id) is None

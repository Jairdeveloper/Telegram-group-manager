import asyncio
import logging

from app.manager_bot._menu_service import create_menu_engine
from app.webhook.handlers import process_update_impl


class FakeTelegramClient:
    def __init__(self):
        self.sent_messages = []
        self.answered_callbacks = []

    async def send_message(self, chat_id: int, text: str, reply_markup=None, **kwargs):
        self.sent_messages.append(
            {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        )
        return {"ok": True}

    async def answer_callback_query(self, callback_query_id: str, text=None, show_alert=False, **kwargs):
        self.answered_callbacks.append(
            {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert,
            }
        )
        return {"ok": True}


def test_config_command_sends_menu():
    create_menu_engine(storage_type="memory")

    update = {
        "update_id": 1,
        "message": {
            "message_id": 10,
            "chat": {"id": 123},
            "from": {"id": 999},
            "text": "/config",
        },
    }

    client = FakeTelegramClient()

    async def _run():
        await process_update_impl(
            update,
            telegram_client=client,
            logger=logging.getLogger("test"),
            handle_chat_message_fn=lambda chat_id, text: {"response": "ok"},
            handle_ops_command_fn=lambda *args, **kwargs: {"response_text": "ok"},
            is_admin_fn=lambda *_: True,
            rate_limit_check=lambda *_: True,
        )

    asyncio.run(_run())

    assert client.sent_messages, "Expected menu to be sent for /config"
    assert client.sent_messages[0]["reply_markup"] is not None


def test_welcome_customize_menu_registered():
    menu_engine, _ = create_menu_engine(storage_type="memory")
    assert "welcome_customize" in menu_engine.registry.list_menus()

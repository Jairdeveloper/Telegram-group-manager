import asyncio
import re

from app.telegram.dispatcher import extract_callback_data
from robot_ptb_compat.compat.handlers import CallbackPrefixAdapter, prefix_pattern


class DummyCallbackQuery:
    def __init__(self, data: str):
        self.data = data


class DummyUpdate:
    def __init__(self, data: str):
        self.callback_query = DummyCallbackQuery(data)


class DummyContext:
    pass


def test_prefix_pattern_matches():
    pattern = prefix_pattern("welcome:toggle")
    assert re.match(pattern, "welcome:toggle")
    assert re.match(pattern, "welcome:toggle:on")
    assert not re.match(pattern, "welcome:edit:text")


def test_callback_prefix_adapter_handles_prefix():
    calls = []

    async def cb(update, context):
        calls.append(update.callback_query.data)

    adapter = CallbackPrefixAdapter(prefix="welcome:toggle", callback=cb)

    async def _run():
        await adapter.handle(DummyUpdate("welcome:toggle:on"), DummyContext())
        await adapter.handle(DummyUpdate("welcome:edit:text"), DummyContext())

    asyncio.run(_run())

    assert calls == ["welcome:toggle:on"]


def test_extract_callback_data_message_id_fallback():
    update_with_message_id = {
        "callback_query": {
            "id": "cb-1",
            "data": "x",
            "from": {"id": 9},
            "message": {"message_id": 123, "chat": {"id": 1}},
        }
    }
    update_with_id = {
        "callback_query": {
            "id": "cb-2",
            "data": "x",
            "from": {"id": 9},
            "message": {"id": 456, "chat": {"id": 1}},
        }
    }

    assert extract_callback_data(update_with_message_id)["message_id"] == 123
    assert extract_callback_data(update_with_id)["message_id"] == 456

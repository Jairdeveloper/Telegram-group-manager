import asyncio

from fastapi import HTTPException

from app.webhook.handlers import dedup_update_impl, handle_webhook_impl, process_update_impl
from app.webhook.infrastructure import InMemoryDedupStore


class _DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class _DummyMetricLabels:
    def __init__(self, calls):
        self._calls = calls

    def inc(self):
        self._calls["inc"] += 1


class _DummyMetric:
    def __init__(self):
        self.calls = {"labels": [], "inc": 0}

    def labels(self, **kwargs):
        self.calls["labels"].append(kwargs)
        return _DummyMetricLabels(self.calls)


class _DummyLogger:
    def info(self, *_args, **_kwargs):
        return None

    def exception(self, *_args, **_kwargs):
        return None


class _DummyQueueError:
    def enqueue_process_update(self, *, update):
        raise RuntimeError("queue failed")


class _FakeChatApiClientRaises:
    def ask(self, *, message: str, session_id: str) -> str:
        raise TimeoutError("timeout")


class _FakeChatApiClientStatic:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls = 0

    def ask(self, *, message: str, session_id: str) -> str:
        self.calls += 1
        return self.reply


class _FakeTelegramClientRecorder:
    def __init__(self, should_raise: bool = False):
        self.calls = []
        self.should_raise = should_raise

    def send_message(self, *, chat_id: int, text: str):
        self.calls.append({"chat_id": chat_id, "text": text})
        if self.should_raise:
            raise RuntimeError("telegram send failed")
        return {"status_code": 200, "text": "ok"}


def test_dedup_update_impl_memory_store():
    seen = set()
    logger = _DummyLogger()
    dedup_store = InMemoryDedupStore(memory_store=seen)

    first = dedup_update_impl(100, dedup_store=dedup_store, dedup_ttl=60, logger=logger)
    second = dedup_update_impl(100, dedup_store=dedup_store, dedup_ttl=60, logger=logger)

    assert first is True
    assert second is False


def test_handle_webhook_impl_rejects_invalid_token():
    metric = _DummyMetric()

    try:
        asyncio.run(
            handle_webhook_impl(
                token="invalid",
                request=_DummyRequest({"update_id": 1}),
                bot_token="valid",
                dedup_update=lambda _update_id: True,
                process_async=False,
                task_queue=None,
                process_update_sync=lambda _update: None,
                requests_metric=metric,
                logger=_DummyLogger(),
            )
        )
        assert False, "Expected HTTPException for invalid token"
    except HTTPException as exc:
        assert exc.status_code == 403

    assert metric.calls["labels"] == [{"status": "forbidden"}]
    assert metric.calls["inc"] == 1


def test_handle_webhook_impl_async_queue_error_returns_ok_and_error_metric():
    metric = _DummyMetric()
    response = asyncio.run(
        handle_webhook_impl(
            token="valid",
            request=_DummyRequest({"update_id": 2, "message": {"chat": {"id": 1}, "text": "hola"}}),
            bot_token="valid",
            dedup_update=lambda _update_id: True,
            process_async=True,
            task_queue=_DummyQueueError(),
            process_update_sync=lambda _update: None,
            requests_metric=metric,
            logger=_DummyLogger(),
        )
    )

    assert response == {"ok": True}
    assert metric.calls["labels"] == [{"status": "error"}]
    assert metric.calls["inc"] == 1


def test_process_update_impl_chat_api_exception_sends_internal_error():
    telegram = _FakeTelegramClientRecorder()
    process_update_impl(
        {"message": {"chat": {"id": 123}, "text": "hola"}},
        chat_api_client=_FakeChatApiClientRaises(),
        telegram_client=telegram,
        logger=_DummyLogger(),
    )

    assert telegram.calls[0]["text"] == "(internal error)"


def test_process_update_impl_payload_without_message_does_not_fail():
    chat_api = _FakeChatApiClientStatic("unused")
    telegram = _FakeTelegramClientRecorder()

    process_update_impl(
        {"update_id": 99},
        chat_api_client=chat_api,
        telegram_client=telegram,
        logger=_DummyLogger(),
    )

    assert chat_api.calls == 0
    assert telegram.calls == []


def test_process_update_impl_unsupported_update_does_not_fail():
    chat_api = _FakeChatApiClientStatic("unused")
    telegram = _FakeTelegramClientRecorder()

    process_update_impl(
        {"update_id": 101, "message": {"chat": {"id": 123}}},
        chat_api_client=chat_api,
        telegram_client=telegram,
        logger=_DummyLogger(),
    )

    assert chat_api.calls == 0
    assert telegram.calls == []


def test_process_update_impl_ignores_telegram_commands():
    chat_api = _FakeChatApiClientStatic("unused")
    telegram = _FakeTelegramClientRecorder()

    process_update_impl(
        {"update_id": 100, "message": {"chat": {"id": 123}, "text": "/logs"}},
        chat_api_client=chat_api,
        telegram_client=telegram,
        logger=_DummyLogger(),
    )

    assert chat_api.calls == 0
    assert telegram.calls == []

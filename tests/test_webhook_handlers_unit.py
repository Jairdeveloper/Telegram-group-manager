import asyncio

from fastapi import HTTPException

from app.webhook.handlers import dedup_update_impl, handle_webhook_impl
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

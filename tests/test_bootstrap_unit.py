from types import SimpleNamespace

from app.webhook.infrastructure import InMemoryDedupStore, RedisDedupStore


class _DummyMetric:
    def __init__(self, *_args, **_kwargs):
        return None


class _DummyRedisFactory:
    @staticmethod
    def from_url(_url):
        return object()


class _DummyQueue:
    def __init__(self, _name, connection):
        self.connection = connection


class _DummyTaskQueue:
    def __init__(self, *, queue, process_update_callable):
        self.queue = queue
        self.process_update_callable = process_update_callable


def _settings(*, process_async: bool, redis_url: str | None):
    return SimpleNamespace(
        telegram_bot_token="token",
        webhook_token=None,
        chatbot_api_url="http://chatapi:8000/api/v1/chat",
        redis_url=redis_url,
        process_async=process_async,
        dedup_ttl=60,
    )


def test_build_webhook_runtime_sync_uses_inmemory_dedup(monkeypatch):
    import app.webhook.bootstrap as wb

    monkeypatch.setattr(wb, "load_dotenv", lambda: None)
    monkeypatch.setattr(wb, "load_webhook_settings", lambda: _settings(process_async=False, redis_url=None))
    monkeypatch.setattr(wb, "Counter", _DummyMetric)
    monkeypatch.setattr(wb, "Histogram", _DummyMetric)
    monkeypatch.setattr(wb, "Redis", None)
    monkeypatch.setattr(wb, "Queue", None)

    runtime = wb.build_webhook_runtime(process_update_callable=lambda _u: None)

    assert runtime.process_async is False
    assert runtime.task_queue is None
    assert isinstance(runtime.dedup_store, InMemoryDedupStore)


def test_build_webhook_runtime_async_with_redis_builds_queue(monkeypatch):
    import app.webhook.bootstrap as wb

    monkeypatch.setattr(wb, "load_dotenv", lambda: None)
    monkeypatch.setattr(
        wb,
        "load_webhook_settings",
        lambda: _settings(process_async=True, redis_url="redis://redis:6379/0"),
    )
    monkeypatch.setattr(wb, "Counter", _DummyMetric)
    monkeypatch.setattr(wb, "Histogram", _DummyMetric)
    monkeypatch.setattr(wb, "Redis", _DummyRedisFactory)
    monkeypatch.setattr(wb, "Queue", _DummyQueue)
    monkeypatch.setattr(wb, "RqTaskQueue", _DummyTaskQueue)

    runtime = wb.build_webhook_runtime(process_update_callable=lambda _u: None)

    assert runtime.process_async is True
    assert runtime.task_queue is not None
    assert isinstance(runtime.dedup_store, RedisDedupStore)


def test_build_api_runtime_uses_bootstrap_dependencies(monkeypatch):
    import app.api.bootstrap as ab

    class _DummyAgent:
        def __init__(self, pattern_responses, default_responses):
            self.pattern_responses = pattern_responses
            self.default_responses = default_responses

    class _DummyStorageAdapter:
        def __init__(self, repo):
            pass

    monkeypatch.setattr(
        ab,
        "load_api_settings",
        lambda: SimpleNamespace(app_name="A", app_version="1.0", is_postgres_enabled=lambda: False, is_storage_disabled=lambda: False),
    )
    monkeypatch.setattr(ab, "get_default_brain", lambda: ([["p"]], [["d"]]))
    monkeypatch.setattr(ab, "Agent", _DummyAgent)
    monkeypatch.setattr(ab, "StorageAdapter", _DummyStorageAdapter)

    runtime = ab.build_api_runtime()

    assert runtime.app_name == "A"
    assert runtime.app_version == "1.0"
    assert runtime.agent.pattern_responses == [["p"]]
    assert runtime.agent.default_responses == [["d"]]
    assert isinstance(runtime.storage, _DummyStorageAdapter)

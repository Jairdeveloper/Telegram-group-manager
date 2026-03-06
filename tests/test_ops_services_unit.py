import asyncio
from types import SimpleNamespace

import app.ops.services as services


class _DummyAgent:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def process(self, text):
        self.calls.append(text)
        return self.response


class _DummyStorage:
    def __init__(self):
        self.calls = []

    def save(self, session_id, message, response):
        self.calls.append(
            {"session_id": session_id, "message": message, "response": response}
        )


class _DummyEventStore:
    def __init__(self, events):
        self.events = list(events)
        self.tail_calls = []

    def tail(self, limit):
        self.tail_calls.append(limit)
        return list(self.events)


def test_handle_chat_message_returns_structured_response():
    response = SimpleNamespace(
        text="respuesta",
        confidence=0.87,
        source="brain",
        pattern_matched="saludo",
    )
    agent = _DummyAgent(response)
    storage = _DummyStorage()

    result = services.handle_chat_message(321, "hola", agent=agent, storage=storage)

    assert result == {
        "chat_id": 321,
        "session_id": "321",
        "message": "hola",
        "response": "respuesta",
        "confidence": 0.87,
        "source": "brain",
        "pattern_matched": "saludo",
    }
    assert agent.calls == ["hola"]
    assert storage.calls == [
        {"session_id": "321", "message": "hola", "response": "respuesta"}
    ]


def test_handle_ops_command_health_uses_reusable_checks():
    async def fake_api_health():
        return {"status": "OK"}

    async def fake_webhook_health():
        return {"status": "FAIL", "error": "down"}

    result = asyncio.run(
        services.handle_ops_command(
            123,
            "/health",
            is_admin_fn=lambda _chat_id: True,
            check_api_health_fn=fake_api_health,
            check_webhook_health_fn=fake_webhook_health,
        )
    )

    assert result["status"] == "ok"
    assert "API: OK" in result["response_text"]
    assert "Webhook: FAIL" in result["response_text"]
    assert "Error: down" in result["response_text"]


def test_handle_ops_command_logs_filters_and_records_event():
    store = _DummyEventStore(
        [
            {
                "ts_utc": "2026-03-06T12:00:00Z",
                "component": "webhook",
                "event": "webhook.received",
                "chat_id": 999,
                "update_id": 1,
            },
            {
                "ts_utc": "2026-03-06T12:00:01Z",
                "component": "ops",
                "event": "ops.logs_requested",
                "chat_id": 123,
                "update_id": 2,
            },
        ]
    )
    recorded = []

    result = asyncio.run(
        services.handle_ops_command(
            123,
            "/logs",
            ("5", "chat", "123"),
            is_admin_fn=lambda _chat_id: True,
            get_event_store_fn=lambda: store,
            record_event_fn=lambda **kwargs: recorded.append(kwargs),
        )
    )

    assert result["status"] == "ok"
    assert "Ultimos eventos (1/5) | chat=123" in result["response_text"]
    assert "ops ops.logs_requested" in result["response_text"]
    assert recorded == [
        {
            "component": "ops",
            "event": "ops.logs_requested",
            "chat_id": 123,
            "limit": 5,
            "filter_chat_id": 123,
            "filter_update_id": None,
        }
    ]
    assert store.tail_calls == [25]


def test_execute_e2e_command_records_success_in_plain_text():
    recorded = []

    async def fake_run():
        return {
            "timestamp": "2026-03-06T12:00:00Z",
            "checks": {"api_health": {"status": "OK"}},
            "overall": "OK",
        }

    result = asyncio.run(
        services.execute_e2e_command(
            123,
            run_id="abc12345",
            run_e2e_check_fn=fake_run,
            record_event_fn=lambda **kwargs: recorded.append(kwargs),
        )
    )

    assert result["status"] == "ok"
    assert result["run_id"] == "abc12345"
    assert "[OK] api_health: OK" in result["response_text"]
    assert [event["event"] for event in recorded] == [
        "ops.e2e.requested",
        "ops.e2e.completed",
    ]


def test_handle_ops_command_rejects_unauthorized_chat():
    result = asyncio.run(
        services.handle_ops_command(
            123,
            "/logs",
            is_admin_fn=lambda _chat_id: False,
        )
    )

    assert result == {
        "status": "unauthorized",
        "command": "/logs",
        "response_text": "No autorizado",
    }

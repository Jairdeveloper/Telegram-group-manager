import os

from fastapi.testclient import TestClient

os.environ["DEDUP_TTL"] = "86400"

import app.webhook.entrypoint as twp
from app.api.factory import create_api_app
from app.webhook import create_webhook_app


class _DummyResponse:
    def __init__(self, text: str):
        self.text = text
        self.confidence = 1.0
        self.source = "pattern"
        self.pattern_matched = True


class _DummyAgent:
    def process(self, message: str):
        return _DummyResponse(f"echo:{message}")


class _DummyStorage:
    def __init__(self):
        self.data = {}

    def save(self, session_id: str, message: str, response: str):
        self.data.setdefault(session_id, []).append(
            {"message": message, "response": response}
        )

    def get_history(self, session_id: str):
        return self.data.get(session_id, [])


def test_modular_api_factory_exposes_chat_route():
    app = create_api_app(
        app_name="Test API",
        app_version="1.0",
        app_description="test",
        agent=_DummyAgent(),
        storage=_DummyStorage(),
    )
    client = TestClient(app)
    response = client.post("/api/v1/chat", params={"message": "hola", "session_id": "s1"})
    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "echo:hola"
    assert body["session_id"] == "s1"


def test_webhook_wrapper_returns_operational_app(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", True)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)
    monkeypatch.setattr(twp, "process_update_sync", lambda update: None)
    if hasattr(twp.dedup_update, "_seen"):
        twp.dedup_update._seen.clear()

    client = TestClient(create_webhook_app())
    payload = {"update_id": 501, "message": {"chat": {"id": 1}, "text": "hi"}}
    response = client.post("/webhook/valid-token", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True


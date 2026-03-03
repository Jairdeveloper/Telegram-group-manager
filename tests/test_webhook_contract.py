from fastapi.testclient import TestClient

import telegram_webhook_prod as twp


def _sample_update(update_id: int = 1):
    return {
        "update_id": update_id,
        "message": {
            "chat": {"id": 12345, "type": "private"},
            "text": "hola",
        },
    }


def test_webhook_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    client = TestClient(twp.app)
    response = client.post("/webhook/invalid-token", json=_sample_update())
    assert response.status_code == 403


def test_webhook_accepts_valid_token_and_processes(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)

    calls = {"count": 0}

    def fake_process(update):
        calls["count"] += 1
        assert update["message"]["chat"]["id"] == 12345

    monkeypatch.setattr(twp, "process_update_sync", fake_process)
    if hasattr(twp.dedup_update, "_seen"):
        twp.dedup_update._seen.clear()

    client = TestClient(twp.app)
    response = client.post("/webhook/valid-token", json=_sample_update(update_id=10))

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert calls["count"] == 1


def test_webhook_deduplicates_update_id(monkeypatch):
    monkeypatch.setattr(twp, "BOT_TOKEN", "valid-token")
    monkeypatch.setattr(twp, "PROCESS_ASYNC", False)
    monkeypatch.setattr(twp, "TASK_QUEUE", None)

    calls = {"count": 0}

    def fake_process(update):
        calls["count"] += 1

    monkeypatch.setattr(twp, "process_update_sync", fake_process)
    if hasattr(twp.dedup_update, "_seen"):
        twp.dedup_update._seen.clear()

    client = TestClient(twp.app)
    payload = _sample_update(update_id=77)

    first = client.post("/webhook/valid-token", json=payload)
    second = client.post("/webhook/valid-token", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["count"] == 1

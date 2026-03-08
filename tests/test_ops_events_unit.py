from app.ops.events import InMemoryEventStore, mask_token, sanitize_event


def test_mask_token_short():
    assert mask_token("123") == "***"


def test_mask_token_long():
    assert mask_token("1234567890") == "1234...7890"


def test_sanitize_event_drops_token_keys_and_masks_values(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1111222233334444")
    event = {
        "ts_utc": "x",
        "component": "webhook",
        "event": "webhook.received",
        "level": "INFO",
        "telegram_bot_token": "1111222233334444",
        "detail": "token=1111222233334444",
        "nested": {"url": "https://x/webhook/1111222233334444"},
    }

    sanitized = sanitize_event(event)
    assert "telegram_bot_token" not in sanitized
    assert "1111222233334444" not in sanitized["detail"]
    assert "1111...4444" in sanitized["detail"]
    assert "1111222233334444" not in sanitized["nested"]["url"]


def test_inmemory_store_tail_returns_newest_first():
    store = InMemoryEventStore(max_events=3)
    store.publish({"event": "a"})
    store.publish({"event": "b"})
    store.publish({"event": "c"})

    assert [e["event"] for e in store.tail(10)] == ["c", "b", "a"]

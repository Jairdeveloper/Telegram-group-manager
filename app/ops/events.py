"""Operational event capture for debugging from Telegram (/logs).

Design goals:
- Best-effort: never break request handling if the store is unavailable.
- No secrets: remove token-like fields and mask known secrets in strings.
- Shared store when possible: Redis list when `REDIS_URL` is configured.
"""

from __future__ import annotations

import json
import os
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Iterable, List, Optional

try:
    from redis import Redis
except Exception:  # pragma: no cover
    Redis = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def mask_token(token: str) -> str:
    token = (token or "").strip()
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def _redact_key(key: str) -> bool:
    key_lower = (key or "").lower()
    return "token" in key_lower or "secret" in key_lower or "password" in key_lower


def _mask_known_secrets(text: str) -> str:
    if not text:
        return text
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or ""
    webhook_token = os.getenv("WEBHOOK_TOKEN") or ""
    if bot_token:
        text = text.replace(bot_token, mask_token(bot_token))
    if webhook_token:
        text = text.replace(webhook_token, mask_token(webhook_token))
    return text


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _mask_known_secrets(value)
    if isinstance(value, dict):
        sanitized: Dict[str, Any] = {}
        for k, v in value.items():
            if _redact_key(str(k)):
                continue
            sanitized[str(k)] = sanitize_value(v)
        return sanitized
    if isinstance(value, list):
        return [sanitize_value(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_value(v) for v in value]
    return value


def sanitize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    return sanitize_value(event)


class InMemoryEventStore:
    def __init__(self, *, max_events: int = 500):
        self._events: Deque[Dict[str, Any]] = deque(maxlen=max_events)
        self._lock = threading.Lock()

    def publish(self, event: Dict[str, Any]) -> None:
        with self._lock:
            self._events.appendleft(event)

    def tail(self, limit: int) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._events)[: max(0, limit)]


class RedisEventStore:
    def __init__(
        self,
        *,
        redis_client,
        key: str = "ops:events",
        max_events: int = 1000,
        ttl_seconds: int = 7 * 24 * 60 * 60,
    ):
        self._redis = redis_client
        self._key = key
        self._max_events = max_events
        self._ttl_seconds = ttl_seconds

    def publish(self, event: Dict[str, Any]) -> None:
        payload = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        pipe = self._redis.pipeline()
        pipe.lpush(self._key, payload)
        pipe.ltrim(self._key, 0, self._max_events - 1)
        pipe.expire(self._key, self._ttl_seconds)
        pipe.execute()

    def tail(self, limit: int) -> List[Dict[str, Any]]:
        raw: Iterable[bytes] = self._redis.lrange(self._key, 0, max(0, limit) - 1)
        out: List[Dict[str, Any]] = []
        for item in raw:
            try:
                out.append(json.loads(item.decode("utf-8")))
            except Exception:
                continue
        return out


class FileEventStore:
    def __init__(self, *, filepath: str = "logs/ops_events.jsonl", max_events: int = 500):
        self._filepath = filepath
        self._max_events = max_events
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    def publish(self, event: Dict[str, Any]) -> None:
        with self._lock:
            try:
                with open(self._filepath, "a") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
                self._trim()
            except Exception:
                pass

    def _trim(self) -> None:
        try:
            if not os.path.exists(self._filepath):
                return
            with open(self._filepath, "r") as f:
                lines = f.readlines()
            if len(lines) > self._max_events:
                with open(self._filepath, "w") as f:
                    f.writelines(lines[-self._max_events:])
        except Exception:
            pass

    def tail(self, limit: int) -> List[Dict[str, Any]]:
        with self._lock:
            out: List[Dict[str, Any]] = []
            try:
                if os.path.exists(self._filepath):
                    with open(self._filepath, "r") as f:
                        lines = f.readlines()
                    for line in reversed(lines):
                        try:
                            out.append(json.loads(line.strip()))
                        except Exception:
                            continue
                        if len(out) >= limit:
                            break
            except Exception:
                pass
            return out


_STORE = None
_STORE_LOCK = threading.Lock()


def get_event_store():
    global _STORE
    with _STORE_LOCK:
        if _STORE is not None:
            return _STORE

        max_events = int(os.getenv("OPS_EVENTS_MAX", "1000") or "1000")
        ttl_seconds = int(os.getenv("OPS_EVENTS_TTL_SECONDS", str(7 * 24 * 60 * 60)) or str(7 * 24 * 60 * 60))
        key = os.getenv("OPS_EVENTS_REDIS_KEY", "ops:events")
        use_file = os.getenv("OPS_USE_FILE", "true").lower() == "true"

        redis_url = os.getenv("REDIS_URL") or ""
        if redis_url and Redis is not None:
            try:
                redis_client = Redis.from_url(redis_url)
                _STORE = RedisEventStore(
                    redis_client=redis_client,
                    key=key,
                    max_events=max_events,
                    ttl_seconds=ttl_seconds,
                )
                return _STORE
            except Exception:
                if use_file:
                    _STORE = FileEventStore(max_events=max_events)
                    return _STORE
                _STORE = InMemoryEventStore(max_events=max_events)
                return _STORE

        if use_file:
            _STORE = FileEventStore(max_events=max_events)
            return _STORE

        _STORE = FileEventStore(max_events=max_events)
        return _STORE


def record_event(
    *,
    component: str,
    event: str,
    level: str = "INFO",
    **fields: Any,
) -> None:
    """Best-effort publish to the configured store."""
    payload: Dict[str, Any] = {
        "ts_utc": _utc_now_iso(),
        "component": component,
        "event": event,
        "level": level,
        **fields,
    }
    sanitized = sanitize_event(payload)
    try:
        store = get_event_store()
        store.publish(sanitized)
    except Exception:
        # Best-effort: never break callers.
        return


def get_recent_events(
    *,
    limit: int = 50,
    chat_id: Optional[int] = None,
    update_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return recent events (newest first) with optional filters."""
    limit = max(1, min(int(limit), 200))
    store = get_event_store()
    candidates = store.tail(min(1000, max(limit * 5, limit)))

    out: List[Dict[str, Any]] = []
    for ev in candidates:
        if chat_id is not None and ev.get("chat_id") != chat_id:
            continue
        if update_id is not None and ev.get("update_id") != update_id:
            continue
        out.append(ev)
        if len(out) >= limit:
            break
    return out

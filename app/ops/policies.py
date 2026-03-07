"""Shared OPS authorization and rate-limit policies."""

from __future__ import annotations

import os
from datetime import datetime, timezone

_last_run_times: dict[int, float] = {}


def _parse_admin_chat_ids() -> tuple[str, ...]:
    raw = os.getenv("ADMIN_CHAT_IDS", "")
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def get_rate_limit_seconds() -> int:
    raw = os.getenv("OPS_RATE_LIMIT_SECONDS", "30").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 30


def is_admin(chat_id: int) -> bool:
    """Return whether the chat_id is authorized for OPS commands."""
    admin_chat_ids = _parse_admin_chat_ids()
    if not admin_chat_ids:
        return True
    return str(chat_id) in admin_chat_ids


async def check_rate_limit(chat_id: int) -> bool:
    """Enforce a small per-chat cooldown for expensive OPS commands."""
    rate_limit_seconds = get_rate_limit_seconds()
    if rate_limit_seconds <= 0:
        return True

    now = datetime.now(timezone.utc).timestamp()
    last_run = _last_run_times.get(chat_id, 0.0)
    if now - last_run < rate_limit_seconds:
        return False

    _last_run_times[chat_id] = now
    return True

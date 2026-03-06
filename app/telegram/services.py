"""Low-level helpers for Telegram update extraction and parsing."""

from typing import Any, Dict, Optional, Tuple


OPS_COMMANDS = frozenset(("/health", "/logs", "/e2e", "/webhookinfo"))


def extract_message(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return Telegram message payload when present."""
    return update.get("message") or update.get("edited_message")


def extract_chat_payload(update: Dict[str, Any]) -> Optional[Tuple[int, str]]:
    """Return (chat_id, text) from a Telegram update when present."""
    message = extract_message(update)
    if not message:
        return None
    return message["chat"]["id"], message.get("text", "")


def split_command(text: str) -> Tuple[Optional[str], Tuple[str, ...]]:
    """Split Telegram command text into command and args."""
    normalized = (text or "").strip()
    if not normalized.startswith("/"):
        return None, ()

    parts = normalized.split()
    command = parts[0].split("@", 1)[0].lower()
    return command, tuple(parts[1:])

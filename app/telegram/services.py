"""Low-level helpers for Telegram update extraction and parsing."""

from typing import Any, Dict, Optional, Tuple


OPS_COMMANDS = frozenset(("/health", "/logs", "/e2e", "/webhookinfo", "/start"))


def extract_message(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return Telegram message payload when present."""
    return update.get("message") or update.get("edited_message")


def extract_chat_payload(update: Dict[str, Any]) -> Optional[Tuple[int, str]]:
    """Return (chat_id, text) from a Telegram update when present."""
    message = extract_message(update)
    if not message:
        return None
    text = message.get("text")
    if not text:
        text = message.get("caption", "")
    return message["chat"]["id"], text


def extract_sender_id(update: Dict[str, Any]) -> Optional[int]:
    """Return sender user id when present."""
    message = extract_message(update)
    if not message:
        return None
    sender = message.get("from")
    if sender and "id" in sender:
        return sender["id"]
    sender_chat = message.get("sender_chat")
    if sender_chat and "id" in sender_chat:
        return sender_chat["id"]
    return None


def split_command(text: str) -> Tuple[Optional[str], Tuple[str, ...]]:
    """Split Telegram command text into command and args."""
    normalized = (text or "").strip()
    if not normalized.startswith("/"):
        return None, ()

    parts = normalized.split()
    command = parts[0].split("@", 1)[0].lower()
    return command, tuple(parts[1:])

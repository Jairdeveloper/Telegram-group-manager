"""Telegram update classifier used by the webhook ingress."""

from typing import Any, Dict

from .models import DispatchResult
from .services import OPS_COMMANDS, extract_chat_payload, split_command


def dispatch_telegram_update(update: Dict[str, Any]) -> DispatchResult:
    """Classify Telegram updates into chat, ops command or unsupported."""
    update_id = update.get("update_id")
    payload = extract_chat_payload(update)

    if not payload:
        return DispatchResult(
            kind="unsupported",
            update_id=update_id,
            chat_id=None,
            reason="missing_message",
            raw_update=update,
        )

    chat_id, text = payload
    text = (text or "").strip()
    if not text:
        return DispatchResult(
            kind="unsupported",
            update_id=update_id,
            chat_id=chat_id,
            reason="missing_text",
            raw_update=update,
        )

    command, args = split_command(text)
    if command in OPS_COMMANDS:
        return DispatchResult(
            kind="ops_command",
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            command=command,
            args=args,
            raw_update=update,
        )

    if command is not None:
        return DispatchResult(
            kind="unsupported",
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            command=command,
            args=args,
            reason="unsupported_command",
            raw_update=update,
        )

    return DispatchResult(
        kind="chat_message",
        update_id=update_id,
        chat_id=chat_id,
        text=text,
        raw_update=update,
    )

"""Telegram update classifier used by the webhook ingress."""

from typing import Any, Dict, Optional

from app.enterprise.transport.dispatcher import is_enterprise_command
from app.agent.intent_router import get_default_intent_router, IntentKind

from .models import DispatchResult
from .services import OPS_COMMANDS, extract_chat_payload, extract_sender_id, split_command


def extract_callback_data(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract callback_query data from update if present."""
    callback_query = update.get("callback_query")
    if not callback_query:
        return None
    
    data = callback_query.get("data")
    if not data:
        return None
    
    message = callback_query.get("message", {})
    chat = message.get("chat", {})
    user = callback_query.get("from", {})

    return {
        "callback_id": callback_query.get("id"),
        "data": data,
        "chat_id": chat.get("id"),
        "message_id": message.get("message_id") or message.get("id"),
        "user_id": user.get("id"),
    }


def dispatch_telegram_update(update: Dict[str, Any]) -> DispatchResult:
    """Classify Telegram updates into callback_query, chat, ops command or unsupported."""
    update_id = update.get("update_id")
    
    # Check for callback_query first (inline keyboard interactions)
    callback_info = extract_callback_data(update)
    if callback_info:
        return DispatchResult(
            kind="callback_query",
            update_id=update_id,
            chat_id=callback_info["chat_id"],
            user_id=callback_info["user_id"],
            text=callback_info["data"],
            command=None,
            args=(),
            raw_update=update,
        )
    
    payload = extract_chat_payload(update)
    sender_id = extract_sender_id(update)

    if not payload:
        return DispatchResult(
            kind="unsupported",
            update_id=update_id,
            chat_id=None,
            user_id=sender_id,
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
            user_id=sender_id,
            reason="missing_text",
            raw_update=update,
        )

    command, args = split_command(text)
    if command in OPS_COMMANDS:
        return DispatchResult(
            kind="ops_command",
            update_id=update_id,
            chat_id=chat_id,
            user_id=sender_id,
            text=text,
            command=command,
            args=args,
            raw_update=update,
        )

    if command is not None and is_enterprise_command(command):
        return DispatchResult(
            kind="enterprise_command",
            update_id=update_id,
            chat_id=chat_id,
            user_id=sender_id,
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
            user_id=sender_id,
            text=text,
            command=command,
            args=args,
            reason="unsupported_command",
            raw_update=update,
        )

    intent_router = get_default_intent_router()
    decision = intent_router.route(text)
    if decision.kind == IntentKind.AGENT_TASK:
        return DispatchResult(
            kind="agent_task",
            update_id=update_id,
            chat_id=chat_id,
            user_id=sender_id,
            text=text,
            raw_update=update,
        )

    return DispatchResult(
        kind="chat_message",
        update_id=update_id,
        chat_id=chat_id,
        user_id=sender_id,
        text=text,
        raw_update=update,
    )

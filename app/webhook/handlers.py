"""Webhook domain logic decoupled from infrastructure libraries."""

import time
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import HTTPException, Request

from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient


def extract_chat_payload(update: Dict[str, Any]) -> Optional[Tuple[int, str]]:
    """Extract chat_id/text from Telegram update."""
    chat = update.get("message") or update.get("edited_message")
    if not chat:
        return None
    return chat["chat"]["id"], chat.get("text", "")


def dedup_update_impl(
    update_id: int,
    *,
    dedup_store: DedupStore,
    dedup_ttl: int,
    logger,
) -> bool:
    """Return True if update is new; False if duplicate."""
    try:
        return dedup_store.mark_if_new(update_id=update_id, ttl_seconds=dedup_ttl)
    except Exception:
        logger.exception("Dedup check failed")
        return True


def process_update_impl(
    update: Dict[str, Any],
    *,
    chat_api_client: ChatApiClient,
    telegram_client: TelegramClient,
    logger,
    process_time_metric=None,
) -> None:
    """Process update by querying Chat API and sending Telegram response."""
    start = time.time()
    payload = extract_chat_payload(update)
    if not payload:
        logger.info("No message to process")
        return

    chat_id, text = payload
    session_id = str(chat_id)

    try:
        reply = chat_api_client.ask(message=text, session_id=session_id)
    except Exception:
        logger.exception("Chat API call failed")
        reply = "(internal error)"

    try:
        telegram_client.send_message(chat_id=chat_id, text=reply)
    except Exception:
        logger.exception("Failed to send message to Telegram")

    if process_time_metric is not None:
        process_time_metric.observe(time.time() - start)


async def handle_webhook_impl(
    *,
    token: str,
    request: Request,
    bot_token: Optional[str],
    dedup_update: Callable[[int], bool],
    process_async: bool,
    task_queue: Optional[TaskQueue],
    process_update_sync: Callable[[Dict[str, Any]], None],
    requests_metric,
    logger,
) -> Dict[str, Any]:
    """Main webhook flow with token validation, dedup and enqueue/process."""
    if not bot_token:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")

    if token != bot_token:
        requests_metric.labels(status="forbidden").inc()
        raise HTTPException(status_code=403, detail="Invalid token")

    update = await request.json()
    update_id = update.get("update_id")

    if update_id is not None and not dedup_update(update_id):
        logger.info("Duplicate update ignored", extra={"update_id": update_id})
        requests_metric.labels(status="duplicate").inc()
        return {"ok": True}

    try:
        if process_async and task_queue is not None:
            job_id = task_queue.enqueue_process_update(update=update)
            logger.info("Enqueued update", extra={"job_id": job_id, "update_id": update_id})
        else:
            process_update_sync(update)

        requests_metric.labels(status="ok").inc()
        return {"ok": True}
    except Exception:
        logger.exception("Failed handling update")
        requests_metric.labels(status="error").inc()
        return {"ok": True}

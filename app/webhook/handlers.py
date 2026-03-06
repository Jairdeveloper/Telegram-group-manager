"""Webhook domain logic decoupled from infrastructure libraries."""

import time
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import HTTPException, Request

from app.telegram.dispatcher import dispatch_telegram_update
from app.telegram.services import extract_chat_payload
from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient
from app.ops.events import record_event


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
    dispatch = dispatch_telegram_update(update)
    update_id = dispatch.update_id
    chat_id = dispatch.chat_id
    log_ctx = {"update_id": update_id, "chat_id": chat_id}

    if dispatch.kind == "unsupported":
        logger.info("webhook.unsupported_update", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.unsupported_update",
            update_id=update_id,
            chat_id=chat_id,
            reason=dispatch.reason,
        )
        return

    text = dispatch.text
    session_id = str(chat_id)
    record_event(
        component="webhook",
        event="webhook.process_start",
        update_id=update_id,
        chat_id=chat_id,
        text_len=len(text or ""),
        dispatch_kind=dispatch.kind,
    )

    if dispatch.kind == "ops_command":
        logger.info("webhook.command_ignored", extra={**log_ctx, "command": dispatch.command})
        record_event(
            component="webhook",
            event="webhook.command_ignored",
            update_id=update_id,
            chat_id=chat_id,
            command=dispatch.command,
        )
        return

    try:
        reply = chat_api_client.ask(message=text, session_id=session_id)
        record_event(
            component="webhook",
            event="webhook.chat_api.ok",
            update_id=update_id,
            chat_id=chat_id,
            reply_len=len(reply or ""),
        )
    except Exception:
        logger.exception("webhook.chat_api_error", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.chat_api.error",
            level="ERROR",
            update_id=update_id,
            chat_id=chat_id,
        )
        reply = "(internal error)"

    try:
        telegram_client.send_message(chat_id=chat_id, text=reply)
        record_event(
            component="webhook",
            event="webhook.telegram_send.ok",
            update_id=update_id,
            chat_id=chat_id,
        )
    except Exception:
        logger.exception("webhook.telegram_send_error", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.telegram_send.error",
            level="ERROR",
            update_id=update_id,
            chat_id=chat_id,
        )

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
        record_event(component="webhook", event="webhook.forbidden", level="WARN")
        raise HTTPException(status_code=403, detail="Invalid token")

    update = await request.json()
    update_id = update.get("update_id")
    payload = extract_chat_payload(update)
    chat_id = payload[0] if payload else None
    log_ctx = {"update_id": update_id, "chat_id": chat_id}
    record_event(
        component="webhook",
        event="webhook.received",
        update_id=update_id,
        chat_id=chat_id,
        process_async=process_async,
    )

    if update_id is not None and not dedup_update(update_id):
        logger.info("webhook.duplicate_update", extra=log_ctx)
        record_event(component="webhook", event="webhook.dedup.duplicate", update_id=update_id, chat_id=chat_id)
        requests_metric.labels(status="duplicate").inc()
        return {"ok": True}

    try:
        if process_async and task_queue is not None:
            try:
                job_id = task_queue.enqueue_process_update(update=update)
                logger.info(
                    "webhook.enqueued_update", extra={**log_ctx, "job_id": job_id}
                )
                record_event(
                    component="webhook",
                    event="webhook.enqueue.ok",
                    update_id=update_id,
                    chat_id=chat_id,
                    job_id=job_id,
                )
            except Exception:
                # If the queue is misconfigured or Redis is down, fall back to
                # sync processing so Telegram still gets a timely response.
                logger.exception("webhook.enqueue_failed", extra=log_ctx)
                logger.warning("webhook.fallback_sync_after_enqueue_failure", extra=log_ctx)
                record_event(
                    component="webhook",
                    event="webhook.enqueue.error",
                    level="ERROR",
                    update_id=update_id,
                    chat_id=chat_id,
                )
                process_update_sync(update)
        elif process_async and task_queue is None:
            logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
            record_event(
                component="webhook",
                event="webhook.enqueue.unavailable",
                level="WARN",
                update_id=update_id,
                chat_id=chat_id,
            )
            process_update_sync(update)
        else:
            process_update_sync(update)

        requests_metric.labels(status="ok").inc()
        return {"ok": True}
    except Exception:
        logger.exception("webhook.handle_error", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.handle_error",
            level="ERROR",
            update_id=update_id,
            chat_id=chat_id,
        )
        requests_metric.labels(status="error").inc()
        return {"ok": True}

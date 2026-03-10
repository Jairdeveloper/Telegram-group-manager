"""Webhook domain logic decoupled from infrastructure libraries."""

import inspect
import time
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request

from app.enterprise import handle_enterprise_command, handle_enterprise_moderation
from app.ops.policies import check_rate_limit, is_admin
from app.ops.services import handle_chat_message, handle_ops_command
from app.ops.events import record_event
from app.telegram.dispatcher import dispatch_telegram_update
from app.telegram.services import extract_chat_payload
from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient


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


async def process_update_impl(
    update: Dict[str, Any],
    *,
    telegram_client: TelegramClient,
    logger,
    process_time_metric=None,
    chat_api_error_metric=None,
    telegram_send_error_metric=None,
    handle_chat_message_fn: Callable[..., Dict[str, Any]] = handle_chat_message,
    handle_ops_command_fn: Callable[..., Any] = handle_ops_command,
    handle_enterprise_command_fn: Callable[..., Any] = handle_enterprise_command,
    handle_enterprise_moderation_fn: Callable[..., Any] = handle_enterprise_moderation,
    is_admin_fn: Callable[[int], bool] = is_admin,
    rate_limit_check: Callable[[int], Any] = check_rate_limit,
) -> None:
    """Process update by dispatching chat and OPS commands via application services."""
    start = time.time()
    dispatch = dispatch_telegram_update(update)
    update_id = dispatch.update_id
    chat_id = dispatch.chat_id
    log_ctx = {"update_id": update_id, "chat_id": chat_id}

    if dispatch.kind == "unsupported":
        logger.info("webhook.unsupported_update", extra=log_ctx)
        record_event(
            component="telegram",
            event="telegram.dispatch.unsupported",
            update_id=update_id,
            chat_id=chat_id,
            reason=dispatch.reason,
        )
        record_event(
            component="webhook",
            event="webhook.unsupported_update",
            update_id=update_id,
            chat_id=chat_id,
            reason=dispatch.reason,
        )
        return

    record_event(
        component="telegram",
        event=f"telegram.dispatch.{dispatch.kind}",
        update_id=update_id,
        chat_id=chat_id,
    )

    record_event(
        component="webhook",
        event="webhook.process_start",
        update_id=update_id,
        chat_id=chat_id,
        text_len=len(dispatch.text or ""),
        dispatch_kind=dispatch.kind,
    )

    try:
        if dispatch.kind == "ops_command":
            result = await handle_ops_command_fn(
                chat_id,
                dispatch.command or "",
                dispatch.args,
                is_admin_fn=is_admin_fn,
                rate_limit_check=rate_limit_check,
            )
            reply = result.get("response_text", "(no response)")
            record_event(
                component="webhook",
                event="webhook.ops_service.ok",
                update_id=update_id,
                chat_id=chat_id,
                command=dispatch.command,
                ops_status=result.get("status"),
                reply_len=len(reply or ""),
            )
        elif dispatch.kind == "enterprise_command":
            result = handle_enterprise_command_fn(
                actor_id=dispatch.user_id,
                chat_id=dispatch.chat_id,
                command=dispatch.command or "",
                args=dispatch.args,
                raw_text=dispatch.text or "",
                raw_update=dispatch.raw_update,
            )
            reply = result.get("response_text", "(no response)")
            record_event(
                component="webhook",
                event="webhook.enterprise_service.ok",
                update_id=update_id,
                chat_id=chat_id,
                command=dispatch.command,
                enterprise_status=result.get("status"),
                reply_len=len(reply or ""),
            )
        else:
            moderation = handle_enterprise_moderation_fn(
                actor_id=dispatch.user_id,
                chat_id=dispatch.chat_id,
                raw_text=dispatch.text or "",
                raw_update=dispatch.raw_update,
            )
            if moderation.get("status") == "blocked":
                reply = moderation.get("response_text", "Mensaje bloqueado.")
                record_event(
                    component="webhook",
                    event="webhook.enterprise_moderation.blocked",
                    update_id=update_id,
                    chat_id=chat_id,
                    reason=moderation.get("reason"),
                    source=moderation.get("source"),
                    reply_len=len(reply or ""),
                )
            else:
                result = handle_chat_message_fn(chat_id, dispatch.text)
                reply = result.get("response", "(no response)")
                record_event(
                    component="webhook",
                    event="webhook.chat_service.ok",
                    update_id=update_id,
                    chat_id=chat_id,
                    reply_len=len(reply or ""),
                )
    except Exception:
        logger.exception("webhook.service_error", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.service.error",
            level="ERROR",
            update_id=update_id,
            chat_id=chat_id,
        )
        if chat_api_error_metric is not None:
            chat_api_error_metric.inc()
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
        if telegram_send_error_metric is not None:
            telegram_send_error_metric.inc()

    if process_time_metric is not None:
        process_time_metric.observe(time.time() - start)


async def handle_webhook_impl(
    *,
    token: str,
    request: Request,
    bot_token: Optional[str],
    webhook_token: Optional[str],
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

    if webhook_token is not None:
        if token != webhook_token:
            requests_metric.labels(status="forbidden").inc()
            record_event(component="webhook", event="webhook.forbidden", level="WARN", detail="invalid_webhook_token")
            raise HTTPException(status_code=403, detail="Invalid token")
    else:
        if token != bot_token:
            requests_metric.labels(status="forbidden").inc()
            record_event(component="webhook", event="webhook.forbidden", level="WARN", detail="invalid_legacy_token")
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
        async def _run_processor() -> None:
            result = process_update_sync(update)
            if inspect.isawaitable(result):
                await result

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
                await _run_processor()
        elif process_async and task_queue is None:
            logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
            record_event(
                component="webhook",
                event="webhook.enqueue.unavailable",
                level="WARN",
                update_id=update_id,
                chat_id=chat_id,
            )
            await _run_processor()
        else:
            await _run_processor()

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

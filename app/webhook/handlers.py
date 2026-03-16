"""Webhook domain logic decoupled from infrastructure libraries."""

import inspect
import time
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request

from app.enterprise import handle_enterprise_command, handle_enterprise_moderation
from app.manager_bot._menu_service import get_menu_engine, get_rate_limiter
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
        if dispatch.kind == "callback_query":
            menu_engine = get_menu_engine()
            rate_limiter = get_rate_limiter()
            callback_data = dispatch.text
            user_id = dispatch.user_id
            
            # Rate limit check
            if rate_limiter and not rate_limiter.is_allowed(user_id, "callback"):
                callback_query_id = dispatch.raw_update.get("callback_query", {}).get("id")
                if callback_query_id:
                    telegram_client.answer_callback_query(
                        callback_query_id=callback_query_id,
                        text="⚠️ Demasiadas solicitudes. Intenta más tarde.",
                        show_alert=True
                    )
                record_event(
                    component="webhook",
                    event="webhook.callback_query.rate_limited",
                    update_id=update_id,
                    user_id=user_id,
                )
                return
            
            if menu_engine and callback_data:
                await menu_engine.handle_callback_query_raw(
                    callback_data=callback_data,
                    callback_query_id=dispatch.raw_update.get("callback_query", {}).get("id"),
                    chat_id=chat_id,
                    message_id=dispatch.raw_update.get("callback_query", {}).get("message", {}).get("message_id"),
                    user_id=user_id,
                )
            else:
                callback_query_id = dispatch.raw_update.get("callback_query", {}).get("id")
                if callback_query_id:
                    telegram_client.answer_callback_query(
                        callback_query_id=callback_query_id,
                        text="Acción no reconocida",
                        show_alert=True
                    )
            record_event(
                component="webhook",
                event="webhook.callback_query.ok",
                update_id=update_id,
                chat_id=chat_id,
                callback_data=callback_data,
            )
            return
        
        if dispatch.kind == "chat_message":
            from app.manager_bot._menu_service import get_conversation_state
            conversation = get_conversation_state()
            user_id = dispatch.user_id
            chat_id = dispatch.chat_id
            text = dispatch.text
            
            state = conversation.get_state(user_id, chat_id)
            if state and state.get("state") == "waiting_welcome_text":
                from app.manager_bot._config.storage import get_config_storage
                from app.manager_bot._config.group_config import GroupConfig
                config_storage = get_config_storage()
                config = await config_storage.get(chat_id)
                if not config:
                    config = GroupConfig.create_default(chat_id, "default")
                config.welcome_text = text
                config.update_timestamp(user_id)
                await config_storage.set(config)
                conversation.clear_state(user_id, chat_id)
                reply = f"✅ Mensaje de bienvenida guardado:\n\n{text}"
            elif state and state.get("state") == "waiting_goodbye_text":
                from app.manager_bot._config.storage import get_config_storage
                from app.manager_bot._config.group_config import GroupConfig
                config_storage = get_config_storage()
                config = await config_storage.get(chat_id)
                if not config:
                    config = GroupConfig.create_default(chat_id, "default")
                config.goodbye_text = text
                config.update_timestamp(user_id)
                await config_storage.set(config)
                conversation.clear_state(user_id, chat_id)
                reply = f"✅ Mensaje de despedida guardado:\n\n{text}"
            else:
                result = handle_chat_message_fn(chat_id, text)
                reply = result.get("response", "(no response)")
        elif dispatch.kind == "ops_command":
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
            
            # Handle menu status - display interactive menu instead of text
            if result.get("status") == "menu":
                menu_engine = get_menu_engine()
                menu_id = result.get("menu_id", "main")
                if menu_engine:
                    await menu_engine.send_menu_message(
                        chat_id=chat_id,
                        bot=telegram_client,
                        menu_id=menu_id,
                    )
                    record_event(
                        component="webhook",
                        event="webhook.menu.display",
                        update_id=update_id,
                        chat_id=chat_id,
                        menu_id=menu_id,
                    )
                    return
            
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

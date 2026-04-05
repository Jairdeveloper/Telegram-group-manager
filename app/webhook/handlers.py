"""Webhook domain logic decoupled from infrastructure libraries."""

import inspect
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request

from app.enterprise import handle_enterprise_command, handle_enterprise_moderation
from app.manager_bot._menu_service import get_menu_engine, get_rate_limiter
from app.manager_bot._utils.duration_parser import parse_duration_to_seconds
from app.ops.policies import check_rate_limit, is_admin
from app.ops.services import handle_chat_message, handle_ops_command
from app.ops.events import record_event
from app.agent.core import AgentContext, get_default_agent_core
from app.agent.actions import ActionParser, ActionExecutor
from app.agent.actions.registry import get_default_registry
from app.agent.actions.types import ActionContext as AgentActionContext
from app.telegram.dispatcher import dispatch_telegram_update
from app.telegram.services import extract_chat_payload
from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient
from .processors import ProcessorFactory
from .response import ResponseBuilder, TelegramResponseSender


async def _maybe_await(result):
    if inspect.isawaitable(result):
        return await result
    return result


_manager_bot_router = None
_agent_core = None


def _get_manager_bot_router():
    global _manager_bot_router
    if _manager_bot_router is None:
        from app.manager_bot.core import ManagerBot
        _manager_bot_router = ManagerBot().get_router()
    return _manager_bot_router


def _get_agent_core():
    global _agent_core
    if _agent_core is None:
        _agent_core = get_default_agent_core()
    return _agent_core


def _get_user_roles(user_id: Optional[int], chat_id: int, is_admin_fn) -> list[str]:
    """Get user roles based on admin check and Telegram status."""
    if user_id is None:
        return []
    
    # Check if user is admin via is_admin_fn
    if is_admin_fn is not None and is_admin_fn(chat_id):
        return ["admin"]
    
    # TODO: Integrate with Telegram API to get actual user roles
    # For now, return empty list (user will need explicit admin/moderator role)
    return []


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


def build_processor_context(
    telegram_client: TelegramClient,
    logger,
    handle_chat_message_fn,
    handle_ops_command_fn,
    handle_enterprise_command_fn,
    handle_enterprise_moderation_fn,
    is_admin_fn,
    rate_limit_check,
) -> Dict[str, Any]:
    """Build context dict for processors."""
    return {
        "telegram_client": telegram_client,
        "logger": logger,
        "handle_chat_message_fn": handle_chat_message_fn,
        "handle_ops_command_fn": handle_ops_command_fn,
        "handle_enterprise_command_fn": handle_enterprise_command_fn,
        "handle_enterprise_moderation_fn": handle_enterprise_moderation_fn,
        "is_admin_fn": is_admin_fn,
        "rate_limit_check": rate_limit_check,
    }


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
    
    if update.get("callback_query"):
        dispatch = dispatch_telegram_update(update)
    else:
        router = _get_manager_bot_router()
        dispatch = router.route_update(update).to_legacy_dispatch()
    
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

    context = build_processor_context(
        telegram_client=telegram_client,
        logger=logger,
        handle_chat_message_fn=handle_chat_message_fn,
        handle_ops_command_fn=handle_ops_command_fn,
        handle_enterprise_command_fn=handle_enterprise_command_fn,
        handle_enterprise_moderation_fn=handle_enterprise_moderation_fn,
        is_admin_fn=is_admin_fn,
        rate_limit_check=rate_limit_check,
    )

    try:
        processor = ProcessorFactory.get_processor(dispatch.kind, context)
        result = await processor.process(dispatch, context)
        response = ResponseBuilder.build_from_processor_result(result)
        
        sender = TelegramResponseSender(telegram_client, logger)
        await sender.send_response(
            chat_id=chat_id,
            text=response.text,
            menu_id=response.menu_to_show,
            update_id=update_id,
            send_message_metric=telegram_send_error_metric,
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
        
        sender = TelegramResponseSender(telegram_client, logger)
        await sender.send_reply(chat_id, "(internal error)", update_id)

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
    ptb_webhook_handler: Optional[Any] = None,
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

    update = None
    body = None
    if hasattr(request, "body"):
        try:
            body = await request.body()
        except Exception:
            body = None

    if body is not None:
        if ptb_webhook_handler is not None and hasattr(ptb_webhook_handler, "to_internal"):
            update = ptb_webhook_handler.to_internal(body)

        if not update:
            try:
                update = json.loads(body)
            except Exception:
                logger.exception("webhook.invalid_json")
                requests_metric.labels(status="invalid").inc()
                return {"ok": True}
    else:
        try:
            update = await request.json()
        except Exception:
            logger.exception("webhook.invalid_json")
            requests_metric.labels(status="invalid").inc()
            return {"ok": True}

        if ptb_webhook_handler is not None and hasattr(ptb_webhook_handler, "to_internal"):
            try:
                body = json.dumps(update).encode("utf-8")
            except Exception:
                body = None
            if body:
                ptb_update = ptb_webhook_handler.to_internal(body)
                if ptb_update:
                    update = ptb_update
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
            logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
            record_event(
                component="webhook",
                event="webhook.enqueue.unavailable",
                level="WARN",
                update_id=update_id,
                chat_id=chat_id,
            )
            await _run_processor()  # ← AGREGADO: Fallback a sync processing
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




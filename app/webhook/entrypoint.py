"""Canonical webhook entrypoint (composition root)."""

from typing import Any, Dict

from app.ops.policies import check_rate_limit, is_admin
from app.ops.services import handle_chat_message, handle_ops_command

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.webhook.handlers import dedup_update_impl, handle_webhook_impl, process_update_impl
from app.webhook.infrastructure import InMemoryDedupStore
from app.webhook.bootstrap import build_webhook_runtime
from webhook_tasks import process_update as process_update_task

runtime = build_webhook_runtime(process_update_callable=process_update_task)

# Re-exported runtime state (kept mutable for tests/legacy wrappers).
LOGGER = runtime.logger
BOT_TOKEN = runtime.bot_token
WEBHOOK_TOKEN = runtime.webhook_token
CHATBOT_API_URL = runtime.chatbot_api_url
PROCESS_ASYNC = runtime.process_async
DEDUP_TTL = runtime.dedup_ttl
DEDUP_STORE = runtime.dedup_store
TASK_QUEUE = runtime.task_queue
CHAT_API_CLIENT = runtime.chat_api_client
TELEGRAM_CLIENT = runtime.telegram_client
REQUESTS = runtime.requests_metric
PROCESS_TIME = runtime.process_time_metric
CHAT_API_ERROR = runtime.chat_api_error_metric
TELEGRAM_SEND_ERROR = runtime.telegram_send_error_metric
CHAT_API = CHATBOT_API_URL

app = FastAPI()


def dedup_update(update_id: int) -> bool:
    """Return True if update is new (not duplicate)."""
    if isinstance(DEDUP_STORE, InMemoryDedupStore):
        dedup_update._seen = DEDUP_STORE.seen
    return dedup_update_impl(
        update_id,
        dedup_store=DEDUP_STORE,
        dedup_ttl=DEDUP_TTL,
        logger=LOGGER,
    )


async def process_update_sync(update: Dict[str, Any]):
    """Process an update synchronously using shared domain service."""
    await process_update_impl(
        update,
        telegram_client=TELEGRAM_CLIENT,
        process_time_metric=PROCESS_TIME,
        chat_api_error_metric=CHAT_API_ERROR,
        telegram_send_error_metric=TELEGRAM_SEND_ERROR,
        logger=LOGGER,
        handle_chat_message_fn=handle_chat_message,
        handle_ops_command_fn=handle_ops_command,
        is_admin_fn=is_admin,
        rate_limit_check=check_rate_limit,
    )


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    return await handle_webhook_impl(
        token=token,
        request=request,
        bot_token=BOT_TOKEN,
        webhook_token=WEBHOOK_TOKEN,
        dedup_update=dedup_update,
        process_async=PROCESS_ASYNC,
        task_queue=TASK_QUEUE,
        process_update_sync=process_update_sync,
        requests_metric=REQUESTS,
        logger=LOGGER,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


def create_webhook_app():
    """Factory-compatible accessor for webhook app."""
    return app

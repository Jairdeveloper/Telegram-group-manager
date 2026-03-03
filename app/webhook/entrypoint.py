"""Canonical webhook entrypoint (composition root)."""

import logging
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.config.settings import load_webhook_settings
from app.webhook.handlers import dedup_update_impl, handle_webhook_impl, process_update_impl
from app.webhook.infrastructure import (
    InMemoryDedupStore,
    RedisDedupStore,
    RequestsChatApiClient,
    RequestsTelegramClient,
    RqTaskQueue,
)
from webhook_tasks import process_update as process_update_task

try:
    from redis import Redis
    from rq import Queue
except Exception:
    Redis = None
    Queue = None

load_dotenv()

LOGGER = logging.getLogger("telegram_webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

WEBHOOK_SETTINGS = load_webhook_settings()
BOT_TOKEN = WEBHOOK_SETTINGS.telegram_bot_token
CHAT_API = WEBHOOK_SETTINGS.chatbot_api_url
REDIS_URL = WEBHOOK_SETTINGS.redis_url
PROCESS_ASYNC = WEBHOOK_SETTINGS.process_async
DEDUP_TTL = WEBHOOK_SETTINGS.dedup_ttl
QUEUE_NAME = "telegram_tasks"

redis_client = None
queue = None
if REDIS_URL and Redis is not None:
    redis_client = Redis.from_url(REDIS_URL)
    if Queue is not None:
        queue = Queue(QUEUE_NAME, connection=redis_client)

CHAT_API_CLIENT = RequestsChatApiClient(chat_api_url=CHAT_API)
TELEGRAM_CLIENT = RequestsTelegramClient(bot_token=BOT_TOKEN or "")
if redis_client is not None:
    DEDUP_STORE = RedisDedupStore(redis_client=redis_client)
else:
    _SEEN = set()
    DEDUP_STORE = InMemoryDedupStore(memory_store=_SEEN)
TASK_QUEUE = RqTaskQueue(queue=queue, process_update_callable=process_update_task) if queue is not None else None

if PROCESS_ASYNC and TASK_QUEUE is None:
    LOGGER.warning(
        "PROCESS_ASYNC=true but async queue is unavailable; falling back to synchronous processing"
    )

REQUESTS = Counter("telegram_webhook_requests_total", "Total webhook requests", ["status"])
PROCESS_TIME = Histogram("telegram_webhook_process_seconds", "Time spent processing webhook")

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


def process_update_sync(update: Dict[str, Any]):
    """Process an update synchronously using shared domain service."""
    process_update_impl(
        update,
        chat_api_client=CHAT_API_CLIENT,
        telegram_client=TELEGRAM_CLIENT,
        process_time_metric=PROCESS_TIME,
        logger=LOGGER,
    )


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    return await handle_webhook_impl(
        token=token,
        request=request,
        bot_token=BOT_TOKEN,
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
    return app

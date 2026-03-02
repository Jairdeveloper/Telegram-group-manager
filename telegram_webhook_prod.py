"""Production-ready Telegram webhook service (FastAPI).

Features:
- Validates BOT_TOKEN in route
- Deduplicates updates using Redis (if configured)
- Enqueues processing to RQ (Redis Queue) when REDIS_URL present
- Supports synchronous fallback (no Redis)
- Exposes /metrics for Prometheus
"""
import os
import logging
import uuid
from typing import Any, Dict

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

try:
    from redis import Redis
    from rq import Queue
except Exception:
    Redis = None
    Queue = None

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from dotenv import load_dotenv
from app.webhook.handlers import (
    dedup_update_impl,
    handle_webhook_impl,
    process_update_sync_impl,
    send_message_impl,
)

load_dotenv()

LOGGER = logging.getLogger("telegram_webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_API = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8000/api/v1/chat")
REDIS_URL = os.getenv("REDIS_URL")
PROCESS_ASYNC = os.getenv("PROCESS_ASYNC", "true").lower() in ("1", "true", "yes")
DEDUP_TTL = int(os.getenv("DEDUP_TTL", "86400"))

redis_client = None
queue = None
if REDIS_URL and Redis is not None:
    redis_client = Redis.from_url(REDIS_URL)
    if Queue is not None:
        queue = Queue("telegram_tasks", connection=redis_client)

# Metrics
REQUESTS = Counter("telegram_webhook_requests_total", "Total webhook requests", ["status"])
PROCESS_TIME = Histogram("telegram_webhook_process_seconds", "Time spent processing webhook")

app = FastAPI()


def dedup_update(update_id: int) -> bool:
    """Return True if update is new (not duplicate)."""
    if not hasattr(dedup_update, "_seen"):
        dedup_update._seen = set()
    return dedup_update_impl(
        update_id,
        redis_client=redis_client,
        dedup_ttl=DEDUP_TTL,
        memory_store=dedup_update._seen,
        logger=LOGGER,
    )


def send_message(chat_id: int, text: str) -> Dict[str, Any]:
    return send_message_impl(
        bot_token=BOT_TOKEN,
        chat_id=chat_id,
        text=text,
        requests_module=requests,
    )


def process_update_sync(update: Dict[str, Any]):
    """Process an update synchronously: call Chat API and send reply via Telegram."""
    process_update_sync_impl(
        update,
        chat_api=CHAT_API,
        send_message=send_message,
        requests_module=requests,
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
        queue=queue,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("telegram_webhook_prod:app", host="0.0.0.0", port=80, log_level="info")

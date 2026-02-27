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
import time
import uuid
import hmac
import hashlib
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
    """Return True if update is new (not duplicate). Uses Redis if available, else in-memory fallback."""
    key = f"tg:update:{update_id}"
    try:
        if redis_client:
            # SETNX + expire
            added = redis_client.setnx(key, "1")
            if added:
                redis_client.expire(key, DEDUP_TTL)
                return True
            return False
        else:
            # naive in-memory fallback (not for prod)
            if not hasattr(dedup_update, "_seen"):
                dedup_update._seen = set()
            if update_id in dedup_update._seen:
                return False
            dedup_update._seen.add(update_id)
            return True
    except Exception:
        LOGGER.exception("Dedup check failed")
        return True


def send_message(chat_id: int, text: str) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    return {"status_code": resp.status_code, "text": resp.text}


def process_update_sync(update: Dict[str, Any]):
    """Process an update synchronously: call Chat API and send reply via Telegram"""
    start = time.time()
    chat = update.get("message") or update.get("edited_message")
    if not chat:
        return

    chat_id = chat["chat"]["id"]
    text = chat.get("text", "")
    session_id = str(chat_id)

    try:
        r = requests.post(CHAT_API, params={"message": text, "session_id": session_id}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            reply = data.get("response", "(no response)")
        else:
            reply = "(chat api error)"
    except Exception:
        LOGGER.exception("Chat API call failed")
        reply = "(internal error)"

    # send reply
    try:
        send_message(chat_id, reply)
    except Exception:
        LOGGER.exception("Failed to send message to Telegram")

    PROCESS_TIME.observe(time.time() - start)


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")

    if token != BOT_TOKEN:
        REQUESTS.labels(status="forbidden").inc()
        raise HTTPException(status_code=403, detail="Invalid token")

    update = await request.json()
    update_id = update.get("update_id")

    # Deduplicate
    if update_id is not None and not dedup_update(update_id):
        LOGGER.info("Duplicate update ignored", extra={"update_id": update_id})
        REQUESTS.labels(status="duplicate").inc()
        return {"ok": True}

    # Enqueue or process inline
    try:
        if PROCESS_ASYNC and queue is not None:
            # enqueue job
            job = queue.enqueue(process_update_sync, update, job_id=str(uuid.uuid4()))
            # RQ Job id is available as `id` attribute
            LOGGER.info("Enqueued update", extra={"job_id": getattr(job, 'id', None), "update_id": update_id})
        else:
            # synchronous processing (fast path)
            process_update_sync(update)

        REQUESTS.labels(status="ok").inc()
        return {"ok": True}
    except Exception:
        LOGGER.exception("Failed handling update")
        REQUESTS.labels(status="error").inc()
        # Always return 200 to Telegram to avoid retry storms; rely on background retry or DLQ
        return {"ok": True}


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

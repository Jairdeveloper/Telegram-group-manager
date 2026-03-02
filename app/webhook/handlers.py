"""Webhook business logic extracted from transport layer."""

import time
import uuid
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request


def dedup_update_impl(
    update_id: int,
    *,
    redis_client,
    dedup_ttl: int,
    memory_store: set,
    logger,
) -> bool:
    """Return True if update is new; False if duplicate."""
    key = f"tg:update:{update_id}"
    try:
        if redis_client:
            added = redis_client.setnx(key, "1")
            if added:
                redis_client.expire(key, dedup_ttl)
                return True
            return False

        if update_id in memory_store:
            return False
        memory_store.add(update_id)
        return True
    except Exception:
        logger.exception("Dedup check failed")
        return True


def send_message_impl(*, bot_token: str, chat_id: int, text: str, requests_module) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests_module.post(url, json=payload, timeout=10)
    return {"status_code": resp.status_code, "text": resp.text}


def process_update_sync_impl(
    update: Dict[str, Any],
    *,
    chat_api: str,
    send_message: Callable[[int, str], Dict[str, Any]],
    requests_module,
    process_time_metric,
    logger,
) -> None:
    """Process an update synchronously by querying Chat API and replying in Telegram."""
    start = time.time()
    chat = update.get("message") or update.get("edited_message")
    if not chat:
        return

    chat_id = chat["chat"]["id"]
    text = chat.get("text", "")
    session_id = str(chat_id)

    try:
        r = requests_module.post(
            chat_api, params={"message": text, "session_id": session_id}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            reply = data.get("response", "(no response)")
        else:
            reply = "(chat api error)"
    except Exception:
        logger.exception("Chat API call failed")
        reply = "(internal error)"

    try:
        send_message(chat_id, reply)
    except Exception:
        logger.exception("Failed to send message to Telegram")

    process_time_metric.observe(time.time() - start)


async def handle_webhook_impl(
    *,
    token: str,
    request: Request,
    bot_token: Optional[str],
    dedup_update: Callable[[int], bool],
    process_async: bool,
    queue,
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
        if process_async and queue is not None:
            job = queue.enqueue(process_update_sync, update, job_id=str(uuid.uuid4()))
            logger.info(
                "Enqueued update",
                extra={"job_id": getattr(job, "id", None), "update_id": update_id},
            )
        else:
            process_update_sync(update)

        requests_metric.labels(status="ok").inc()
        return {"ok": True}
    except Exception:
        logger.exception("Failed handling update")
        requests_metric.labels(status="error").inc()
        return {"ok": True}


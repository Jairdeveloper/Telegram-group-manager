"""Dependency bootstrap for webhook runtime."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from prometheus_client import Counter, Histogram

from app.config.settings import load_webhook_settings
from app.webhook.infrastructure import (
    InMemoryDedupStore,
    RedisDedupStore,
    RequestsChatApiClient,
    RequestsTelegramClient,
    RqTaskQueue,
)

try:
    from redis import Redis
    from rq import Queue
except Exception:
    Redis = None
    Queue = None


@dataclass
class WebhookRuntime:
    logger: logging.Logger
    bot_token: str | None
    webhook_token: str | None
    chatbot_api_url: str
    process_async: bool
    dedup_ttl: int
    dedup_store: object
    task_queue: object | None
    chat_api_client: RequestsChatApiClient
    telegram_client: RequestsTelegramClient
    requests_metric: Counter
    process_time_metric: Histogram
    chat_api_error_metric: Counter
    telegram_send_error_metric: Counter


def build_webhook_runtime(*, process_update_callable, queue_name: str = "telegram_tasks") -> WebhookRuntime:
    """Build and return concrete runtime dependencies for webhook transport."""
    load_dotenv()

    logger = logging.getLogger("telegram_webhook")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    settings = load_webhook_settings()
    bot_token = settings.telegram_bot_token
    webhook_token = settings.webhook_token
    chatbot_api_url = settings.chatbot_api_url
    redis_url = settings.redis_url
    process_async = settings.process_async
    dedup_ttl = settings.dedup_ttl

    redis_client = None
    rq_queue = None
    if redis_url and Redis is not None:
        redis_client = Redis.from_url(redis_url)
        if Queue is not None:
            rq_queue = Queue(queue_name, connection=redis_client)

    chat_api_client = RequestsChatApiClient(chat_api_url=chatbot_api_url)
    telegram_client = RequestsTelegramClient(bot_token=bot_token or "")

    if redis_client is not None:
        dedup_store = RedisDedupStore(redis_client=redis_client)
    else:
        dedup_store = InMemoryDedupStore(memory_store=set())

    task_queue = (
        RqTaskQueue(queue=rq_queue, process_update_callable=process_update_callable)
        if rq_queue is not None
        else None
    )

    if process_async and task_queue is None:
        logger.warning(
            "webhook.async_queue_unavailable_on_startup"
        )

    requests_metric = Counter("telegram_webhook_requests_total", "Total webhook requests", ["status"])
    process_time_metric = Histogram("telegram_webhook_process_seconds", "Time spent processing webhook")
    chat_api_error_metric = Counter("telegram_webhook_chat_api_errors_total", "Total Chat API errors")
    telegram_send_error_metric = Counter("telegram_webhook_telegram_send_errors_total", "Total Telegram send errors")

    return WebhookRuntime(
        logger=logger,
        bot_token=bot_token,
        webhook_token=webhook_token,
        chatbot_api_url=chatbot_api_url,
        process_async=process_async,
        dedup_ttl=dedup_ttl,
        dedup_store=dedup_store,
        task_queue=task_queue,
        chat_api_client=chat_api_client,
        telegram_client=telegram_client,
        requests_metric=requests_metric,
        process_time_metric=process_time_metric,
        chat_api_error_metric=chat_api_error_metric,
        telegram_send_error_metric=telegram_send_error_metric,
    )

"""Dependency bootstrap for webhook runtime."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from prometheus_client import Counter, Histogram

from app.config.settings import load_webhook_settings
from app.manager_bot._menu_service import create_menu_engine
from app.webhook.infrastructure import (
    InMemoryDedupStore,
    RedisDedupStore,
    RequestsChatApiClient,
    RequestsTelegramClient,
    RqTaskQueue,
    get_telegram_client,
)

try:
    from robot_ptb_compat.runtime import CompatApplicationBuilder, WebhookRunner
    HAS_ROBOT_PTB_COMPAT = True
except ImportError:
    HAS_ROBOT_PTB_COMPAT = False
    CompatApplicationBuilder = None
    WebhookRunner = None


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
    telegram_client = get_telegram_client(bot_token or "")

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

    # Initialize menu engine
    try:
        storage_type = os.getenv("MENU_STORAGE_TYPE", "memory")
        database_url = os.getenv("DATABASE_URL")
        redis_url = os.getenv("REDIS_URL")
        
        menu_engine, rate_limiter = create_menu_engine(
            storage_type=storage_type,
            database_url=database_url,
            redis_url=redis_url,
        )
        logger.info("Menu engine initialized successfully", extra={
            "storage": storage_type,
            "menus_count": len(menu_engine.registry.list_menus()) if menu_engine else 0,
        })
    except Exception as e:
        logger.error(f"Failed to initialize menu engine: {e}")
        menu_engine = None
        rate_limiter = None

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


def build_ptb_application(bot_token: str, handlers: list = None):
    """Build a PTB Application using robot-ptb-compat if available.
    
    Args:
        bot_token: Telegram bot token
        handlers: List of handlers to register
        
    Returns:
        PTB Application or None if robot-ptb-compat not available
    """
    if not HAS_ROBOT_PTB_COMPAT or CompatApplicationBuilder is None:
        return None
    
    try:
        app = (
            CompatApplicationBuilder(token=bot_token)
            .build()
        )
        return app
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to build PTB application: {e}")
        return None


def get_webhook_runner(bot_token: str, application=None):
    """Get a WebhookRunner using robot-ptb-compat if available.
    
    Args:
        bot_token: Telegram bot token
        application: PTB Application (optional)
        
    Returns:
        WebhookRunner or None if not available
    """
    if not HAS_ROBOT_PTB_COMPAT or WebhookRunner is None:
        return None
    
    from app.webhook.infrastructure import get_telegram_client
    telegram_client = get_telegram_client(bot_token)
    
    return WebhookRunner(application=application, bot=telegram_client.bot if hasattr(telegram_client, 'bot') else None)

"""Canonical webhook entrypoint (composition root)."""

from typing import Any, Dict
import importlib.util

from app.ops.policies import check_rate_limit, is_admin
from app.ops.services import handle_chat_message, handle_ops_command

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.webhook.handlers import dedup_update_impl, handle_webhook_impl, process_update_impl
from app.webhook.infrastructure import InMemoryDedupStore
from app.webhook.bootstrap import build_webhook_runtime

from app.manager_bot.core import ManagerBot


def _load_webhook_tasks():
    """Dynamically load webhook_tasks module from project root."""
    import os
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    webhook_tasks_path = project_root / "webhook_tasks.py"
    
    spec = importlib.util.spec_from_file_location("webhook_tasks", webhook_tasks_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


webhook_tasks_module = _load_webhook_tasks()
process_update_task = webhook_tasks_module.process_update

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
PTB_WEBHOOK_HANDLER = runtime.ptb_webhook_handler
PTB_APPLICATION = runtime.ptb_application
REQUESTS = runtime.requests_metric
PROCESS_TIME = runtime.process_time_metric
CHAT_API_ERROR = runtime.chat_api_error_metric
TELEGRAM_SEND_ERROR = runtime.telegram_send_error_metric
CHAT_API = CHATBOT_API_URL

app = FastAPI()

# ManagerBot integration (FASE 0)
_manager_bot = None


def _get_manager_bot():
    """Get or create ManagerBot instance."""
    global _manager_bot
    if _manager_bot is None:
        from app.manager_bot.core import ManagerBot
        _manager_bot = ManagerBot()
    return _manager_bot


# Include ManagerBot routes in the main app
@app.on_event("startup")
async def mount_manager_bot():
    """Mount ManagerBot routes on startup."""
    manager = _get_manager_bot()
    manager_app = manager.get_app()
    app.mount("/manager", manager_app)


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


def _register_ptb_handlers() -> None:
    """Register ManagerBot handlers into PTB application when available."""
    if PTB_APPLICATION is None:
        return
    from app.manager_bot._transport.telegram.ptb_adapter import ManagerBotPtbAdapter

    adapter = ManagerBotPtbAdapter(_get_manager_bot(), process_update_sync)
    adapter.register(PTB_APPLICATION)


_register_ptb_handlers()


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
        ptb_webhook_handler=PTB_WEBHOOK_HANDLER,
    )


@app.get("/health")
async def health():
    redis_status = {"status": "unavailable", "error": "not_configured"}
    
    try:
        from app.config.redis import get_redis_manager
        redis_manager = get_redis_manager()
        redis_status = redis_manager.health_check()
    except Exception as e:
        redis_status = {"status": "error", "error": str(e)}
    
    return {
        "status": "ok",
        "redis": redis_status,
    }


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


def create_webhook_app():
    """Factory-compatible accessor for webhook app."""
    return app


def main():
    """Entry point para CLI."""
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "app.webhook.entrypoint:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

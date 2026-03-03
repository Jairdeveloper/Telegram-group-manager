"""Legacy compatibility wrapper for webhook runtime.

Canonical source now lives in `app.webhook.entrypoint`.
"""

from app.webhook.entrypoint import (  # noqa: F401
    BOT_TOKEN,
    CHAT_API,
    DEDUP_STORE,
    DEDUP_TTL,
    LOGGER,
    PROCESS_ASYNC,
    PROCESS_TIME,
    REQUESTS,
    TASK_QUEUE,
    TELEGRAM_CLIENT,
    app,
    dedup_update,
    process_update_sync,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.webhook.entrypoint:app", host="0.0.0.0", port=80, log_level="info")

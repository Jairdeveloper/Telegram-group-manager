"""Tasks executed by workers (called from RQ)."""
import asyncio
import logging

from app.config.settings import load_webhook_settings
from app.ops.policies import check_rate_limit, is_admin
from app.ops.services import handle_chat_message, handle_ops_command
from app.webhook.handlers import process_update_impl
from app.webhook.infrastructure import get_telegram_client

LOGGER = logging.getLogger("webhook_tasks")
WEBHOOK_SETTINGS = load_webhook_settings()
BOT_TOKEN = WEBHOOK_SETTINGS.telegram_bot_token
TELEGRAM_CLIENT = get_telegram_client(BOT_TOKEN or "")


def process_update(update: dict):
    """Process an update via shared webhook domain service."""
    asyncio.run(
        process_update_impl(
            update,
            telegram_client=TELEGRAM_CLIENT,
            logger=LOGGER,
            process_time_metric=None,
            handle_chat_message_fn=handle_chat_message,
            handle_ops_command_fn=handle_ops_command,
            is_admin_fn=is_admin,
            rate_limit_check=check_rate_limit,
        )
    )

"""Tasks executed by workers (called from RQ)."""
import logging

from app.config.settings import load_webhook_settings
from app.webhook.handlers import process_update_impl
from app.webhook.infrastructure import RequestsChatApiClient, RequestsTelegramClient

LOGGER = logging.getLogger("webhook_tasks")
WEBHOOK_SETTINGS = load_webhook_settings()
BOT_TOKEN = WEBHOOK_SETTINGS.telegram_bot_token
CHATBOT_API_URL = WEBHOOK_SETTINGS.chatbot_api_url
CHAT_API_CLIENT = RequestsChatApiClient(chat_api_url=CHATBOT_API_URL)
TELEGRAM_CLIENT = RequestsTelegramClient(bot_token=BOT_TOKEN or "")


def process_update(update: dict):
    """Process an update via shared webhook domain service."""
    process_update_impl(
        update,
        chat_api_client=CHAT_API_CLIENT,
        telegram_client=TELEGRAM_CLIENT,
        logger=LOGGER,
        process_time_metric=None,
    )

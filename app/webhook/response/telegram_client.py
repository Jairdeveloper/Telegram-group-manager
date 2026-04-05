"""Telegram client wrapper for sending responses."""

import logging
from typing import Any, Dict, Optional

from app.manager_bot._menu_service import get_menu_engine
from app.ops.events import record_event


logger = logging.getLogger(__name__)


class TelegramResponseSender:
    """Client for sending Telegram responses."""

    def __init__(self, telegram_client: Any, logger: Optional[logging.Logger] = None):
        self.telegram_client = telegram_client
        self.logger = logger or logging.getLogger(__name__)

    async def send_reply(
        self,
        chat_id: int,
        text: str,
        update_id: int,
    ) -> bool:
        """Send reply message to Telegram."""
        try:
            import inspect
            if inspect.isawaitable(self.telegram_client.send_message):
                await self.telegram_client.send_message(chat_id=chat_id, text=text)
            else:
                self.telegram_client.send_message(chat_id=chat_id, text=text)

            record_event(
                component="webhook",
                event="webhook.telegram_send.ok",
                update_id=update_id,
                chat_id=chat_id,
            )
            return True
        except Exception:
            self.logger.exception("webhook.telegram_send_error", extra={
                "update_id": update_id,
                "chat_id": chat_id,
            })
            record_event(
                component="webhook",
                event="webhook.telegram_send.error",
                level="ERROR",
                update_id=update_id,
                chat_id=chat_id,
            )
            return False

    async def send_menu(
        self,
        chat_id: int,
        menu_id: str,
    ) -> bool:
        """Send menu message to Telegram."""
        try:
            menu_engine = get_menu_engine()
            if menu_engine:
                await menu_engine.send_menu_message(
                    chat_id=chat_id,
                    bot=self.telegram_client,
                    menu_id=menu_id,
                )
                return True
        except Exception:
            self.logger.exception("webhook.menu.send_error", extra={
                "chat_id": chat_id,
                "menu_id": menu_id,
            })
        return False

    async def send_response(
        self,
        chat_id: int,
        text: str,
        menu_id: Optional[str],
        update_id: int,
        send_message_metric: Optional[Any] = None,
    ) -> bool:
        """Send complete response (text + menu)."""
        text = text.strip() if text else "(sin respuesta)"
        
        sent = await self.send_reply(chat_id, text, update_id)
        
        if send_message_metric is not None and not sent:
            send_message_metric.inc()

        if menu_id:
            await self.send_menu(chat_id, menu_id)

        return sent

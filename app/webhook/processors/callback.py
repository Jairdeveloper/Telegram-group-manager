"""Callback query processor."""

import logging
from typing import Any, Dict, Optional

from app.manager_bot._menu_service import get_menu_engine, get_rate_limiter
from app.ops.events import record_event

from .base import MessageProcessor, ProcessorResult


logger = logging.getLogger(__name__)


class CallbackProcessor(MessageProcessor):
    """Processor for callback queries."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.telegram_client = context.get("telegram_client")
        self.logger = context.get("logger")

    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process a callback query."""
        update_id = dispatch.update_id
        chat_id = dispatch.chat_id
        user_id = dispatch.user_id
        callback_data = dispatch.text
        raw_update = dispatch.raw_update

        menu_engine = get_menu_engine()
        rate_limiter = get_rate_limiter()

        if rate_limiter and not rate_limiter.is_allowed(user_id, "callback"):
            callback_query_id = raw_update.get("callback_query", {}).get("id")
            if callback_query_id and self.telegram_client:
                await self.telegram_client.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text="⚠️ Demasiadas solicitudes. Intenta más tarde.",
                    show_alert=True
                )
            record_event(
                component="webhook",
                event="webhook.callback_query.rate_limited",
                update_id=update_id,
                user_id=user_id,
            )
            return ProcessorResult()

        if menu_engine and callback_data:
            await menu_engine.handle_callback_query_raw(
                callback_data=callback_data,
                callback_query_id=raw_update.get("callback_query", {}).get("id"),
                chat_id=chat_id,
                message_id=raw_update.get("callback_query", {}).get("message", {}).get("message_id"),
                user_id=user_id,
            )
        else:
            callback_query_id = raw_update.get("callback_query", {}).get("id")
            if callback_query_id and self.telegram_client:
                await self.telegram_client.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text="Acción no reconocida",
                    show_alert=True
                )

        record_event(
            component="webhook",
            event="webhook.callback_query.ok",
            update_id=update_id,
            chat_id=chat_id,
            callback_data=callback_data,
        )

        return ProcessorResult()

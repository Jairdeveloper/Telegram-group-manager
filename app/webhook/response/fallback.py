"""Fallback handlers for webhook processor."""

import logging
from typing import Any, Callable, Dict, Optional

from app.ops.events import record_event


logger = logging.getLogger(__name__)


class FallbackHandler:
    """Handler for fallback responses when primary processing fails."""

    def __init__(
        self,
        chat_service_fn: Optional[Callable] = None,
        nlp_integration: Optional[Any] = None,
    ):
        self.chat_service_fn = chat_service_fn
        self.nlp_integration = nlp_integration

    async def handle_nlp_fallback(
        self,
        text: str,
        chat_id: int,
        update_id: int,
    ) -> Optional[str]:
        """Handle fallback to NLP processing."""
        try:
            if self.nlp_integration and text and self.nlp_integration.should_use_nlp(text):
                nlp_result = self.nlp_integration.process_message(text)
                if (nlp_result and
                    hasattr(nlp_result, 'action_result') and
                    nlp_result.action_result and
                    nlp_result.action_result.action_id):
                    reply = f"✓ Accion: {nlp_result.action_result.action_id}"
                    record_event(
                        component="webhook",
                        event="webhook.nlp_flow.ok",
                        update_id=update_id,
                        chat_id=chat_id,
                        action_id=nlp_result.action_result.action_id,
                        confidence=nlp_result.action_result.confidence,
                        intent=nlp_result.intent,
                    )
                    return reply
        except Exception as e:
            logger.error(f"NLP fallback error: {e}")

        return None

    async def handle_chat_service_fallback(
        self,
        text: str,
        chat_id: int,
        update_id: int,
    ) -> Optional[str]:
        """Handle fallback to chat service."""
        try:
            if self.chat_service_fn:
                result = self.chat_service_fn(chat_id, text)
                if result and isinstance(result, dict):
                    reply = result.get("response", "(no response)")
                else:
                    reply = "(no response)"
                    logger.warning(f"Invalid result from chat service: {result}")

                record_event(
                    component="webhook",
                    event="webhook.chat_service.ok",
                    update_id=update_id,
                    chat_id=chat_id,
                    reply_len=len(reply or ""),
                )
                return reply
        except Exception as e:
            import traceback
            logger.error(f"Chat service fallback error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            record_event(
                component="webhook",
                event="webhook.chat_service.fallback",
                update_id=update_id,
                chat_id=chat_id,
                error=str(e),
                error_type=type(e).__name__,
            )

        return None

    async def handle_full_fallback(
        self,
        text: str,
        chat_id: int,
        update_id: int,
    ) -> str:
        """Handle full fallback chain: NLP -> Chat Service."""
        nlp_reply = await self.handle_nlp_fallback(text, chat_id, update_id)
        if nlp_reply:
            return nlp_reply

        chat_reply = await self.handle_chat_service_fallback(text, chat_id, update_id)
        if chat_reply:
            return chat_reply

        return "(no response)"

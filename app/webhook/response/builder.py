"""Response builder for webhook processor."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


@dataclass
class BuiltResponse:
    """A built response ready to be sent."""
    text: str
    menu_to_show: Optional[str] = None
    should_send: bool = True


class ResponseBuilder:
    """Builder for constructing Telegram responses."""

    DEFAULT_EMPTY_RESPONSE = "(sin respuesta)"
    DEFAULT_ERROR_RESPONSE = "(internal error)"

    @staticmethod
    def build_reply(
        action_result: Optional[Any] = None,
        fallback_response: Optional[str] = None,
    ) -> str:
        """Build reply from action result or fallback."""
        if action_result and hasattr(action_result, "status"):
            if action_result.status == "ok" and action_result.message:
                return action_result.message
            elif action_result.status != "ok":
                return action_result.response_text or f"La acción falló: {action_result.status}"

        if fallback_response:
            return fallback_response

        return ""

    @staticmethod
    def validate_not_empty(reply: Optional[str]) -> str:
        """Validate reply is not empty, return default if empty."""
        if not reply or not reply.strip():
            logger.warning("webhook.empty_reply")
            return ResponseBuilder.DEFAULT_EMPTY_RESPONSE
        return reply.strip()

    @classmethod
    def build(
        cls,
        reply: Optional[str],
        menu_to_show: Optional[str] = None,
        error: bool = False,
    ) -> BuiltResponse:
        """Build a complete response."""
        if error:
            text = cls.DEFAULT_ERROR_RESPONSE
        else:
            text = cls.validate_not_empty(reply)

        return BuiltResponse(
            text=text,
            menu_to_show=menu_to_show,
            should_send=True,
        )

    @classmethod
    def build_from_processor_result(
        cls,
        processor_result: Optional[Any],
    ) -> BuiltResponse:
        """Build response from ProcessorResult."""
        if processor_result is None:
            return cls.build(reply=None)

        reply = getattr(processor_result, "reply", None)
        menu_to_show = getattr(processor_result, "menu_to_show", None)
        error = getattr(processor_result, "error", None)

        return cls.build(
            reply=reply,
            menu_to_show=menu_to_show,
            error=error is not None,
        )

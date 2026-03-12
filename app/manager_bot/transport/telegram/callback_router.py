"""Callback router for handling inline keyboard callbacks."""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Pattern, TYPE_CHECKING

from telegram import CallbackQuery

if TYPE_CHECKING:
    from telegram import Bot

logger = logging.getLogger(__name__)

CallbackHandler = Callable[[CallbackQuery, "Bot", str], Awaitable[Any]]
FallbackHandler = Callable[[CallbackQuery, "Bot", str], Awaitable[Any]]


@dataclass
class CallbackPattern:
    """Pattern for matching callback queries."""
    pattern: str
    compiled: Optional[Pattern[str]] = None
    handler: Optional[CallbackHandler] = None
    description: str = ""

    def __post_init__(self):
        if self.pattern and ("^" in self.pattern or "$" in self.pattern):
            try:
                self.compiled = re.compile(self.pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{self.pattern}': {e}")

    def matches(self, data: str) -> bool:
        """Check if data matches this pattern."""
        if self.compiled:
            return bool(self.compiled.match(data))
        return data.startswith(self.pattern.rstrip(":").replace("^", ""))


class CallbackRouter:
    """
    Scalable router for inline keyboard callbacks.
    
    Callback data format: {module}:{action}:{subaction}:{value}
    Examples:
        - antispam:toggle:on
        - antispam:spamwatch:toggle:on
        - filters:add:pattern:palabra
        - welcome:edit:text
        - navigation:back:main
    """

    def __init__(self):
        self._handlers: List[CallbackPattern] = []
        self._fallback: Optional[FallbackHandler] = None

    def register(
        self,
        pattern: str,
        handler: CallbackHandler,
        description: str = ""
    ) -> None:
        """Register a handler for a callback pattern."""
        callback_pattern = CallbackPattern(
            pattern=pattern,
            handler=handler,
            description=description or pattern
        )
        self._handlers.append(callback_pattern)
        logger.debug(f"Registered callback handler: {description or pattern}")

    def register_prefix(
        self,
        prefix: str,
        handler: CallbackHandler,
        description: str = ""
    ) -> None:
        """Register a handler for all callbacks starting with a prefix."""
        pattern = f"^{prefix}:"
        self.register(pattern, handler, description or f"Handler for {prefix}")

    def register_exact(
        self,
        callback_data: str,
        handler: CallbackHandler,
        description: str = ""
    ) -> None:
        """Register a handler for exact callback data match."""
        self.register(f"^{re.escape(callback_data)}$", handler, description)

    def set_fallback(self, handler: FallbackHandler) -> None:
        """Set handler for unmatched callbacks."""
        self._fallback = handler

    async def handle(self, callback: "CallbackQuery", bot: "Bot") -> Any:
        """Process a callback query."""
        data = callback.data or ""
        user_id = callback.from_user.id
        chat_id = callback.message.chat.id if callback.message else None

        logger.info(f"Callback received: '{data}' from user {user_id} in chat {chat_id}")

        matched = False
        for handler_pattern in self._handlers:
            if handler_pattern.matches(data):
                matched = True
                if handler_pattern.handler:
                    try:
                        result = await handler_pattern.handler(callback, bot, data)
                        logger.debug(f"Callback '{data}' handled successfully")
                        return result
                    except Exception as e:
                        logger.error(f"Error handling callback '{data}': {e}")
                        await self._answer_callback(
                            callback, 
                            f"⚠️ Error: {str(e)[:100]}"
                        )
                        return

        if not matched and self._fallback:
            try:
                return await self._fallback(callback, bot, data)
            except Exception as e:
                logger.error(f"Error in fallback handler for '{data}': {e}")
                await self._answer_callback(
                    callback,
                    f"⚠️ Error: {str(e)[:100]}"
                )
                return

        await self._answer_callback(callback, "❓ Acción no reconocida")

    async def _answer_callback(
        self,
        callback: CallbackQuery,
        text: str,
        show_alert: bool = False
    ) -> None:
        """Answer the callback query."""
        try:
            await callback.answer(text, show_alert=show_alert)
        except Exception as e:
            logger.debug(f"Could not answer callback: {e}")

    def list_handlers(self) -> Dict[str, str]:
        """List all registered handlers."""
        return {
            p.pattern: p.description for p in self._handlers
        }

    def clear(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
        self._fallback = None

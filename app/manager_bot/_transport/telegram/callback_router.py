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
            result = bool(self.compiled.match(data))
            logger.debug(f"Regex match '{self.pattern}' vs '{data}': {result}")
            return result
        pattern = self.pattern.rstrip("$").lstrip("^")
        if pattern.endswith(":"):
            result = data.startswith(pattern)
            logger.debug(f"Prefix match '{pattern}' vs '{data}': {result}")
            return result
        result = data == pattern or data.startswith(pattern + ":")
        logger.debug(f"Exact/prefix match '{pattern}' vs '{data}': {result}")
        return result

    def matches_with_full_check(self, data: str) -> bool:
        """Check if data matches this pattern with full regex support.
        
        This method ensures full regex matching including end-of-string ($)
        when the pattern contains regex anchors.
        """
        if self.compiled:
            full_pattern = self.pattern
            if not (full_pattern.startswith('^') and full_pattern.endswith('$')):
                if not full_pattern.startswith('^'):
                    full_pattern = '^' + full_pattern
                if not full_pattern.endswith('$'):
                    full_pattern = full_pattern + '$'
                try:
                    compiled = re.compile(full_pattern)
                    result = bool(compiled.match(data))
                    logger.debug(f"Full regex match '{full_pattern}' vs '{data}': {result}")
                    return result
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{full_pattern}': {e}")
            result = bool(self.compiled.match(data))
            logger.debug(f"Regex match '{self.pattern}' vs '{data}': {result}")
            return result
        
        pattern = self.pattern.rstrip("$").lstrip("^")
        if pattern.endswith(":"):
            result = data.startswith(pattern)
            logger.debug(f"Prefix match '{pattern}' vs '{data}': {result}")
            return result
        result = data == pattern or data.startswith(pattern + ":")
        logger.debug(f"Exact/prefix match '{pattern}' vs '{data}': {result}")
        return result


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
        """Register a handler for all callbacks starting with a prefix.
        
        This matches both exact prefix and prefix with suffixes (e.g., "antispam:toggle" 
        and "antispam:toggle:on").
        
        The generated pattern is: ^{prefix}(:.*)?$
        This ensures:
        - Exact match: "antispam" matches "antispam"
        - With suffix: "antispam" matches "antispam:on", "antispam:toggle:on"
        
        Args:
            prefix: The prefix to match against (e.g., "antispam:toggle")
            handler: Callback handler function
            description: Optional description for logging
        """
        escaped_prefix = re.escape(prefix)
        pattern = f"^{escaped_prefix}(:.*)?$"
        self.register(pattern, handler, description or f"Handler for {prefix}")
        logger.debug(f"Registered prefix handler: '{pattern}' -> {description or prefix}")

    def register_callback(
        self,
        callback_key: str,
        handler: CallbackHandler,
        description: str = ""
    ) -> None:
        """Register a handler for a callback that can have optional suffixes.
        
        This is a convenience method that registers a regex pattern matching both
        the exact callback key and any suffixed versions.
        Examples:
            - "antispam:toggle" matches "antispam:toggle" and "antispam:toggle:on"
            - "filters:add" matches "filters:add" and "filters:add:word"
        """
        pattern = f"^{re.escape(callback_key)}(:.*)?$"
        self.register(pattern, handler, description or callback_key)

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
        logger.debug(f"Available handlers ({len(self._handlers)}): {self.list_handlers()}")

        matched = False
        for handler_pattern in self._handlers:
            match_result = handler_pattern.matches(data)
            logger.debug(f"Handler '{handler_pattern.pattern}' (desc: {handler_pattern.description}) vs '{data}': {match_result}")
            if match_result:
                logger.info(f"Handler matched: {handler_pattern.pattern} for callback '{data}'")
                matched = True
                if handler_pattern.handler:
                    try:
                        result = await handler_pattern.handler(callback, bot, data)
                        logger.info(f"Callback '{data}' handled successfully")
                        return result
                    except Exception as e:
                        logger.error(f"Error handling callback '{data}': {e}", exc_info=True)
                        await self._answer_callback(
                            callback, 
                            f"⚠️ Error: {str(e)[:100]}"
                        )
                        return

        if not matched and self._fallback:
            logger.info(f"No exact match, trying fallback handler for '{data}'")
            try:
                return await self._fallback(callback, bot, data)
            except Exception as e:
                logger.error(f"Error in fallback handler for '{data}': {e}", exc_info=True)
                await self._answer_callback(
                    callback,
                    f"⚠️ Error: {str(e)[:100]}"
                )
                return

        logger.warning(f"No handler found for callback: '{data}'")
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

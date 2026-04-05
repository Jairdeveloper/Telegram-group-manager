"""Chat member processor."""

import logging
from typing import Any, Dict

from .base import MessageProcessor, ProcessorResult


logger = logging.getLogger(__name__)


class ChatMemberProcessor(MessageProcessor):
    """Processor for chat member updates."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.telegram_client = context.get("telegram_client")
        self.logger = context.get("logger")

    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process a chat member update."""
        update_id = dispatch.update_id
        chat_id = dispatch.chat_id

        logger.info(f"Chat member update: update_id={update_id}, chat_id={chat_id}")

        return ProcessorResult()

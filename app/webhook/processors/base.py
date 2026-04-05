"""Base classes for message processors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProcessorResult:
    """Result from processing a message."""
    reply: Optional[str] = None
    menu_to_show: Optional[str] = None
    error: Optional[str] = None
    skip_send: bool = False


class MessageProcessor(ABC):
    """Base class for all message processors."""

    @abstractmethod
    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process a message and return the result."""
        pass

    async def _maybe_await(self, result):
        """Await result if it's awaitable."""
        import inspect
        if inspect.isawaitable(result):
            return await result
        return result

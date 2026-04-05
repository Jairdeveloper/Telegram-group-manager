"""Factory for creating message processors."""

from typing import Any, Dict, Type

from .base import MessageProcessor, ProcessorResult
from .callback import CallbackProcessor
from .command import OpsCommandProcessor, EnterpriseCommandProcessor
from .chat_message import ChatMessageProcessor
from .chat_member import ChatMemberProcessor


class ProcessorFactory:
    """Factory for creating message processors based on dispatch kind."""

    _processors: Dict[str, Type[MessageProcessor]] = {
        "callback_query": CallbackProcessor,
        "ops_command": OpsCommandProcessor,
        "enterprise_command": EnterpriseCommandProcessor,
        "chat_message": ChatMessageProcessor,
        "chat_member": ChatMemberProcessor,
        "agent_task": ChatMessageProcessor,
    }

    @classmethod
    def get_processor(
        cls,
        dispatch_kind: str,
        context: Dict[str, Any],
    ) -> MessageProcessor:
        """Get a processor for the given dispatch kind."""
        processor_class = cls._processors.get(
            dispatch_kind,
            ChatMessageProcessor,
        )
        return processor_class(context=context)

    @classmethod
    def register_processor(
        cls,
        dispatch_kind: str,
        processor_class: Type[MessageProcessor],
    ) -> None:
        """Register a custom processor for a dispatch kind."""
        cls._processors[dispatch_kind] = processor_class

    @classmethod
    def get_available_kinds(cls) -> list[str]:
        """Get list of available processor kinds."""
        return list(cls._processors.keys())

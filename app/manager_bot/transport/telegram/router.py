"""Telegram router for ManagerBot."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple

from app.enterprise.transport.dispatcher import is_enterprise_command

if TYPE_CHECKING:
    from app.manager_bot.core import ModuleRegistry
    from app.telegram.models import DispatchResult

logger = logging.getLogger(__name__)

OPS_COMMANDS = {"/health", "/e2e", "/webhookinfo", "/logs"}


def extract_chat_payload(update: Dict[str, Any]) -> Optional[Tuple[int, str]]:
    """Extract (chat_id, text) from a Telegram update."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    chat = message.get("chat")
    if not chat:
        return None
    chat_id = chat.get("id")
    text = message.get("text", "")
    return chat_id, text


def extract_sender_id(update: Dict[str, Any]) -> Optional[int]:
    """Extract sender user ID from a Telegram update."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    user = message.get("from")
    if not user:
        return None
    return user.get("id")


def split_command(text: str) -> Tuple[Optional[str], Tuple[str, ...]]:
    """Split text into command and args."""
    parts = text.strip().split()
    if not parts:
        return None, ()
    cmd = parts[0]
    if not cmd.startswith("/"):
        return None, ()
    args = tuple(parts[1:])
    return cmd, args


DispatchKind = Literal["ops_command", "enterprise_command", "chat_message", "unsupported"]


@dataclass
class RouterDispatchResult:
    """Classification result for a Telegram update."""

    kind: DispatchKind
    update_id: Optional[int]
    chat_id: Optional[int]
    user_id: Optional[int] = None
    text: str = ""
    command: Optional[str] = None
    args: Tuple[str, ...] = ()
    reason: Optional[str] = None
    raw_update: Dict[str, Any] = None

    def __post_init__(self):
        if self.raw_update is None:
            self.raw_update = {}

    def to_legacy_dispatch(self) -> "DispatchResult":
        """Convert to legacy DispatchResult for compatibility."""
        from app.telegram.models import DispatchResult

        return DispatchResult(
            kind=self.kind,
            update_id=self.update_id,
            chat_id=self.chat_id,
            user_id=self.user_id,
            text=self.text,
            command=self.command,
            args=self.args,
            reason=self.reason,
            raw_update=self.raw_update,
        )


class TelegramRouter:
    """Router that classifies and delegates Telegram updates to modules."""

    def __init__(self, registry: "ModuleRegistry"):
        self.registry = registry

    def route_update(self, update: Dict[str, Any]) -> RouterDispatchResult:
        """Classify Telegram update and return routing decision."""
        update_id = update.get("update_id")
        payload = extract_chat_payload(update)
        sender_id = extract_sender_id(update)

        if not payload:
            return RouterDispatchResult(
                kind="unsupported",
                update_id=update_id,
                chat_id=None,
                user_id=sender_id,
                reason="missing_message",
                raw_update=update,
            )

        chat_id, text = payload
        text = (text or "").strip()
        if not text:
            return RouterDispatchResult(
                kind="unsupported",
                update_id=update_id,
                chat_id=chat_id,
                user_id=sender_id,
                reason="missing_text",
                raw_update=update,
            )

        command, args = split_command(text)

        if command in OPS_COMMANDS:
            return RouterDispatchResult(
                kind="ops_command",
                update_id=update_id,
                chat_id=chat_id,
                user_id=sender_id,
                text=text,
                command=command,
                args=args,
                raw_update=update,
            )

        if command is not None and is_enterprise_command(command):
            return RouterDispatchResult(
                kind="enterprise_command",
                update_id=update_id,
                chat_id=chat_id,
                user_id=sender_id,
                text=text,
                command=command,
                args=args,
                raw_update=update,
            )

        if command is not None:
            return RouterDispatchResult(
                kind="unsupported",
                update_id=update_id,
                chat_id=chat_id,
                user_id=sender_id,
                text=text,
                command=command,
                args=args,
                reason="unsupported_command",
                raw_update=update,
            )

        return RouterDispatchResult(
            kind="chat_message",
            update_id=update_id,
            chat_id=chat_id,
            user_id=sender_id,
            text=text,
            raw_update=update,
        )

    def get_module_for_dispatch(
        self, dispatch: RouterDispatchResult
    ) -> Optional[Any]:
        """Get the appropriate module for a dispatch result."""
        module_mapping = {
            "ops_command": "ops",
            "enterprise_command": "enterprise",
            "chat_message": "enterprise",
        }

        module_name = module_mapping.get(dispatch.kind)
        if module_name:
            return self.registry.get_module(module_name)
        return None

    def get_handler_for_command(
        self, command: str
    ) -> Optional[Any]:
        """Get handler for a specific command from any enabled module."""
        for module in self.registry.list_enabled_modules():
            handlers = module.get_handlers()
            if command in handlers:
                return handlers[command]
        return None

    def list_available_commands(self) -> List[str]:
        """List all available commands from enabled modules."""
        commands = []
        for module in self.registry.list_enabled_modules():
            handlers = module.get_handlers()
            commands.extend(handlers.keys())
        return commands

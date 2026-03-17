"""PTB adapter for ManagerBot using robot_ptb_compat handlers."""

from __future__ import annotations

from typing import Any, Callable, Iterable, List, Optional

from robot_ptb_compat.compat.handlers import CallbackAdapter, CommandAdapter

try:
    from telegram.ext import CallbackQueryHandler, CommandHandler
    HAS_TELEGRAM_EXT = True
except ImportError:  # pragma: no cover
    HAS_TELEGRAM_EXT = False
    CallbackQueryHandler = None
    CommandHandler = None


class ManagerBotPtbAdapter:
    """Bridge ManagerBot registry to PTB handlers via robot_ptb_compat adapters."""

    def __init__(self, manager_bot: Any, process_update: Callable[[dict], Any]):
        self._manager_bot = manager_bot
        self._process_update = process_update
        self._command_adapter: Optional[CommandAdapter] = None
        self._callback_adapter: Optional[CallbackAdapter] = None

    def _collect_commands(self) -> List[str]:
        commands: List[str] = []
        for module in self._manager_bot.registry.list_enabled_modules():
            for command in module.get_handlers().keys():
                if not command.startswith("/"):
                    continue
                commands.append(command.lstrip("/").lower())
        return sorted(set(commands))

    async def _handle_update(self, update: Any, context: Any) -> Any:
        """Handle PTB update by converting to internal dict and delegating."""
        from robot_ptb_compat.bridge import UpdateBridge

        internal = UpdateBridge.to_internal(update)
        if not internal:
            return None
        return await self._process_update(internal)

    def build_adapters(self) -> tuple[CommandAdapter, CallbackAdapter]:
        commands = self._collect_commands()
        self._command_adapter = CommandAdapter(
            commands=commands,
            callback=self._handle_update,
        )
        self._callback_adapter = CallbackAdapter(
            callback=self._handle_update,
        )
        return self._command_adapter, self._callback_adapter

    def register(self, application: Any) -> None:
        """Register adapters into PTB application or fallback runtime."""
        command_adapter, callback_adapter = self.build_adapters()

        if HAS_TELEGRAM_EXT and CommandHandler and CallbackQueryHandler:
            async def _command_wrapper(update, context):
                return await command_adapter.handle(update, context)

            async def _callback_wrapper(update, context):
                return await callback_adapter.handle(update, context)

            commands = command_adapter.get_commands()
            if commands:
                command_handler = CommandHandler(commands, _command_wrapper)
                application.add_handler(command_handler)
            callback_handler = CallbackQueryHandler(_callback_wrapper)
            application.add_handler(callback_handler)
        else:
            application.add_handler(command_adapter)
            application.add_handler(callback_adapter)

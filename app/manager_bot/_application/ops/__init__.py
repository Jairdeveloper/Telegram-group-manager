"""OPS module for ManagerBot."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence

from app.manager_bot.core import Module, ModuleContract

OPS_COMMANDS_LIST = [
    "/health",
    "/e2e",
    "/webhookinfo",
    "/logs",
]


@dataclass
class OpsCommand:
    name: str
    handler: Callable
    description: str
    admin_only: bool = True


def get_ops_commands() -> List[OpsCommand]:
    """Get all OPS commands with their handlers."""
    from app.ops.services import (
        execute_e2e_command,
        handle_ops_command,
    )
    from app.ops.policies import check_rate_limit, is_admin
    from app.ops.events import get_event_store, record_event
    from app.ops import checks as ops_checks

    async def health_handler(chat_id: int, args: Sequence[str]) -> Dict[str, Any]:
        return await handle_ops_command(
            chat_id,
            "/health",
            args,
            is_admin_fn=is_admin,
            check_api_health_fn=ops_checks.check_api_health,
            check_webhook_health_fn=ops_checks.check_webhook_health,
            record_event_fn=record_event,
        )

    async def e2e_handler(chat_id: int, args: Sequence[str]) -> Dict[str, Any]:
        return await execute_e2e_command(
            chat_id,
            rate_limit_check=check_rate_limit,
            run_e2e_check_fn=ops_checks.run_e2e_check,
            record_event_fn=record_event,
        )

    async def webhookinfo_handler(chat_id: int, args: Sequence[str]) -> Dict[str, Any]:
        return await handle_ops_command(
            chat_id,
            "/webhookinfo",
            args,
            is_admin_fn=is_admin,
            get_webhook_info_fn=ops_checks.get_webhook_info,
            record_event_fn=record_event,
        )

    async def logs_handler(chat_id: int, args: Sequence[str]) -> Dict[str, Any]:
        return await handle_ops_command(
            chat_id,
            "/logs",
            args,
            is_admin_fn=is_admin,
            get_event_store_fn=get_event_store,
            record_event_fn=record_event,
        )

    return [
        OpsCommand("/health", health_handler, "Estado de API y Webhook", admin_only=True),
        OpsCommand("/e2e", e2e_handler, "Ejecutar checks E2E", admin_only=True),
        OpsCommand("/webhookinfo", webhookinfo_handler, "Info de webhook", admin_only=True),
        OpsCommand("/logs", logs_handler, "Últimos eventos", admin_only=True),
    ]


class OpsModule(Module):
    """OPS module for ManagerBot - handles operational commands."""

    def __init__(self):
        self._commands = get_ops_commands()

    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="ops",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_OPS",
            routes=OPS_COMMANDS_LIST,
            permissions=["admin"],
        )

    def is_enabled(self) -> bool:
        import os

        return os.getenv("MANAGER_ENABLE_OPS", "true").lower() == "true"

    def get_handlers(self) -> Dict[str, Callable]:
        return {cmd.name: cmd.handler for cmd in self._commands}

    def get_command_descriptions(self) -> Dict[str, str]:
        return {cmd.name: cmd.description for cmd in self._commands}

    def is_admin_command(self, command: str) -> bool:
        for cmd in self._commands:
            if cmd.name == command:
                return cmd.admin_only
        return False

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "module": "ops",
            "commands": OPS_COMMANDS_LIST,
        }

"""Enterprise module for ManagerBot."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence

from app.manager_bot.core import Module, ModuleContract

ENTERPRISE_COMMANDS_LIST = [
    "/config",
    "/adminhelp",
    "/antichannel",
    "/antispam",
    "/anilist",
    "/ban",
    "/blacklist",
    "/delnote",
    "/fun",
    "/gettime",
    "/unban",
    "/filter",
    "/note",
    "/notes",
    "/reactions",
    "/rules",
    "/setnote",
    "/setrules",
    "/setwelcome",
    "/stickerblacklist",
    "/user",
    "/users",
    "/welcome",
    "/wallpaper",
    "/whoami",
]


@dataclass
class EnterpriseCommand:
    name: str
    handler: Callable
    description: str
    required_permissions: List[str]


class EnterpriseModule(Module):
    """Enterprise module for ManagerBot - handles enterprise commands."""

    def __init__(self):
        self._commands = self._get_commands()
        self._menu_engine = None
        self._config_storage = None

    def _config_handler(
        self,
        chat_id: int,
        args: Sequence[str],
        user_id: int,
        raw_text: str,
        raw_update: Dict,
    ) -> Dict[str, Any]:
        return {
            "status": "menu",
            "menu_id": "main",
        }

    def _get_commands(self) -> List[EnterpriseCommand]:
        """Get all Enterprise commands with their handlers."""
        from app.enterprise.transport.handlers import (
            handle_enterprise_command,
            handle_enterprise_moderation,
        )

        async def enterprise_handler(
            chat_id: int, args: Sequence[str], user_id: int, raw_text: str, raw_update: Dict
        ) -> Dict[str, Any]:
            return handle_enterprise_command(
                actor_id=user_id,
                chat_id=chat_id,
                command=args[0] if args else "",
                args=args[1:] if args else (),
                raw_text=raw_text,
                raw_update=raw_update,
            )

        async def moderation_handler(
            chat_id: int, args: Sequence[str], user_id: int, raw_text: str, raw_update: Dict
        ) -> Dict[str, Any]:
            return handle_enterprise_moderation(
                actor_id=user_id,
                chat_id=chat_id,
                raw_text=raw_text,
                raw_update=raw_update,
            )

        return [
            EnterpriseCommand(
                "/config", self._config_handler, "Menú de configuración", ["admin"]
            ),
            EnterpriseCommand(
                "/adminhelp", enterprise_handler, "Ayuda de comandos admin", ["admin"]
            ),
            EnterpriseCommand(
                "/antichannel", enterprise_handler, "Configurar anticanal", ["admin"]
            ),
            EnterpriseCommand(
                "/antispam", enterprise_handler, "Configurar antispam", ["admin"]
            ),
            EnterpriseCommand("/anilist", enterprise_handler, "Buscar anime", ["user"]),
            EnterpriseCommand("/ban", enterprise_handler, "Banear usuario", ["admin"]),
            EnterpriseCommand(
                "/blacklist", enterprise_handler, "Blacklist de patrones", ["admin"]
            ),
            EnterpriseCommand(
                "/delnote", enterprise_handler, "Eliminar nota", ["admin"]
            ),
            EnterpriseCommand("/fun", enterprise_handler, "Modo fun", ["user"]),
            EnterpriseCommand("/gettime", enterprise_handler, "Obtener hora", ["user"]),
            EnterpriseCommand("/unban", enterprise_handler, "Desbanear", ["admin"]),
            EnterpriseCommand("/filter", enterprise_handler, "Filtros de contenido", ["admin"]),
            EnterpriseCommand("/note", enterprise_handler, "Ver nota", ["user"]),
            EnterpriseCommand("/notes", enterprise_handler, "Listar notas", ["user"]),
            EnterpriseCommand(
                "/reactions", enterprise_handler, "Reacciones automáticas", ["user"]
            ),
            EnterpriseCommand("/rules", enterprise_handler, "Ver reglas", ["user"]),
            EnterpriseCommand("/setnote", enterprise_handler, "Establecer nota", ["admin"]),
            EnterpriseCommand("/setrules", enterprise_handler, "Establecer reglas", ["admin"]),
            EnterpriseCommand(
                "/setwelcome", enterprise_handler, "Establecer bienvenida", ["admin"]
            ),
            EnterpriseCommand(
                "/stickerblacklist",
                enterprise_handler,
                "Blacklist de stickers",
                ["admin"],
            ),
            EnterpriseCommand("/user", enterprise_handler, "Gestión de usuarios", ["admin"]),
            EnterpriseCommand("/users", enterprise_handler, "Listar usuarios", ["admin"]),
            EnterpriseCommand("/welcome", enterprise_handler, "Ver bienvenida", ["user"]),
            EnterpriseCommand("/wallpaper", enterprise_handler, "Wallpaper", ["user"]),
            EnterpriseCommand("/whoami", enterprise_handler, "Mi rol", ["user"]),
            EnterpriseCommand(
                "_moderation",
                moderation_handler,
                "Moderación de mensajes",
                ["user"],
            ),
        ]

    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="enterprise",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_ENTERPRISE",
            routes=ENTERPRISE_COMMANDS_LIST + ["_moderation"],
            permissions=["user", "admin"],
        )

    def is_enabled(self) -> bool:
        import os

        return os.getenv("MANAGER_ENABLE_ENTERPRISE", "true").lower() == "true"

    def get_handlers(self) -> Dict[str, Callable]:
        return {cmd.name: cmd.handler for cmd in self._commands}

    def get_command_descriptions(self) -> Dict[str, str]:
        return {cmd.name: cmd.description for cmd in self._commands}

    def get_required_permissions(self, command: str) -> List[str]:
        for cmd in self._commands:
            if cmd.name == command:
                return cmd.required_permissions
        return []

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "module": "enterprise",
            "commands": ENTERPRISE_COMMANDS_LIST,
        }

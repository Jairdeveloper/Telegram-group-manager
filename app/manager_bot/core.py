"""Core module for ManagerBot."""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ModuleContract(BaseModel):
    """Contrato que define la estructura de un módulo."""

    name: str
    version: str
    feature_flag: str
    routes: List[str]
    permissions: List[str]


class Module:
    """Interfaz base que deben implementar todos los módulos."""

    @property
    def contract(self) -> ModuleContract:
        """Retornar el contrato del módulo."""
        raise NotImplementedError

    def is_enabled(self) -> bool:
        """Verificar si el módulo está habilitado via feature flag."""
        return os.getenv(self.contract.feature_flag, "false").lower() == "true"

    def get_handlers(self) -> Dict[str, Callable]:
        """Devolver handlers del módulo."""
        raise NotImplementedError

    def get_required_permissions(self, command: str) -> List[str]:
        """Obtener permisos requeridos para un comando."""
        return self.contract.permissions

    def health_check(self) -> Dict[str, Any]:
        """Health check opcional del módulo."""
        return {"status": "ok", "module": self.contract.name}


class ManagerBot:
    """ManagerBot - Unified bot dispatcher with module registry."""

    def __init__(self):
        from app.manager_bot.registry import ModuleRegistry

        self.registry = ModuleRegistry()
        self._app = None
        self._router = None
        self._register_core_modules()

    def _register_core_modules(self):
        """Registrar módulos base del ManagerBot."""
        from app.manager_bot.application.ops import OpsModule
        from app.manager_bot.application.enterprise import EnterpriseModule
        from app.manager_bot.application.agent import AgentModule

        ops_module = OpsModule()
        self.registry.register(ops_module)
        logger.info(f"Registered OPS module (enabled: {ops_module.is_enabled()})")

        enterprise_module = EnterpriseModule()
        self.registry.register(enterprise_module)
        logger.info(f"Registered Enterprise module (enabled: {enterprise_module.is_enabled()})")

        agent_module = AgentModule()
        self.registry.register(agent_module)
        logger.info(f"Registered Agent module (enabled: {agent_module.is_enabled()})")

    def register_module(self, module: Module) -> None:
        """Registrar un módulo en el registry."""
        self.registry.register(module)
        logger.info(
            f"Registered module: {module.contract.name} "
            f"(version: {module.contract.version})"
        )

    def get_module(self, name: str) -> Optional[Module]:
        """Obtener módulo por nombre."""
        return self.registry.get_module(name)

    def is_module_enabled(self, name: str) -> bool:
        """Verificar si un módulo está habilitado."""
        return self.registry.is_enabled(name)

    def get_app(self):
        """Obtener la aplicación FastAPI."""
        if self._app is None:
            from fastapi import FastAPI

            self._app = FastAPI(
                title="ManagerBot",
                description="Unified bot dispatcher with module registry",
                version="1.0.0",
            )
            self._setup_routes()
        return self._app

    def get_router(self):
        """Obtener el router de Telegram."""
        if self._router is None:
            from app.manager_bot.transport.telegram.router import TelegramRouter

            self._router = TelegramRouter(self.registry)
        return self._router

    def _setup_routes(self):
        """Configurar rutas base."""
        from fastapi import FastAPI

        app = self.get_app()

        @app.get("/health")
        async def health():
            return {"status": "ok", "manager_bot": "ready"}

        @app.get("/manager/health")
        async def manager_health():
            modules_health = {}
            for module in self.registry.list_enabled_modules():
                try:
                    modules_health[module.contract.name] = module.health_check()
                except Exception as e:
                    modules_health[module.contract.name] = {
                        "status": "error",
                        "error": str(e),
                    }
            return {
                "status": "ok",
                "modules": modules_health,
                "enabled_modules": [
                    m.contract.name for m in self.registry.list_enabled_modules()
                ],
            }

    def list_commands(self) -> Dict[str, List[str]]:
        """Listar todos los comandos disponibles por módulo."""
        commands = {}
        for module in self.registry.list_enabled_modules():
            handlers = module.get_handlers()
            commands[module.contract.name] = list(handlers.keys())
        return commands

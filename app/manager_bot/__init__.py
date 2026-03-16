"""ManagerBot - Unified bot dispatcher with module registry."""

from app.manager_bot.core import ManagerBot
from app.manager_bot.core import Module
from app.manager_bot.core import ModuleContract
from app.manager_bot.registry import ModuleRegistry
from app.manager_bot._application.ops import OpsModule
from app.manager_bot._application.enterprise import EnterpriseModule
from app.manager_bot._application.agent import AgentModule
from app.manager_bot._application.agent.gateway import AgentGateway

__all__ = [
    "ManagerBot",
    "Module",
    "ModuleContract",
    "ModuleRegistry",
    "OpsModule",
    "EnterpriseModule",
    "AgentModule",
    "AgentGateway",
]

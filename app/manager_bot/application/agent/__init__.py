"""Agent module for ManagerBot."""

from typing import Any, Callable, Dict, List, Optional

from app.manager_bot.core import Module, ModuleContract

from .gateway import AgentGateway


class AgentModule(Module):
    """Agent module that delegates to external Agent service."""

    def __init__(self, gateway: Optional[AgentGateway] = None):
        self._gateway = gateway or AgentGateway()

    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="agent",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_AGENT",
            routes=["/agent/chat"],
            permissions=["user"],
        )

    def is_enabled(self) -> bool:
        import os

        return os.getenv("MANAGER_ENABLE_AGENT", "false").lower() == "true"

    def get_handlers(self) -> Dict[str, Callable]:
        return {
            "/agent/chat": self._handle_chat,
        }

    async def _handle_chat(
        self, chat_id: int, args: tuple, user_id: Optional[int] = None, text: str = ""
    ) -> Dict[str, Any]:
        """Handle chat message via Agent service."""
        return await self._gateway.chat(
            message=text,
            session_id=str(chat_id),
            context={"user_id": user_id} if user_id else {},
        )

    def get_gateway(self) -> AgentGateway:
        """Get the agent gateway."""
        return self._gateway

    def get_required_permissions(self, command: str) -> List[str]:
        return ["user"]

    def health_check(self) -> Dict[str, Any]:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return {
                    "status": "ok",
                    "module": "agent",
                    "gateway_configured": self._gateway.is_available(),
                    "note": "Use /agent/chat for async health check",
                }
            else:
                is_healthy = asyncio.run(self._gateway.health_check())
                return {
                    "status": "ok" if is_healthy else "degraded",
                    "module": "agent",
                    "service_available": is_healthy,
                    "gateway_configured": self._gateway.is_available(),
                }
        except Exception as e:
            return {
                "status": "error",
                "module": "agent",
                "error": str(e),
                "gateway_configured": self._gateway.is_available(),
            }

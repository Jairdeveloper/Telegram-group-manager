from __future__ import annotations

from typing import Any, Dict

from app.manager_bot.services import GroupConfigService

from .types import ActionContext


class ActionStateProvider:
    def __init__(self, config_service: GroupConfigService | None = None):
        self._config_service = config_service or GroupConfigService()

    async def get_state(self, action_id: str, context: ActionContext) -> Dict[str, Any]:
        config = await self._config_service.get_or_create(
            chat_id=context.chat_id,
            tenant_id=context.tenant_id,
        )
        if action_id == "welcome.toggle":
            return {"welcome_enabled": config.welcome_enabled}
        if action_id == "welcome.set_text":
            return {"welcome_text": config.welcome_text, "welcome_enabled": config.welcome_enabled}
        if action_id == "antispam.toggle":
            return {"antispam_enabled": config.antispam_enabled}
        return {}

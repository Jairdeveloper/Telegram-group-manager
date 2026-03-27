from __future__ import annotations

from typing import Callable, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage, get_config_storage


class GroupConfigService:
    def __init__(self, config_storage: Optional[ConfigStorage] = None):
        self._storage = config_storage or get_config_storage()

    async def get_or_create(self, chat_id: int, tenant_id: str) -> GroupConfig:
        config = await self._storage.get(chat_id)
        if config is None:
            config = GroupConfig.create_default(chat_id=chat_id, tenant_id=tenant_id)
            await self._storage.set(config)
        return config

    async def update(
        self,
        *,
        chat_id: int,
        tenant_id: str,
        updated_by: Optional[int],
        updater: Callable[[GroupConfig], None],
    ) -> GroupConfig:
        config = await self.get_or_create(chat_id=chat_id, tenant_id=tenant_id)
        updater(config)
        config.update_timestamp(updated_by)
        await self._storage.set(config)
        return config

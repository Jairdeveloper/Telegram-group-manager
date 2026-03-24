"""Reports configuration service."""

from enum import Enum
from typing import List, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage


class DestinationType(Enum):
    """Report destination types."""
    NINGUNO = "ninguno"
    FUNDADOR = "fundador"
    GRUPO_STAFF = "grupo_staff"


class ReportsConfigService:
    """Service for managing report destination configuration."""

    VALID_DESTINATIONS = {d.value for d in DestinationType}

    def __init__(self, config_storage: ConfigStorage):
        self._config_storage = config_storage

    async def get_destination(self, chat_id: int) -> DestinationType:
        """Get the current destination configuration for a chat."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return DestinationType.NINGUNO

        dest = config.report_destination or "ninguno"
        if dest not in self.VALID_DESTINATIONS:
            dest = "ninguno"

        return DestinationType(dest)

    async def set_destination(
        self,
        chat_id: int,
        destination: DestinationType,
    ) -> bool:
        """Set the destination configuration for a chat."""
        config = await self._config_storage.get(chat_id)
        if not config:
            config = GroupConfig.create_default(
                chat_id=chat_id,
                tenant_id="default"
            )

        config.report_destination = destination.value
        await self._config_storage.set(config)
        return True

    async def is_enabled(self, chat_id: int) -> bool:
        """Check if report destination is enabled."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return True

        return getattr(config, "report_destination_enabled", True)

    async def set_enabled(self, chat_id: int, enabled: bool) -> bool:
        """Enable or disable report destination feature."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return False

        config.report_destination_enabled = enabled
        await self._config_storage.set(config)
        return True

    async def get_destination_recipients(
        self,
        chat_id: int,
        founder_id: Optional[int] = None,
        staff_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Resolve the list of recipient user IDs based on destination config.
        
        Args:
            chat_id: The chat ID
            founder_id: Optional founder user ID
            staff_ids: Optional list of staff user IDs
            
        Returns:
            List of user IDs that should receive reports
        """
        destination = await self.get_destination(chat_id)
        enabled = await self.is_enabled(chat_id)

        if not enabled:
            return []

        if destination == DestinationType.NINGUNO:
            return []

        if destination == DestinationType.FUNDADOR:
            return [founder_id] if founder_id else []

        if destination == DestinationType.GRUPO_STAFF:
            return staff_ids if staff_ids else []

        return []

    def validate_destination(self, value: str) -> bool:
        """Validate if a destination value is valid."""
        return value in self.VALID_DESTINATIONS
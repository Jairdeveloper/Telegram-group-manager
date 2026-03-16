"""Base feature module for ManagerBot."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._menus.base import MenuDefinition

if TYPE_CHECKING:
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class FeatureModule(ABC):
    """
    Base class for feature modules.
    
    Each feature (antispam, filters, welcome, etc.) should inherit from this
    and implement the required methods to provide menu definitions and
    callback handlers.
    """

    MENU_ID: str = ""
    FEATURE_NAME: str = ""

    def __init__(self, config_storage: ConfigStorage):
        self.config_storage = config_storage

    @abstractmethod
    def register_callbacks(self, router: "CallbackRouter") -> None:
        """
        Register all callback handlers for this feature.
        
        Args:
            router: The callback router to register handlers with.
        """
        pass

    def get_menu_definition(
        self, 
        chat_id: int, 
        config: Optional[GroupConfig] = None
    ) -> MenuDefinition:
        """
        Get the menu definition for this feature.
        
        Default implementation tries to import from menus module.
        Override this in subclasses for custom menus.
        """
        from app.manager_bot._menus import main_menu
        
        menu_id = self.MENU_ID.replace("mod:", "")
        
        try:
            if menu_id == "antispam":
                from app.manager_bot._menus.antispam_menu import create_antispam_menu
                return create_antispam_menu(config)
            elif menu_id == "filters":
                from app.manager_bot._menus.filters_menu import create_filters_menu
                return create_filters_menu(config)
            elif menu_id == "welcome":
                from app.manager_bot._menus.welcome_menu import create_welcome_menu
                return create_welcome_menu(config)
            elif menu_id == "goodbye":
                from app.manager_bot._menus.welcome_menu import create_goodbye_menu
                return create_goodbye_menu(config)
            elif menu_id == "mod" or menu_id == "moderation":
                from app.manager_bot._menus.moderation_menu import create_moderation_menu
                return create_moderation_menu(config)
        except ImportError:
            pass
        
        return MenuDefinition(
            menu_id=self.MENU_ID,
            title=f"{self.FEATURE_NAME} Settings"
        )

    async def get_config(self, chat_id: int) -> Optional[GroupConfig]:
        """Get configuration for a chat."""
        return await self.config_storage.get(chat_id)

    async def update_config(
        self, 
        config: GroupConfig, 
        user_id: Optional[int] = None
    ) -> None:
        """Update configuration for a chat."""
        config.update_timestamp(user_id)
        await self.config_storage.set(config)

    async def create_default_config(
        self, 
        chat_id: int, 
        tenant_id: str
    ) -> GroupConfig:
        """Create default configuration for a new chat."""
        config = GroupConfig.create_default(chat_id, tenant_id)
        await self.config_storage.set(config)
        return config

    def get_feature_toggle_status(
        self, 
        config: GroupConfig
    ) -> Dict[str, bool]:
        """
        Get the toggle status for all features in this module.
        
        Override this in subclasses to return specific status.
        """
        return {}

    @property
    def feature_id(self) -> str:
        """Get the feature identifier."""
        return self.MENU_ID or self.__class__.__name__.lower().replace("feature", "")

"""Menu registry for ManagerBot."""

from typing import Callable, Dict, List, Optional, Union, TYPE_CHECKING

from app.manager_bot._menus.base import MenuDefinition

if TYPE_CHECKING:
    from app.manager_bot._config.group_config import GroupConfig

MenuFactory = Callable[[Optional["GroupConfig"]], MenuDefinition]
MenuProvider = Union[MenuDefinition, MenuFactory]


class MenuRegistry:
    """Central registry for menu definitions."""

    def __init__(self):
        self._menus: Dict[str, MenuProvider] = {}

    def register(self, menu: MenuProvider) -> None:
        """Register a menu definition or factory."""
        if callable(menu):
            menu_def = menu(None)
            menu_id = menu_def.menu_id
            if menu_id in self._menus:
                raise ValueError(f"Menu '{menu_id}' is already registered")
            self._menus[menu_id] = menu
            return

        if menu.menu_id in self._menus:
            raise ValueError(f"Menu '{menu.menu_id}' is already registered")
        self._menus[menu.menu_id] = menu

    def get(self, menu_id: str, config: Optional["GroupConfig"] = None) -> Optional[MenuDefinition]:
        """Get a menu by ID (builds from factory if needed)."""
        provider = self._menus.get(menu_id)
        if provider is None:
            return None
        if callable(provider):
            return provider(config)
        return provider

    def unregister(self, menu_id: str) -> bool:
        """Unregister a menu by ID."""
        if menu_id in self._menus:
            del self._menus[menu_id]
            return True
        return False

    def list_menus(self) -> List[str]:
        """List all registered menu IDs."""
        return list(self._menus.keys())

    def clear(self) -> None:
        """Clear all registered menus."""
        self._menus.clear()

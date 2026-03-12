"""Menu registry for ManagerBot."""

from typing import Dict, List, Optional

from app.manager_bot.menus.base import MenuDefinition


class MenuRegistry:
    """Central registry for menu definitions."""

    def __init__(self):
        self._menus: Dict[str, MenuDefinition] = {}

    def register(self, menu: MenuDefinition) -> None:
        """Register a menu definition."""
        if menu.menu_id in self._menus:
            raise ValueError(f"Menu '{menu.menu_id}' is already registered")
        self._menus[menu.menu_id] = menu

    def get(self, menu_id: str) -> Optional[MenuDefinition]:
        """Get a menu by ID."""
        return self._menus.get(menu_id)

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

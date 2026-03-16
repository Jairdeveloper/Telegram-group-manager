"""Reports menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_reports_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the reports settings menu."""
    menu = MenuDefinition(
        menu_id="reports",
        title="📊 Centro de Reportes",
        parent_menu="main",
    )

    menu.add_row().add_action(
        "reports:list:open",
        "📋 Reportes abiertos",
        "📋"
    )

    menu.add_row().add_action(
        "reports:list:resolved",
        "✅ Reportes resueltos",
        "✅"
    )

    menu.add_row().add_action(
        "reports:stats",
        "📈 Estadísticas",
        "📈"
    )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu

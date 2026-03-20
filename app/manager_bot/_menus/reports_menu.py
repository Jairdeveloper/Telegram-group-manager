"""Reports menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.rendering import build_title


def create_reports_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the reports settings menu."""
    title = build_title("Centro de Reportes")
    menu = MenuDefinition(
        menu_id="reports",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action(
        "reports:list:open",
        "Reportes abiertos",
    )

    menu.add_row().add_action(
        "reports:list:resolved",
        "Reportes resueltos",
    )

    menu.add_row().add_action(
        "reports:stats",
        "Estadisticas",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

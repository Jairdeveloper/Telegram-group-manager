"""Filters menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_filters_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the filters management menu."""
    menu = MenuDefinition(
        menu_id="filters",
        title="🔤 Gestión de Filtros",
        parent_menu="main",
    )

    filter_count = len(config.filters) if config else 0
    menu.add_row().add_action(
        "filters:add",
        f"➕ Agregar Filtro ({filter_count} activos)",
        "➕"
    )

    menu.add_row().add_action(
        "filters:list",
        "📋 Lista de Filtros",
        "📋"
    )

    blocked_count = len(config.blocked_words) if config else 0
    menu.add_row().add_action(
        "filters:words:show",
        f"🔇 Palabras Bloqueadas ({blocked_count})",
        "🔇"
    )

    menu.add_row().add_action(
        "filters:sticker:show",
        "🖼️ Sticker Blacklist",
        "🖼️"
    )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_filters_list_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the filters list menu."""
    menu = MenuDefinition(
        menu_id="filters:list",
        title="📋 Lista de Filtros",
        parent_menu="filters",
    )

    filters = config.filters if config else []
    if filters:
        for f in filters[:10]:
            pattern = f.get("pattern", "unknown")
            menu.add_row().add_action(
                f"filters:del:{pattern}",
                f"❌ {pattern[:20]}",
                "❌"
            )
        
        if len(filters) > 10:
            menu.add_row().add_action("filters:page:1", f"📄 Más ({len(filters) - 10})", "📄")
    else:
        menu.add_row().add_action("filters:add", "➕ Agregar primer filtro", "➕")

    menu.add_row().add_action("nav:back:filters", "🔙 Volver", "🔙")

    return menu


def create_blocked_words_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the blocked words management menu."""
    menu = MenuDefinition(
        menu_id="filters:words",
        title="🔇 Palabras Bloqueadas",
        parent_menu="filters",
    )

    words = config.blocked_words if config else []
    if words:
        for word in words[:10]:
            menu.add_row().add_action(
                f"filters:words:del:{word}",
                f"❌ {word}",
                "❌"
            )
        
        if len(words) > 10:
            menu.add_row().add_action("filters:words:page:1", f"📄 Más ({len(words) - 10})", "📄")
    else:
        menu.add_row().add_action("filters:words:add", "➕ Agregar palabra", "➕")

    menu.add_row().add_action("nav:back:filters", "🔙 Volver", "🔙")

    return menu


def create_sticker_blacklist_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the sticker blacklist menu."""
    menu = MenuDefinition(
        menu_id="filters:sticker",
        title="🖼️ Sticker Blacklist",
        parent_menu="filters",
    )

    menu.add_row().add_action("filters:sticker:add", "➕ Agregar sticker", "➕")
    menu.add_row().add_action("filters:sticker:list", "📋 Ver blacklist", "📋")
    menu.add_row().add_action("nav:back:filters", "🔙 Volver", "🔙")

    return menu

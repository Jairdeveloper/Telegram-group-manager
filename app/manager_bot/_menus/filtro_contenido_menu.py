"""Filtro de Contenido menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.rendering import build_title, build_section


def create_filtro_contenido_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the filters management menu."""
    filter_count = len(config.filters) if config else 0
    blocked_count = len(config.blocked_words) if config else 0
    title = build_title(
        "Filtros de Contenido",
        [
            build_section("Filtros activos", str(filter_count)),
            build_section("Palabras bloqueadas", str(blocked_count)),
        ],
    )

    menu = MenuDefinition(
        menu_id="filtro_contenido",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action(
        "filtro_contenido:add",
        "Agregar filtro",
    )

    menu.add_row().add_action(
        "filtro_contenido:list",
        "Lista de filtros",
    )

    menu.add_row().add_action(
        "filtro_contenido:words:show",
        f"Palabras Bloqueadas ({blocked_count})",
    )

    menu.add_row().add_action(
        "filtro_contenido:sticker:show",
        "Sticker blacklist",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_filtro_contenido_list_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the filters list menu."""
    menu = MenuDefinition(
        menu_id="filtro_contenido:list",
        title="Lista de Filtros",
        parent_menu="filtro_contenido",
    )

    filters = config.filters if config else []
    if filters:
        for f in filters[:10]:
            pattern = f.get("pattern", "unknown")
            menu.add_row().add_action(
                f"filtro_contenido:del:{pattern}",
                f"Eliminar: {pattern[:20]}",
            )

        if len(filters) > 10:
            menu.add_row().add_action("filtro_contenido:page:1", f"Mas ({len(filters) - 10})")
    else:
        menu.add_row().add_action("filtro_contenido:add", "Agregar primer filtro")

    menu.add_row().add_action("nav:back:filtro_contenido", "Volver")

    return menu


def create_filtro_contenido_words_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the blocked words management menu."""
    menu = MenuDefinition(
        menu_id="filtro_contenido:words",
        title="Palabras Bloqueadas",
        parent_menu="filtro_contenido",
    )

    words = config.blocked_words if config else []
    if words:
        for word in words[:10]:
            menu.add_row().add_action(
                f"filtro_contenido:words:del:{word}",
                f"Eliminar: {word}",
            )

        if len(words) > 10:
            menu.add_row().add_action("filtro_contenido:words:page:1", f"Mas ({len(words) - 10})")
    else:
        menu.add_row().add_action("filtro_contenido:words:add", "Agregar palabra")

    menu.add_row().add_action("nav:back:filtro_contenido", "Volver")

    return menu


def create_filtro_contenido_sticker_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the sticker blacklist menu."""
    menu = MenuDefinition(
        menu_id="filtro_contenido:sticker",
        title="Sticker Blacklist",
        parent_menu="filtro_contenido",
    )

    menu.add_row().add_action("filtro_contenido:sticker:add", "Agregar sticker")
    menu.add_row().add_action("filtro_contenido:sticker:list", "Ver blacklist")
    menu.add_row().add_action("nav:back:filtro_contenido", "Volver")

    return menu

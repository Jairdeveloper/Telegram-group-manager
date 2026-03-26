"""Moderation menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import yes_no, on_off
from app.manager_bot._menus.rendering import build_title, build_section


def create_moderation_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the moderation settings menu."""
    title = build_title("Configuracion de Moderacion")
    menu = MenuDefinition(
        menu_id="mod",
        title=title,
        parent_menu="main",
    )

    antiflood_status = yes_no(config.antiflood_enabled if config else False)
    menu.add_row().add_action(
        f"mod:antiflood:toggle:{'on' if config and config.antiflood_enabled else 'off'}",
        f"Anti-Flood ({antiflood_status})",
    )

    antichannel_status = yes_no(config.antichannel_enabled if config else False)
    antilink_status = yes_no(config.antilink_enabled if config else False)
    menu.add_row()         .add_action("mod:antichannel:show", f"Anti-Canal ({antichannel_status})")         .add_action("mod:antilink:show", f"Anti-Enlaces ({antilink_status})")

    menu.add_row().add_action("mod:media:show", "Moderacion Media")

    blocked_count = len(config.blocked_words) if config else 0
    menu.add_row().add_action(
        "mod:words:show",
        f"Palabras Bloqueadas ({blocked_count})",
    )

    nightmode_status = yes_no(config.nightmode_enabled if config else False)
    menu.add_row().add_action(
        "mod:nightmode:show",
        f"Modo Nocturno ({nightmode_status})",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_antichannel_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the anti-channel settings menu."""
    enabled = config.antichannel_enabled if config else False
    title = build_title(
        "Configuracion Anti-Canal",
        [build_section("Estado", on_off(enabled))],
    )
    menu = MenuDefinition(
        menu_id="mod:antichannel",
        title=title,
        parent_menu="main",
    )

    toggle_label = "Desactivar" if enabled else "Activar"
    menu.add_row().add_action(
        f"mod:antichannel:toggle:{'off' if enabled else 'on'}",
        toggle_label,
    )
    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_blocked_words_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the blocked words menu."""
    total = len(config.blocked_words) if config else 0
    title = build_title(
        "Palabras Bloqueadas",
        [build_section("Total", str(total))],
    )
    menu = MenuDefinition(
        menu_id="mod:words",
        title=title,
        parent_menu="main",
    )

    words = config.blocked_words if config else []
    if words:
        for word in words[:10]:
            menu.add_row().add_action(f"mod:words:del:{word}", f"Eliminar: {word}")

        if len(words) > 10:
            menu.add_row().add_action("mod:words:page:1", f"Mas ({len(words) - 10})")
    else:
        menu.add_row().add_action("mod:words:add", "Agregar palabra")

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

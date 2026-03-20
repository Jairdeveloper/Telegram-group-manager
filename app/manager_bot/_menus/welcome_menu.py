"""Welcome and goodbye menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import on_off, yes_no
from app.manager_bot._menus.rendering import build_title, build_section


def create_welcome_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the welcome settings menu."""
    welcome_enabled = config.welcome_enabled if config else False

    base = (
        "Mensaje de bienvenida\n"
        "Desde este menu puedes configurar un mensaje que se enviara cuando alguien se una al grupo."
    )
    title = build_title(
        base,
        [build_section("Estado", on_off(welcome_enabled))],
    )

    menu = MenuDefinition(
        menu_id="welcome",
        title=title,
        parent_menu="main",
    )

    menu.add_row()         .add_action("welcome:toggle:off", "Desactivar")         .add_action("welcome:toggle:on", "Activar")

    menu.add_row().add_action(
        "welcome:customize:open",
        "Personalizar mensaje",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_welcome_customize_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the welcome customize menu."""
    has_text = bool(config.welcome_text) if config else False
    has_media = bool(config.welcome_media) if config else False

    title = build_title(
        "Personalizar mensaje de bienvenida",
        [
            build_section("Texto", yes_no(has_text)),
            build_section("Multimedia", yes_no(has_media)),
            "Usa los botones para configurar.",
        ],
    )

    menu = MenuDefinition(
        menu_id="welcome_customize",
        title=title,
        parent_menu="welcome",
    )

    menu.add_row().add_action("welcome:text:edit", "Texto")
    menu.add_row().add_action("welcome:media:edit", "Multimedia")
    menu.add_row().add_action("nav:back:welcome", "Volver")

    return menu


def create_goodbye_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the goodbye settings menu."""
    goodbye_enabled = config.goodbye_enabled if config else False
    title = build_title(
        "Configuracion de Despedida",
        [build_section("Estado", on_off(goodbye_enabled))],
    )

    menu = MenuDefinition(
        menu_id="goodbye",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action(
        f"goodbye:toggle:{'on' if goodbye_enabled else 'off'}",
        "Desactivar" if goodbye_enabled else "Activar",
    )

    if goodbye_enabled:
        has_text = bool(config.goodbye_text) if config else False
        menu.add_row().add_action(
            "goodbye:edit:text",
            "Editar texto" if has_text else "Agregar texto",
        )

        if has_text:
            menu.add_row().add_action(
                "goodbye:preview",
                "Previsualizar",
            )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

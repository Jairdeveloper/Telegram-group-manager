"""Welcome and goodbye menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_welcome_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the welcome settings menu."""
    welcome_enabled = config.welcome_enabled if config else False
    status_text = "Activado" if welcome_enabled else "Desactivado"

    title = (
        "Mensaje de bienvenida\n"
        "Desde este menu puedes configurar un mensaje de bienvenida que se enviara cuando alguien se una a este grupo.\n\n"
        f"Estado: {status_text}"
    )

    menu = MenuDefinition(
        menu_id="welcome",
        title=title,
        parent_menu="main",
    )

    menu.add_row() \
        .add_action("welcome:toggle:off", "Desactivar") \
        .add_action("welcome:toggle:on", "Activar")

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

    text_status = "SI" if has_text else "NO"
    media_status = "SI" if has_media else "NO"

    title = (
        "Personalizar mensaje de bienvenida\n"
        f"Texto: {text_status}\n"
        f"Multimedia: {media_status}\n"
        "Usa los botones para configurar."
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
    menu = MenuDefinition(
        menu_id="goodbye",
        title="Configuracion de Despedida",
        parent_menu="main",
    )

    goodbye_enabled = config.goodbye_enabled if config else False
    goodbye_status = "Activada" if goodbye_enabled else "Desactivada"

    menu.add_row().add_action(
        f"goodbye:toggle:{'on' if goodbye_enabled else 'off'}",
        f"{goodbye_status} Despedida",
    )

    if goodbye_enabled:
        has_text = bool(config.goodbye_text) if config else False
        menu.add_row().add_action(
            "goodbye:edit:text",
            f"{'Texto configurado' if has_text else 'Agregar texto'}",
        )

        if has_text:
            menu.add_row().add_action(
                "goodbye:preview",
                "Previsualizar",
            )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

"""Captcha menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import on_off
from app.manager_bot._menus.rendering import build_title, build_section


def create_captcha_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the captcha settings menu."""
    captcha_enabled = config.captcha_enabled if config else False
    current_type = config.captcha_type if config else "button"
    current_timeout = config.captcha_timeout if config else 300

    title = build_title(
        "Configuracion de Captcha",
        [
            build_section("Estado", on_off(captcha_enabled)),
            build_section("Tipo", current_type) if captcha_enabled else "",
            build_section("Timeout", f"{current_timeout}s") if captcha_enabled else "",
        ],
    )

    menu = MenuDefinition(
        menu_id="captcha",
        title=title,
        parent_menu="main",
    )

    toggle_label = "Desactivar" if captcha_enabled else "Activar"
    menu.add_row().add_action(
        f"captcha:toggle:{'off' if captcha_enabled else 'on'}",
        toggle_label,
    )

    if captcha_enabled:
        menu.add_row().add_action(
            f"captcha:type:{current_type}",
            f"Tipo: {current_type}",
        )

        menu.add_row().add_action(
            "captcha:timeout:show",
            f"Timeout: {current_timeout}s",
        )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

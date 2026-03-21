"""Captcha menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


CAPTCHA_MODES = ["button", "presentation", "math", "rules", "quiz"]

CAPTCHA_MODE_LABELS = {
    "button": "Boton",
    "presentation": "Presentacion",
    "math": "Matematicas",
    "rules": "Reglamento",
    "quiz": "Prueba",
}

CAPTCHA_FAIL_ACTIONS = ["kick", "ban", "mute"]

CAPTCHA_FAIL_ACTION_LABELS = {
    "kick": "Kick",
    "ban": "Ban",
    "mute": "Silenciar",
}

CAPTCHA_TIMEOUTS = [
    (15, "15 seg"),
    (30, "30 seg"),
    (60, "1 min"),
    (120, "2 min"),
    (180, "3 min"),
    (300, "5 min"),
    (600, "10 min"),
    (900, "15 min"),
    (1200, "20 min"),
    (1800, "30 min"),
]


def _build_captcha_title(config: Optional[GroupConfig]) -> str:
    """Build the dynamic title for captcha menu."""
    enabled = config.captcha_enabled if config else False
    mode = config.captcha_mode if config else "math"
    timeout = config.captcha_timeout if config else 180
    fail_action = config.captcha_fail_action if config else "kick"
    delete_msg = config.captcha_delete_service_message if config else False

    status_icon = "✅" if enabled else "❌"
    status_text = "Activo" if enabled else "Apagado"
    mode_label = CAPTCHA_MODE_LABELS.get(mode, mode)
    action_label = CAPTCHA_FAIL_ACTION_LABELS.get(fail_action, fail_action)
    delete_label = "Encendido" if delete_msg else "Apagado"

    if timeout < 60:
        time_str = f"{timeout} Segundos"
    elif timeout < 3600:
        time_str = f"{timeout // 60} Minutos"
    else:
        time_str = f"{timeout // 3600} Horas"

    title = (
        "🧠 Captcha\n\n"
        "Al activar el captcha, cuando un usuario ingrese al grupo no podra enviar mensajes "
        "hasta que haya confirmado que no es un robot.\n\n"
        "🕑 Tambien puedes decidir un CASTIGO en caso de que no resuelva el captcha "
        "dentro del tiempo establecido y si se borrara o no el mensaje de servicio.\n\n"
        f"Estado: {status_text} {status_icon}\n"
        f"🕒 Tiempo: {time_str}\n"
        f"⛔️ Castigo: {action_label}\n"
        f"🗂 Modo: {mode_label}\n"
        f"  └ El usuario tendra que resolver un sencillo cuestionario de matematicas.\n"
        f"🗑 Eliminar mensaje de servicio: {delete_label}"
    )

    return title


def create_captcha_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Captcha menu."""
    title = _build_captcha_title(config)

    menu = MenuDefinition(
        menu_id="captcha",
        title=title,
        parent_menu="main",
    )

    toggle_state = "off" if (config and config.captcha_enabled) else "on"
    menu.add_row().add_action(
        f"captcha:toggle:{toggle_state}",
        "Estado",
    )

    menu.add_row().add_action("captcha:mode:show", "Modo")
    menu.add_row().add_action("captcha:time:show", "Tiempo")
    menu.add_row().add_action("captcha:fail_action:show", "Castigo")

    delete_state = "off" if (config and config.captcha_delete_service_message) else "on"
    menu.add_row().add_action(
        f"captcha:delete:toggle:{delete_state}",
        "Eliminar mensaje",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_captcha_mode_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Captcha mode selection submenu."""
    current_mode = config.captcha_mode if config else "math"
    current_label = CAPTCHA_MODE_LABELS.get(current_mode, current_mode)

    title = (
        "Modo de Captcha\n\n"
        f"🗂 Modo actual: {current_label}"
    )

    menu = MenuDefinition(
        menu_id="captcha:mode",
        title=title,
        parent_menu="captcha",
    )

    for mode in CAPTCHA_MODES:
        label = CAPTCHA_MODE_LABELS.get(mode, mode)
        is_current = mode == current_mode
        menu.add_row().add_action(
            f"captcha:mode:{mode}",
            f"[{label}]" if is_current else label,
        )

    menu.add_row().add_action("captcha:show", "Volver")

    return menu


def create_captcha_time_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Captcha timeout selection submenu."""
    current_timeout = config.captcha_timeout if config else 180

    if current_timeout < 60:
        current_label = f"{current_timeout} Segundos"
    elif current_timeout < 3600:
        current_label = f"{current_timeout // 60} Minutos"
    else:
        current_label = f"{current_timeout // 3600} Horas"

    title = (
        "Tiempo de Captcha\n\n"
        f"🕒 Tiempo actual: {current_label}"
    )

    menu = MenuDefinition(
        menu_id="captcha:time",
        title=title,
        parent_menu="captcha",
    )

    for seconds, label in CAPTCHA_TIMEOUTS:
        is_current = seconds == current_timeout
        menu.add_row().add_action(
            f"captcha:time:{seconds}",
            f"[{label}]" if is_current else label,
        )

    menu.add_row().add_action("captcha:show", "Volver")

    return menu


def create_captcha_fail_action_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Captcha fail action selection submenu."""
    current_action = config.captcha_fail_action if config else "kick"
    current_label = CAPTCHA_FAIL_ACTION_LABELS.get(current_action, current_action)

    title = (
        "Castigo por Fallar\n\n"
        f"⛔️ Castigo actual: {current_label}"
    )

    menu = MenuDefinition(
        menu_id="captcha:fail_action",
        title=title,
        parent_menu="captcha",
    )

    for action in CAPTCHA_FAIL_ACTIONS:
        label = CAPTCHA_FAIL_ACTION_LABELS.get(action, action)
        is_current = action == current_action
        menu.add_row().add_action(
            f"captcha:fail_action:{action}",
            f"[{label}]" if is_current else label,
        )

    menu.add_row().add_action("captcha:show", "Volver")

    return menu

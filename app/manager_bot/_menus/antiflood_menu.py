"""Anti-Flood menu definitions."""

from typing import Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.base import MenuDefinition


def _format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "sin duracion"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


def _format_action(config: Optional[GroupConfig]) -> str:
    if not config:
        return "Off"
    action = (config.antiflood_action or "off").lower()
    mapping = {
        "off": "Off",
        "warn": "Warn",
        "kick": "Kick",
        "mute": "Silenciar",
        "ban": "Ban",
    }
    label = mapping.get(action, action)
    duration = ""
    if action == "warn":
        duration = f" ({_format_duration(config.antiflood_warn_duration_sec)})"
    elif action == "ban":
        duration = f" ({_format_duration(config.antiflood_ban_duration_sec)})"
    elif action == "mute":
        duration = f" ({_format_duration(config.antiflood_mute_duration_sec)})"
    delete_suffix = " + Borrar mensajes" if config.antiflood_delete_messages else ""
    return f"{label}{duration}{delete_suffix}"


def create_antiflood_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Anti-Flood menu."""
    limit = config.antiflood_limit if config else 5
    interval = config.antiflood_interval if config else 5
    action_text = _format_action(config)

    text = (
        "Anti-Flood\n"
        "Desde este menu puedes establecer un castigo para quienes envien muchos mensajes en poco tiempo.\n\n"
        "Actualmente se activa si se envian:\n"
        f"{limit} mensajes en {interval} segundos.\n\n"
        f"Castigo: {action_text}"
    )

    menu = MenuDefinition(
        menu_id="antiflood",
        title=text,
        parent_menu="main",
    )

    menu.add_row() \
        .add_action("mod:antiflood:limit:show", "Mensajes") \
        .add_action("mod:antiflood:interval:show", "Tiempo")

    menu.add_row() \
        .add_action("mod:antiflood:action:off", "Off") \
        .add_action("mod:antiflood:action:warn", "Warn")

    menu.add_row() \
        .add_action("mod:antiflood:action:kick", "Kick") \
        .add_action("mod:antiflood:action:mute", "Silenciar") \
        .add_action("mod:antiflood:action:ban", "Ban")

    delete_enabled = config.antiflood_delete_messages if config else False
    delete_label = "Borrar mensajes: Si" if delete_enabled else "Borrar mensajes: No"
    menu.add_row().add_action(
        f"mod:antiflood:delete:toggle:{'off' if delete_enabled else 'on'}",
        delete_label,
    )

    if config:
        if config.antiflood_action == "warn":
            menu.add_row().add_action("mod:antiflood:warn:duration:show", "Duracion advertencia")
        elif config.antiflood_action == "ban":
            menu.add_row().add_action("mod:antiflood:ban:duration:show", "Duracion ban")
        elif config.antiflood_action == "mute":
            menu.add_row().add_action("mod:antiflood:mute:duration:show", "Duracion silenciar")

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def _add_numeric_buttons(menu: MenuDefinition, prefix: str) -> None:
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]
    row = None
    for idx, value in enumerate(values, start=1):
        if row is None or (idx - 1) % 4 == 0:
            row = menu.add_row()
        row.add_action(f"{prefix}:{value}", str(value))


def create_antiflood_limit_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the message limit submenu."""
    limit = config.antiflood_limit if config else 5
    interval = config.antiflood_interval if config else 5
    text = (
        "Cantidad de Mensajes\n"
        "Desde aqui puedes establecer la cantidad minima de mensajes para activar el antiflood.\n\n"
        "Actualmente se activa cuando se envian:\n"
        f"{limit} mensajes en {interval} segundos."
    )

    menu = MenuDefinition(
        menu_id="antiflood:limit",
        title=text,
        parent_menu="antiflood",
    )

    _add_numeric_buttons(menu, "mod:antiflood:limit:set")
    menu.add_row().add_action("mod:antiflood:show", "Volver")
    return menu


def create_antiflood_interval_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the time interval submenu."""
    limit = config.antiflood_limit if config else 5
    interval = config.antiflood_interval if config else 5
    text = (
        "Intervalo de Tiempo\n"
        "Desde aqui puedes establecer el intervalo de tiempo para activar el antiflood.\n\n"
        "Actualmente se activa cuando se envian:\n"
        f"{limit} mensajes en {interval} segundos."
    )

    menu = MenuDefinition(
        menu_id="antiflood:interval",
        title=text,
        parent_menu="antiflood",
    )

    _add_numeric_buttons(menu, "mod:antiflood:interval:set")
    menu.add_row().add_action("mod:antiflood:show", "Volver")
    return menu


def create_antiflood_warn_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the warn duration submenu."""
    current = _format_duration(config.antiflood_warn_duration_sec) if config else "sin duracion"
    text = (
        "Duracion de Advertencia\n"
        "Envia ahora la duracion del castigo (Warn).\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
        f"Duracion actual: {current}"
    )

    menu = MenuDefinition(
        menu_id="antiflood:warn:duration",
        title=text,
        parent_menu="antiflood",
    )

    menu.add_row().add_action("mod:antiflood:duration:clear:warn", "Eliminar duracion")
    menu.add_row().add_action("mod:antiflood:show", "Cancelar")
    return menu


def create_antiflood_ban_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the ban duration submenu."""
    current = _format_duration(config.antiflood_ban_duration_sec) if config else "sin duracion"
    text = (
        "Duracion de Ban\n"
        "Envia ahora la duracion del castigo (Ban).\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
        f"Duracion actual: {current}"
    )

    menu = MenuDefinition(
        menu_id="antiflood:ban:duration",
        title=text,
        parent_menu="antiflood",
    )

    menu.add_row().add_action("mod:antiflood:duration:clear:ban", "Eliminar duracion")
    menu.add_row().add_action("mod:antiflood:show", "Cancelar")
    return menu


def create_antiflood_mute_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the mute duration submenu."""
    current = _format_duration(config.antiflood_mute_duration_sec) if config else "sin duracion"
    text = (
        "Duracion de Silenciar\n"
        "Envia ahora la duracion del castigo (Silenciar).\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
        f"Duracion actual: {current}"
    )

    menu = MenuDefinition(
        menu_id="antiflood:mute:duration",
        title=text,
        parent_menu="antiflood",
    )

    menu.add_row().add_action("mod:antiflood:duration:clear:mute", "Eliminar duracion")
    menu.add_row().add_action("mod:antiflood:show", "Cancelar")
    return menu

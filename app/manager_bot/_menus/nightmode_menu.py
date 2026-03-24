"""NightMode menu definitions."""

from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.manager_bot._menus.base import MenuDefinition, MenuRow, MenuAction
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import on_off
from app.manager_bot._menus.rendering import build_title, build_section


MODE_LABELS = {
    "multimedia": "📸 Eliminación multimedia",
    "silencio": "🔇 Silencio global",
}

MODE_ICONS = {
    "multimedia": "📸",
    "silencio": "🔇",
}


def _get_current_mode_label(config: GroupConfig) -> str:
    """Get the current mode label based on configuration."""
    if not config:
        return "📸 Eliminación multimedia"
    
    if config.nightmode_silence and not config.nightmode_delete_media:
        return "🔇 Silencio global"
    elif config.nightmode_delete_media and not config.nightmode_silence:
        return "📸 Eliminación multimedia"
    elif config.nightmode_delete_media and config.nightmode_silence:
        return "📸 Eliminación multimedia + 🔇 Silencio"
    
    return "📸 Eliminación multimedia"


def _get_active_hours(config: GroupConfig) -> str:
    """Get the active hours string."""
    start = config.nightmode_start if config else "23:00"
    end = config.nightmode_end if config else "07:00"
    return f"{start} - {end}"


def create_nightmode_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the night mode settings menu with tree format."""
    enabled = config.nightmode_enabled if config else False
    announcements = config.nightmode_announcements if config else True
    
    mode_label = _get_current_mode_label(config)
    hours_str = _get_active_hours(config)
    
    title_lines = [
        f"🌙 Modo Nocturno",
        f"",
        f"Estado: {mode_label}",
        f"├ Activo entre las horas {hours_str}",
        f"└ Anuncios de inicio y fin: {'✅' if announcements else '❌'}",
    ]
    title = "\n".join(title_lines)
    
    menu = MenuDefinition(
        menu_id="mod:nightmode",
        title=title,
        parent_menu="main",
    )
    
    toggle_label = "🌙 Desactivar" if enabled else "🌙 Activar"
    menu.add_row().add_action(
        f"mod:nightmode:toggle:{'off' if enabled else 'on'}",
        toggle_label,
    )
    
    menu.add_row().add_action(
        "mod:nightmode:mode",
        "Cambiar modo de acción",
    )
    
    menu.add_row().add_action(
        "mod:nightmode:schedule",
        "⏰ Establecer franja horaria",
    )
    
    ann_label = "🔔 Anuncios: Desactivar" if announcements else "🔔 Anuncios: Activar"
    menu.add_row().add_action(
        f"mod:nightmode:announcements:{'off' if announcements else 'on'}",
        ann_label,
    )
    
    menu.add_row().add_action("nav:back:main", "🔙 Volver")
    
    return menu


def create_mode_selection_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the mode selection submenu."""
    delete_media = config.nightmode_delete_media if config else True
    silence = config.nightmode_silence if config else False
    
    title = "📋 Seleccionar modo de acción"
    
    menu = MenuDefinition(
        menu_id="mod:nightmode_mode",
        title=title,
        parent_menu="mod:nightmode",
    )
    
    dm_label = f"✅ {MODE_LABELS['multimedia']}" if delete_media else MODE_LABELS['multimedia']
    menu.add_row().add_action(
        f"mod:nightmode:action:delete_media:{'off' if delete_media else 'on'}",
        dm_label,
    )
    
    sil_label = f"✅ {MODE_LABELS['silencio']}" if silence else MODE_LABELS['silencio']
    menu.add_row().add_action(
        f"mod:nightmode:action:silence:{'off' if silence else 'on'}",
        sil_label,
    )
    
    menu.add_row().add_action("mod:nightmode:show", "🔙 Volver")
    
    return menu


def create_schedule_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the schedule selection menu with 5x4 matrix."""
    start = config.nightmode_start if config else "23:00"
    end = config.nightmode_end if config else "07:00"
    
    start_hour = int(start.split(":")[0]) if start else 23
    end_hour = int(end.split(":")[0]) if end else 7
    
    title = f"⏰ Seleccionar horario\n\n"
    title += f"├ Inicio: {start} (clic para cambiar)\n"
    title += f"└ Fin: {end} (clic para cambiar)"
    
    menu = MenuDefinition(
        menu_id="mod:nightmode_schedule",
        title=title,
        parent_menu="mod:nightmode",
    )
    
    menu.add_row().add_action("mod:nightmode:schedule:start", f"🕐 Hora inicio: {start}")
    menu.add_row().add_action("mod:nightmode:schedule:end", f"🕑 Hora fin: {end}")
    
    menu.add_row().add_action("mod:nightmode:show", "🔙 Volver al menú principal")
    
    return menu


def create_schedule_matrix_menu(
    config: Optional[GroupConfig] = None,
    selecting_start: bool = True
) -> MenuDefinition:
    """Create the hour selection matrix (5x4 for 0-23)."""
    current = config.nightmode_start if config else "23:00"
    if not selecting_start:
        current = config.nightmode_end if config else "07:00"
    
    current_hour = int(current.split(":")[0]) if current else (23 if selecting_start else 7)
    
    hour_type = "INICIO" if selecting_start else "FIN"
    title = f"⏰ Seleccionar hora de {hour_type}\n\nClic en una hora para seleccionar"
    
    menu = MenuDefinition(
        menu_id=f"mod:nightmode_schedule_{'start' if selecting_start else 'end'}",
        title=title,
        parent_menu="mod:nightmode_schedule",
    )
    
    hours = list(range(24))
    for row_start in range(0, 24, 4):
        row_hours = hours[row_start:row_start + 4]
        for hour in row_hours:
            is_selected = hour == current_hour
            label = f"✓ {hour:02d}:00" if is_selected else f"{hour:02d}:00"
            menu.add_row().add_action(
                f"mod:nightmode:schedule:{'start' if selecting_start else 'end'}:{hour}",
                label,
            )
    
    menu.add_row().add_action("mod:nightmode:schedule", "🔙 Volver")
    
    return menu


def build_schedule_keyboard(
    selecting_start: bool = True,
    current_hour: int = 23
) -> InlineKeyboardMarkup:
    """Build inline keyboard for hour selection matrix (5x4 grid)."""
    keyboard = []
    
    for row_start in range(0, 24, 4):
        row = []
        for hour in range(row_start, min(row_start + 4, 24)):
            is_selected = hour == current_hour
            label = f"✓{hour:02d}" if is_selected else f"{hour:02d}"
            callback = f"mod:nightmode:schedule:{'start' if selecting_start else 'end'}:{hour}"
            row.append(InlineKeyboardButton(label, callback_data=callback))
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("🔙 Volver", callback_data="mod:nightmode:schedule")
    ])
    
    return InlineKeyboardMarkup(keyboard)
"""Reports menu definitions."""

from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.manager_bot._menus.base import MenuDefinition, MenuRow, MenuAction
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.rendering import build_title, build_section
from app.manager_bot._features.reports import Report, ReportStats


DESTINATION_LABELS = {
    "ninguno": "🚫 Ninguno",
    "fundador": "👑 Fundador",
    "grupo_staff": "👥 Grupo Staff",
}


def create_reports_menu(
    config: Optional[GroupConfig] = None,
    stats: Optional[ReportStats] = None
) -> MenuDefinition:
    """Create the reports settings menu."""
    title = build_title(
        "Centro de Reportes",
        [
            build_section("Abiertos", str(stats.open) if stats else "0"),
            build_section("Resueltos", str(stats.resolved) if stats else "0"),
        ] if stats else None
    )
    menu = MenuDefinition(
        menu_id="reports",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action(
        "reports:list:open",
        f"Reportes abiertos ({stats.open})" if stats else "Reportes abiertos",
    )

    menu.add_row().add_action(
        "reports:list:resolved",
        f"Reportes resueltos ({stats.resolved})" if stats else "Reportes resueltos",
    )

    menu.add_row().add_action(
        "reports:stats",
        "Estadisticas",
    )

    current_dest = "ninguno"
    if config and hasattr(config, "report_destination"):
        current_dest = config.report_destination or "ninguno"

    dest_label = DESTINATION_LABELS.get(current_dest, DESTINATION_LABELS["ninguno"])
    menu.add_row().add_action(
        "reports:config:dest",
        f"📤 Destinatario: {dest_label}",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_destination_menu(
    current_destination: str = "ninguno",
    enabled: bool = True
) -> MenuDefinition:
    """Create the destination configuration menu."""
    title = build_title(
        "📤 Configurar Destinatario de Reportes",
        [build_section("Estado", "✅ Activado" if enabled else "❌ Desactivado")] if enabled else None
    )
    menu = MenuDefinition(
        menu_id="reports_config_destination",
        title=title,
        parent_menu="reports",
    )

    options = [
        ("ninguno", "🚫 No enviar a nadie"),
        ("fundador", "👑 Enviar al fundador"),
        ("grupo_staff", "👥 Enviar al grupo Staff"),
    ]

    for dest_value, dest_label in options:
        is_selected = current_destination == dest_value
        label = f"✓ {dest_label}" if is_selected else dest_label
        menu.add_row().add_action(
            f"reports:config:set:{dest_value}",
            label,
        )

    menu.add_row().add_action(
        f"reports:config:toggle:{'off' if enabled else 'on'}",
        "❌ Desactivar" if enabled else "✅ Activar",
    )

    menu.add_row().add_action("reports:show", "🔙 Volver")

    return menu


def build_reports_list_keyboard(
    status: str,
    page: int,
    total_pages: int,
    reports: List[Report]
) -> InlineKeyboardMarkup:
    """Build keyboard for reports list with pagination and actions."""
    keyboard = []

    for report in reports:
        report_short_id = report.report_id[:8]
        row = [
            InlineKeyboardButton(
                f"📋 {report_short_id} | User:{report.reported_id}",
                callback_data=f"reports:detail:{report.report_id}"
            )
        ]
        keyboard.append(row)

        actions_row = [
            InlineKeyboardButton("🚫 Ban", callback_data=f"reports:resolve:{report.report_id}:ban"),
            InlineKeyboardButton("⚠️ Warn", callback_data=f"reports:resolve:{report.report_id}:warn"),
            InlineKeyboardButton("👢 Kick", callback_data=f"reports:resolve:{report.report_id}:kick"),
            InlineKeyboardButton("✅ Ignorar", callback_data=f"reports:resolve:{report.report_id}:ignore"),
        ]
        keyboard.append(actions_row)

        keyboard.append([
            InlineKeyboardButton("❌ Descartar", callback_data=f"reports:dismiss:{report.report_id}")
        ])

    pagination_row = []
    if page > 0:
        pagination_row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"reports:list:{status}:{page - 1}"))
    if page < total_pages - 1:
        pagination_row.append(InlineKeyboardButton("Siguiente ➡️", callback_data=f"reports:list:{status}:{page + 1}"))
    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="reports:show")])

    return InlineKeyboardMarkup(keyboard)

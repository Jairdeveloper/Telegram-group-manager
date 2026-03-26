"""Reports feature module."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule
from app.manager_bot._features.reports.repository import ReportRepository

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class ReportStatus(Enum):
    """Report status."""
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportAction(Enum):
    """Action taken on a report."""
    BAN = "ban"
    WARN = "warn"
    KICK = "kick"
    IGNORE = "ignore"


@dataclass
class Report:
    """Represents a user report."""
    report_id: str
    chat_id: int
    reporter_id: int
    reported_id: int
    reason: str
    message_id: Optional[int] = None
    status: ReportStatus = ReportStatus.OPEN
    action: Optional[ReportAction] = None
    resolved_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    recipients: List[int] = field(default_factory=list)


@dataclass
class ReportStats:
    """Report statistics."""
    total: int = 0
    open: int = 0
    resolved: int = 0
    dismissed: int = 0


class ReportsFeature(FeatureModule):
    """Feature module for user reports."""

    MENU_ID = "reports"
    FEATURE_NAME = "Reports"

    def __init__(
        self,
        config_storage: ConfigStorage,
        repository: Optional[ReportRepository] = None,
    ):
        super().__init__(config_storage)
        self._repository = repository
        self._reports: Dict[int, List[Report]] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for reports."""

        async def handle_show_list(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            parts = data.split(":")
            status_filter = parts[2] if len(parts) > 2 else None
            page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

            status = ReportStatus(status_filter) if status_filter else None
            reports = self.get_reports(chat_id, status)

            page_size = 10
            total_pages = (len(reports) + page_size - 1) // page_size
            page = min(page, max(0, total_pages - 1))
            page_reports = reports[page * page_size:(page + 1) * page_size]

            if not page_reports:
                await callback.answer("No hay reportes para mostrar", show_alert=True)
                return

            lines = [f"📋 Reportes {'abiertos' if status_filter == 'open' else 'resueltos'}: (Página {page + 1}/{total_pages})"]
            for r in page_reports:
                status_emoji = "🔴" if r.status == ReportStatus.OPEN else "✅"
                lines.append(f"{status_emoji} ID:{r.report_id[:6]} | User:{r.reported_id}")
                lines.append(f"   Razón: {r.reason[:50]}")
                if r.status == ReportStatus.RESOLVED and r.action:
                    lines.append(f"   Acción: {r.action.value}")

            text = "\n".join(lines)

            from app.manager_bot._menus.reports_menu import build_reports_list_keyboard
            keyboard = build_reports_list_keyboard(
                status_filter or "open",
                page,
                total_pages,
                page_reports
            )

            try:
                await callback.edit_message_text(text=text, reply_markup=keyboard)
            except Exception:
                await callback.answer("Error al mostrar reportes", show_alert=True)

        async def handle_stats(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            stats = self.get_stats(chat_id)
            text = (
                f"📊 Estadísticas de Reportes\n\n"
                f"• Total: {stats.total}\n"
                f"• Abiertos: {stats.open}\n"
                f"• Resueltos: {stats.resolved}\n"
                f"• Descartados: {stats.dismissed}"
            )

            try:
                await callback.edit_message_text(
                    text=text,
                    reply_markup=callback.message.reply_markup if callback.message else None
                )
            except Exception:
                pass
            await callback.answer()

        async def handle_resolve(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            report_id = parts[2]
            action_str = parts[3]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            try:
                action = ReportAction(action_str)
            except ValueError:
                await callback.answer("Acción inválida", show_alert=True)
                return

            report = self.get_report_by_id(report_id)
            if not report:
                await callback.answer("Reporte no encontrado", show_alert=True)
                return

            action_performed = False
            action_message = ""

            if action in (ReportAction.BAN, ReportAction.WARN, ReportAction.KICK):
                try:
                    from app.enterprise.transport.handlers import _build_services
                    from app.config.settings import load_enterprise_settings

                    settings = load_enterprise_settings()
                    user_service, _, _, _ = _build_services()

                    if action == ReportAction.BAN:
                        user_service.ban_user(
                            callback.from_user.id,
                            report.reported_id,
                            f"Reporte #{report_id[:8]}: {report.reason}"
                        )
                        action_performed = True
                        action_message = "Usuario baneado"
                    elif action == ReportAction.KICK:
                        try:
                            await bot.unban_chat_member(chat_id, report.reported_id)
                            await bot.ban_chat_member(chat_id, report.reported_id)
                            action_performed = True
                            action_message = "Usuario expulsado"
                        except Exception:
                            action_message = "Error al expulsar (verifica permisos)"
                    elif action == ReportAction.WARN:
                        action_performed = True
                        action_message = "Usuario advertid@"

                except PermissionError as e:
                    action_message = f"No tienes permisos: {str(e)}"
                except Exception as e:
                    action_message = f"Error: {str(e)}"

            success = self.resolve_report(report_id, action, callback.from_user.id)
            if success:
                await callback.answer(
                    f"Reporte resuelto. {action_message}" if action_performed else f"Reporte resuelto con acción: {action.value}",
                    show_alert=True
                )
                try:
                    await callback.edit_message_text(
                        text=f"✅ Reporte resuelto\n{action_message}",
                        reply_markup=None
                    )
                except Exception:
                    pass
            else:
                await callback.answer("Reporte no encontrado", show_alert=True)

        async def handle_dismiss(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            report_id = parts[2]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            success = self.dismiss_report(report_id, callback.from_user.id)
            if success:
                await callback.answer("Reporte descartado", show_alert=True)
                try:
                    await callback.edit_message_text(
                        text="Reporte descartado",
                        reply_markup=None
                    )
                except Exception:
                    pass
            else:
                await callback.answer("Reporte no encontrado", show_alert=True)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.reports_menu import create_reports_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            stats = self.get_stats(chat_id)
            menu = create_reports_menu(config, stats)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_config_destination(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.reports_menu import create_destination_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            current_dest = "ninguno"
            enabled = True

            if config and hasattr(config, "report_destination"):
                current_dest = config.report_destination or "ninguno"
                enabled = getattr(config, "report_destination_enabled", True)

            menu = create_destination_menu(current_dest, enabled)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_set_destination(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            dest_type = parts[3]

            from app.manager_bot._features.reports.config_service import (
                DestinationType,
                ReportsConfigService,
            )

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            valid_dests = {d.value for d in DestinationType}
            if dest_type not in valid_dests:
                await callback.answer("Destino inválido", show_alert=True)
                return

            config_service = ReportsConfigService(self._config_storage)
            await config_service.set_destination(chat_id, DestinationType(dest_type))

            await callback.answer(f"Destinatario configurado: {dest_type}", show_alert=True)

            menu = create_destination_menu(dest_type, True)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_toggle_destination(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            new_state = parts[3] == "on"

            from app.manager_bot._features.reports.config_service import ReportsConfigService

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config_service = ReportsConfigService(self._config_storage)
            await config_service.set_enabled(chat_id, new_state)

            config = await self.get_config(chat_id)
            current_dest = "ninguno"
            if config and hasattr(config, "report_destination"):
                current_dest = config.report_destination or "ninguno"

            from app.manager_bot._menus.reports_menu import create_destination_menu
            menu = create_destination_menu(current_dest, new_state)

            await callback.answer(
                f"Destinatario {'activado' if new_state else 'desactivado'}",
                show_alert=True
            )

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("reports:list", handle_show_list)
        router.register_callback("reports:resolve", handle_resolve)
        router.register_callback("reports:dismiss", handle_dismiss)
        router.register_callback("reports:stats", handle_stats)
        router.register_exact("reports:show", handle_show_menu)
        router.register_exact("reports:config:dest", handle_config_destination)
        router.register_callback("reports:config:set", handle_set_destination)
        router.register_callback("reports:config:toggle", handle_toggle_destination)

    def create_report(
        self,
        chat_id: int,
        reporter_id: int,
        reported_id: int,
        reason: str,
        message_id: Optional[int] = None,
        founder_id: Optional[int] = None,
        staff_ids: Optional[List[int]] = None,
    ) -> Report:
        """Create a new report."""
        recipients = []
        
        from app.manager_bot._features.reports.config_service import ReportsConfigService
        config_service = ReportsConfigService(self._config_storage)
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    recipients = list(executor.submit(
                        asyncio.run,
                        config_service.get_destination_recipients(chat_id, founder_id, staff_ids)
                    ).result())
            else:
                recipients = asyncio.run(
                    config_service.get_destination_recipients(chat_id, founder_id, staff_ids)
                )
        except Exception:
            recipients = []

        report = Report(
            report_id=str(uuid.uuid4()),
            chat_id=chat_id,
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            message_id=message_id,
            recipients=recipients,
        )

        if self._repository:
            self._repository.save(report)
        else:
            key = chat_id
            if key not in self._reports:
                self._reports[key] = []
            self._reports[key].append(report)

        return report

    def get_reports(self, chat_id: int, status: Optional[ReportStatus] = None) -> List[Report]:
        """Get reports for a chat."""
        if self._repository:
            return self._repository.get_by_chat(chat_id, status)

        reports = self._reports.get(chat_id, [])
        if status:
            reports = [r for r in reports if r.status == status]
        return reports

    def get_report_by_id(self, report_id: str) -> Optional[Report]:
        """Get a report by its ID."""
        if self._repository:
            return self._repository.get_by_id(report_id)

        for reports in self._reports.values():
            for report in reports:
                if report.report_id == report_id:
                    return report
        return None

    def resolve_report(
        self,
        report_id: str,
        action: ReportAction,
        resolved_by: int,
    ) -> bool:
        """Resolve a report."""
        if self._repository:
            return self._repository.update_status(
                report_id, ReportStatus.RESOLVED, action, resolved_by
            )

        for reports in self._reports.values():
            for report in reports:
                if report.report_id == report_id:
                    report.status = ReportStatus.RESOLVED
                    report.action = action
                    report.resolved_by = resolved_by
                    report.resolved_at = datetime.utcnow()
                    return True
        return False

    def dismiss_report(self, report_id: str, dismissed_by: int) -> bool:
        """Dismiss a report without taking action."""
        if self._repository:
            return self._repository.update_status(
                report_id, ReportStatus.DISMISSED, None, dismissed_by
            )

        for reports in self._reports.values():
            for report in reports:
                if report.report_id == report_id:
                    report.status = ReportStatus.DISMISSED
                    report.resolved_by = dismissed_by
                    report.resolved_at = datetime.utcnow()
                    return True
        return False

    def delete_report(self, report_id: str) -> bool:
        """Delete a report."""
        if self._repository:
            return self._repository.delete(report_id)

        for reports in self._reports.values():
            for i, report in enumerate(reports):
                if report.report_id == report_id:
                    reports.pop(i)
                    return True
        return False

    def get_stats(self, chat_id: int) -> ReportStats:
        """Get report statistics."""
        if self._repository:
            stats = self._repository.get_stats(chat_id)
            return ReportStats(
                total=stats["total"],
                open=stats["open"],
                resolved=stats["resolved"],
                dismissed=stats["dismissed"],
            )

        reports = self._reports.get(chat_id, [])
        return ReportStats(
            total=len(reports),
            open=len([r for r in reports if r.status == ReportStatus.OPEN]),
            resolved=len([r for r in reports if r.status == ReportStatus.RESOLVED]),
            dismissed=len([r for r in reports if r.status == ReportStatus.DISMISSED]),
        )

"""Reports feature module."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

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

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)
        self._reports: Dict[int, List[Report]] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for reports."""

        async def handle_show_list(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Usa /reports para ver la lista de reportes",
                show_alert=True
            )

        async def handle_stats(callback: "CallbackQuery", bot: "Bot", data: str):
            stats = self.get_stats(0)
            await callback.answer(
                f"Reports: {stats.open} abiertos, {stats.resolved} resueltos",
                show_alert=True
            )

        async def handle_resolve(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 4:
                report_id = parts[2]
                action = parts[3]
            else:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            await callback.answer(
                f"Reporte {report_id} resuelto con acción: {action}",
                show_alert=True
            )

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.reports_menu import create_reports_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_reports_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("reports:list", handle_show_list)
        router.register_callback("reports:resolve", handle_resolve)
        router.register_exact("reports:stats", handle_stats)
        router.register_exact("reports:show", handle_show_menu)

    def create_report(
        self,
        chat_id: int,
        reporter_id: int,
        reported_id: int,
        reason: str,
        message_id: Optional[int] = None,
    ) -> Report:
        """Create a new report."""
        key = chat_id
        
        report = Report(
            report_id=str(uuid.uuid4()),
            chat_id=chat_id,
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            message_id=message_id,
        )
        
        if key not in self._reports:
            self._reports[key] = []
        
        self._reports[key].append(report)
        return report

    def get_reports(self, chat_id: int, status: Optional[ReportStatus] = None) -> List[Report]:
        """Get reports for a chat."""
        reports = self._reports.get(chat_id, [])
        if status:
            reports = [r for r in reports if r.status == status]
        return reports

    def resolve_report(
        self,
        report_id: str,
        action: ReportAction,
        resolved_by: int,
    ) -> bool:
        """Resolve a report."""
        for reports in self._reports.values():
            for report in reports:
                if report.report_id == report_id:
                    report.status = ReportStatus.RESOLVED
                    report.action = action
                    report.resolved_by = resolved_by
                    report.resolved_at = datetime.utcnow()
                    return True
        return False

    def get_stats(self, chat_id: int) -> ReportStats:
        """Get report statistics."""
        reports = self._reports.get(chat_id, [])
        return ReportStats(
            total=len(reports),
            open=len([r for r in reports if r.status == ReportStatus.OPEN]),
            resolved=len([r for r in reports if r.status == ReportStatus.RESOLVED]),
            dismissed=len([r for r in reports if r.status == ReportStatus.DISMISSED]),
        )

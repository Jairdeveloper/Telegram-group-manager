"""Reports repository for data persistence."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

if TYPE_CHECKING:
    from app.manager_bot._features.reports import Report, ReportAction, ReportStatus

logger = logging.getLogger(__name__)


class ReportRepository:
    """Repository for persisting reports."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create reports table if it doesn't exist."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id VARCHAR(36) PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    reporter_id BIGINT NOT NULL,
                    reported_id BIGINT NOT NULL,
                    reason TEXT NOT NULL,
                    message_id BIGINT,
                    status VARCHAR(20) NOT NULL DEFAULT 'open',
                    action VARCHAR(20),
                    resolved_by BIGINT,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    resolved_at TIMESTAMP,
                    recipients TEXT
                )
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reports_chat_id ON reports(chat_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)
            """))
            conn.commit()

    def save(self, report: "Report") -> None:
        """Save a report to the database."""
        from app.manager_bot._features.reports import ReportAction, ReportStatus
        
        recipients_json = json.dumps(report.recipients) if report.recipients else None
        
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO reports (
                        report_id, chat_id, reporter_id, reported_id, reason,
                        message_id, status, action, resolved_by, created_at, resolved_at,
                        recipients
                    ) VALUES (
                        :report_id, :chat_id, :reporter_id, :reported_id, :reason,
                        :message_id, :status, :action, :resolved_by, :created_at, :resolved_at,
                        :recipients
                    )
                """),
                {
                    "report_id": report.report_id,
                    "chat_id": report.chat_id,
                    "reporter_id": report.reporter_id,
                    "reported_id": report.reported_id,
                    "reason": report.reason,
                    "message_id": report.message_id,
                    "status": report.status.value,
                    "action": report.action.value if report.action else None,
                    "resolved_by": report.resolved_by,
                    "created_at": report.created_at,
                    "resolved_at": report.resolved_at,
                    "recipients": recipients_json,
                },
            )
            conn.commit()

    def get_by_chat(
        self,
        chat_id: int,
        status: Optional["ReportStatus"] = None,
    ) -> List["Report"]:
        """Get all reports for a chat, optionally filtered by status."""
        from app.manager_bot._features.reports import ReportStatus
        
        query = "SELECT * FROM reports WHERE chat_id = :chat_id"
        params = {"chat_id": chat_id}

        if status:
            query += " AND status = :status"
            params["status"] = status.value

        query += " ORDER BY created_at DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params).fetchall()
            return [self._row_to_report(row) for row in result]

    def get_by_id(self, report_id: str) -> Optional["Report"]:
        """Get a report by its ID."""
        with self.engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM reports WHERE report_id = :report_id"),
                {"report_id": report_id},
            ).fetchone()
            return self._row_to_report(row) if row else None

    def update_status(
        self,
        report_id: str,
        status: "ReportStatus",
        action: Optional["ReportAction"] = None,
        resolved_by: Optional[int] = None,
    ) -> bool:
        """Update the status of a report."""
        from app.manager_bot._features.reports import ReportStatus
        
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    UPDATE reports
                    SET status = :status,
                        action = :action,
                        resolved_by = :resolved_by,
                        resolved_at = :resolved_at
                    WHERE report_id = :report_id
                """),
                {
                    "report_id": report_id,
                    "status": status.value,
                    "action": action.value if action else None,
                    "resolved_by": resolved_by,
                    "resolved_at": datetime.utcnow() if status != ReportStatus.OPEN else None,
                },
            )
            conn.commit()
            return result.rowcount > 0

    def delete(self, report_id: str) -> bool:
        """Delete a report by its ID."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("DELETE FROM reports WHERE report_id = :report_id"),
                {"report_id": report_id},
            )
            conn.commit()
            return result.rowcount > 0

    def get_stats(self, chat_id: int) -> dict:
        """Get report statistics for a chat."""
        with self.engine.connect() as conn:
            total = conn.execute(
                text("SELECT COUNT(*) FROM reports WHERE chat_id = :chat_id"),
                {"chat_id": chat_id},
            ).fetchone()[0]

            open_count = conn.execute(
                text("SELECT COUNT(*) FROM reports WHERE chat_id = :chat_id AND status = 'open'"),
                {"chat_id": chat_id},
            ).fetchone()[0]

            resolved = conn.execute(
                text("SELECT COUNT(*) FROM reports WHERE chat_id = :chat_id AND status = 'resolved'"),
                {"chat_id": chat_id},
            ).fetchone()[0]

            dismissed = conn.execute(
                text("SELECT COUNT(*) FROM reports WHERE chat_id = :chat_id AND status = 'dismissed'"),
                {"chat_id": chat_id},
            ).fetchone()[0]

        return {
            "total": total,
            "open": open_count,
            "resolved": resolved,
            "dismissed": dismissed,
        }

    def _row_to_report(self, row) -> "Report":
        """Convert a database row to a Report object."""
        from app.manager_bot._features.reports import ReportAction, ReportStatus
        
        recipients = []
        if row.recipients:
            try:
                recipients = json.loads(row.recipients)
            except (json.JSONDecodeError, TypeError):
                recipients = []
        
        return Report(
            report_id=row.report_id,
            chat_id=row.chat_id,
            reporter_id=row.reporter_id,
            reported_id=row.reported_id,
            reason=row.reason,
            message_id=row.message_id,
            status=ReportStatus(row.status),
            action=ReportAction(row.action) if row.action else None,
            resolved_by=row.resolved_by,
            created_at=row.created_at,
            resolved_at=row.resolved_at,
            recipients=recipients,
        )

    def get_top_reported_users(self, chat_id: int, limit: int = 10) -> List[dict]:
        """Get top reported users for a chat."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT reported_id, COUNT(*) as report_count
                    FROM reports
                    WHERE chat_id = :chat_id
                    GROUP BY reported_id
                    ORDER BY report_count DESC
                    LIMIT :limit
                """),
                {"chat_id": chat_id, "limit": limit},
            ).fetchall()
            return [{"user_id": row[0], "count": row[1]} for row in result]

    def get_reports_by_reason(self, chat_id: int, limit: int = 10) -> List[dict]:
        """Get most common report reasons."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT reason, COUNT(*) as count
                    FROM reports
                    WHERE chat_id = :chat_id
                    GROUP BY reason
                    ORDER BY count DESC
                    LIMIT :limit
                """),
                {"chat_id": chat_id, "limit": limit},
            ).fetchall()
            return [{"reason": row[0], "count": row[1]} for row in result]

    def cleanup_old_reports(self, days: int = 30, keep_count: int = 100) -> int:
        """Clean up old resolved/dismissed reports.
        
        Args:
            days: Delete reports older than this many days
            keep_count: Keep at least this many reports per chat regardless of age
            
        Returns:
            Number of reports deleted
        """
        deleted = 0
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT chat_id FROM reports")).fetchall()
            for row in result:
                chat_id = row[0]

                conn.execute(
                    text("""
                        DELETE FROM reports
                        WHERE chat_id = :chat_id
                        AND status IN ('resolved', 'dismissed')
                        AND resolved_at < :cutoff_date
                        AND report_id NOT IN (
                            SELECT report_id FROM reports
                            WHERE chat_id = :chat_id
                            ORDER BY created_at DESC
                            LIMIT :keep_count
                        )
                    """),
                    {"chat_id": chat_id, "cutoff_date": cutoff_date, "keep_count": keep_count},
                )
                deleted += conn.execute(
                    text("SELECT CHANGES()")
                ).fetchone()[0]

            conn.commit()
        return deleted

    def export_to_json(self, chat_id: int) -> str:
        """Export reports to JSON format."""
        reports = self.get_by_chat(chat_id)
        data = []
        for r in reports:
            data.append({
                "report_id": r.report_id,
                "chat_id": r.chat_id,
                "reporter_id": r.reporter_id,
                "reported_id": r.reported_id,
                "reason": r.reason,
                "message_id": r.message_id,
                "status": r.status.value,
                "action": r.action.value if r.action else None,
                "resolved_by": r.resolved_by,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
            })
        return json.dumps(data, indent=2, ensure_ascii=False)

    def export_to_csv(self, chat_id: int) -> str:
        """Export reports to CSV format."""
        import csv
        import io

        reports = self.get_by_chat(chat_id)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "report_id", "chat_id", "reporter_id", "reported_id", "reason",
            "message_id", "status", "action", "resolved_by", "created_at", "resolved_at"
        ])

        for r in reports:
            writer.writerow([
                r.report_id,
                r.chat_id,
                r.reporter_id,
                r.reported_id,
                r.reason,
                r.message_id,
                r.status.value,
                r.action.value if r.action else "",
                r.resolved_by or "",
                r.created_at.isoformat() if r.created_at else "",
                r.resolved_at.isoformat() if r.resolved_at else "",
            ])

        return output.getvalue()

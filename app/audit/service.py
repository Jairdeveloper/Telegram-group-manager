"""Audit service for multi-tenant enterprise."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import secrets

from app.audit.models import AuditEvent, AuditEventType, AuditQuery


class AuditRepository(ABC):
    """Abstract base class for audit log storage."""

    @abstractmethod
    def save(self, event: AuditEvent) -> None:
        """Save an audit event."""
        pass

    @abstractmethod
    def query(
        self,
        tenant_id: str,
        event_types: Optional[List[AuditEventType]] = None,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events with filters."""
        pass

    @abstractmethod
    def get_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """Get a specific audit event by ID."""
        pass


class InMemoryAuditRepository(AuditRepository):
    """In-memory implementation of AuditRepository."""

    def __init__(self):
        self._events: List[AuditEvent] = []
        self._events_by_id: dict = {}

    def save(self, event: AuditEvent) -> None:
        self._events.append(event)
        self._events_by_id[event.event_id] = event

    def query(
        self,
        tenant_id: str,
        event_types: Optional[List[AuditEventType]] = None,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        results = []

        for event in reversed(self._events):
            if event.tenant_id != tenant_id:
                continue

            if event_types and event.event_type not in event_types:
                continue

            if actor_id and event.actor_id != actor_id:
                continue

            if resource_id and event.resource_id != resource_id:
                continue

            if start_date and event.timestamp < start_date:
                continue

            if end_date and event.timestamp > end_date:
                continue

            results.append(event)

            if len(results) >= limit:
                break

        return results

    def get_by_id(self, event_id: str) -> Optional[AuditEvent]:
        return self._events_by_id.get(event_id)


class AuditService:
    """Service for managing audit logs."""

    def __init__(self, audit_repo: Optional[AuditRepository] = None):
        self.audit_repo = audit_repo or InMemoryAuditRepository()

    def log(
        self,
        tenant_id: str,
        event_type: AuditEventType,
        actor_id: Optional[str] = None,
        actor_type: str = "system",
        resource_type: str = "",
        resource_id: Optional[str] = None,
        action: str = "",
        result: str = "success",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: dict = None
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=f"evt_{secrets.token_hex(16)}",
            tenant_id=tenant_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )

        self.audit_repo.save(event)
        return event

    def log_login(
        self,
        tenant_id: str,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        return self.log(
            tenant_id=tenant_id,
            event_type=AuditEventType.USER_LOGIN,
            actor_id=user_id,
            actor_type="user",
            action="login",
            result="success" if success else "failure",
            ip_address=ip_address,
            user_agent=user_agent
        )

    def log_logout(
        self,
        tenant_id: str,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        return self.log(
            tenant_id=tenant_id,
            event_type=AuditEventType.USER_LOGOUT,
            actor_id=user_id,
            actor_type="user",
            action="logout",
            ip_address=ip_address
        )

    def log_chat_message(
        self,
        tenant_id: str,
        session_id: str,
        actor_id: Optional[str] = None,
        actor_type: str = "user",
        blocked: bool = False
    ) -> AuditEvent:
        event_type = (
            AuditEventType.CHAT_MESSAGE_BLOCKED
            if blocked
            else AuditEventType.CHAT_MESSAGE
        )
        return self.log(
            tenant_id=tenant_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type="session",
            resource_id=session_id,
            action="send_message",
            result="blocked" if blocked else "success"
        )

    def log_policy_violation(
        self,
        tenant_id: str,
        session_id: str,
        policy_name: str,
        message: str,
        actor_id: Optional[str] = None
    ) -> AuditEvent:
        return self.log(
            tenant_id=tenant_id,
            event_type=AuditEventType.POLICY_VIOLATION,
            actor_id=actor_id,
            actor_type="user",
            resource_type="session",
            resource_id=session_id,
            action="policy_violation",
            result="blocked",
            metadata={"policy": policy_name, "message": message}
        )

    def query(self, query: AuditQuery) -> List[AuditEvent]:
        return self.audit_repo.query(
            tenant_id=query.tenant_id,
            event_types=query.event_types,
            actor_id=query.actor_id,
            resource_id=query.resource_id,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit
        )

    def get_user_activity(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 50
    ) -> List[AuditEvent]:
        return self.audit_repo.query(
            tenant_id=tenant_id,
            actor_id=user_id,
            limit=limit
        )

    def get_session_activity(
        self,
        tenant_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[AuditEvent]:
        return self.audit_repo.query(
            tenant_id=tenant_id,
            resource_id=session_id,
            limit=limit
        )


_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service


def set_audit_service(service: AuditService) -> None:
    global _audit_service
    _audit_service = service

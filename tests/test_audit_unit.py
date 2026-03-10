"""Tests for audit module."""
import pytest
from datetime import datetime, timedelta
from app.audit.models import AuditEventType, AuditEvent, AuditQuery
from app.audit.service import AuditService, InMemoryAuditRepository


class TestAuditModels:
    def test_audit_event_type_enum(self):
        assert AuditEventType.USER_LOGIN.value == "user.login"
        assert AuditEventType.USER_LOGOUT.value == "user.logout"
        assert AuditEventType.CHAT_MESSAGE.value == "chat.message"
        assert AuditEventType.POLICY_VIOLATION.value == "policy.violation"
        assert AuditEventType.TENANT_CREATE.value == "tenant.create"

    def test_audit_event_model(self):
        event = AuditEvent(
            tenant_id="tenant_1",
            event_type=AuditEventType.USER_LOGIN,
            actor_id="user_123",
            actor_type="user",
            action="login",
            result="success"
        )
        assert event.tenant_id == "tenant_1"
        assert event.event_type == AuditEventType.USER_LOGIN
        assert event.actor_id == "user_123"

    def test_audit_query_model(self):
        query = AuditQuery(
            tenant_id="tenant_1",
            event_types=[AuditEventType.USER_LOGIN],
            limit=50
        )
        assert query.tenant_id == "tenant_1"
        assert len(query.event_types) == 1
        assert query.limit == 50


class TestAuditService:
    @pytest.fixture
    def audit_service(self):
        return AuditService(InMemoryAuditRepository())

    def test_log_event(self, audit_service):
        event = audit_service.log(
            tenant_id="tenant_1",
            event_type=AuditEventType.USER_LOGIN,
            actor_id="user_123",
            action="login"
        )
        
        assert event.tenant_id == "tenant_1"
        assert event.event_type == AuditEventType.USER_LOGIN
        assert event.actor_id == "user_123"

    def test_log_login_success(self, audit_service):
        event = audit_service.log_login(
            tenant_id="tenant_1",
            user_id="user_123",
            success=True,
            ip_address="192.168.1.1"
        )
        
        assert event.event_type == AuditEventType.USER_LOGIN
        assert event.result == "success"
        assert event.ip_address == "192.168.1.1"

    def test_log_login_failure(self, audit_service):
        event = audit_service.log_login(
            tenant_id="tenant_1",
            user_id="user_123",
            success=False
        )
        
        assert event.result == "failure"

    def test_log_logout(self, audit_service):
        event = audit_service.log_logout(
            tenant_id="tenant_1",
            user_id="user_123",
            ip_address="192.168.1.1"
        )
        
        assert event.event_type == AuditEventType.USER_LOGOUT

    def test_log_chat_message(self, audit_service):
        event = audit_service.log_chat_message(
            tenant_id="tenant_1",
            session_id="session_123",
            actor_id="user_123"
        )
        
        assert event.event_type == AuditEventType.CHAT_MESSAGE
        assert event.resource_id == "session_123"

    def test_log_chat_message_blocked(self, audit_service):
        event = audit_service.log_chat_message(
            tenant_id="tenant_1",
            session_id="session_123",
            actor_id="user_123",
            blocked=True
        )
        
        assert event.event_type == AuditEventType.CHAT_MESSAGE_BLOCKED

    def test_log_policy_violation(self, audit_service):
        event = audit_service.log_policy_violation(
            tenant_id="tenant_1",
            session_id="session_123",
            policy_name="no_profanity",
            message="Profanity detected"
        )
        
        assert event.event_type == AuditEventType.POLICY_VIOLATION
        assert event.result == "blocked"
        assert event.metadata["policy"] == "no_profanity"

    def test_query_by_tenant(self, audit_service):
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN)
        audit_service.log(tenant_id="tenant_2", event_type=AuditEventType.USER_LOGIN)
        
        events = audit_service.query(AuditQuery(tenant_id="tenant_1"))
        
        assert len(events) == 1
        assert events[0].tenant_id == "tenant_1"

    def test_query_by_event_type(self, audit_service):
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN)
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.CHAT_MESSAGE)
        
        events = audit_service.query(AuditQuery(
            tenant_id="tenant_1",
            event_types=[AuditEventType.USER_LOGIN]
        ))
        
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.USER_LOGIN

    def test_query_by_actor(self, audit_service):
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN, actor_id="user_1")
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN, actor_id="user_2")
        
        events = audit_service.query(AuditQuery(
            tenant_id="tenant_1",
            actor_id="user_1"
        ))
        
        assert len(events) == 1
        assert events[0].actor_id == "user_1"

    def test_query_with_limit(self, audit_service):
        for i in range(20):
            audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN)
        
        events = audit_service.query(AuditQuery(tenant_id="tenant_1", limit=5))
        
        assert len(events) == 5

    def test_get_user_activity(self, audit_service):
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN, actor_id="user_123")
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.CHAT_MESSAGE, actor_id="user_123")
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGOUT, actor_id="user_456")
        
        activity = audit_service.get_user_activity("tenant_1", "user_123")
        
        assert len(activity) == 2

    def test_get_session_activity(self, audit_service):
        audit_service.log(
            tenant_id="tenant_1",
            event_type=AuditEventType.CHAT_MESSAGE,
            resource_id="session_123"
        )
        audit_service.log(
            tenant_id="tenant_1",
            event_type=AuditEventType.CHAT_MESSAGE,
            resource_id="session_456"
        )
        
        activity = audit_service.get_session_activity("tenant_1", "session_123")
        
        assert len(activity) == 1
        assert activity[0].resource_id == "session_123"


class TestAuditIsolation:
    @pytest.fixture
    def audit_service(self):
        return AuditService(InMemoryAuditRepository())

    def test_tenant_isolation(self, audit_service):
        audit_service.log(tenant_id="tenant_1", event_type=AuditEventType.USER_LOGIN)
        audit_service.log(tenant_id="tenant_2", event_type=AuditEventType.USER_LOGIN)
        
        events_tenant_1 = audit_service.query(AuditQuery(tenant_id="tenant_1"))
        events_tenant_2 = audit_service.query(AuditQuery(tenant_id="tenant_2"))
        
        assert len(events_tenant_1) == 1
        assert len(events_tenant_2) == 1
        assert events_tenant_1[0].tenant_id == "tenant_1"
        assert events_tenant_2[0].tenant_id == "tenant_2"

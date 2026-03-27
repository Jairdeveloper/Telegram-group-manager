import pytest

from app.agent.actions import (
    ActionContext,
    ActionExecutor,
    ActionParser,
    ActionStateProvider,
    SlotResolver,
)
from app.agent.actions.permissions import ActionPermissionPolicy
from app.agent.actions.registry import ActionRegistry, ActionError
from app.agent.actions.pilot_actions import register_pilot_actions
from app.agent.core import AgentCore, AgentContext
from app.audit.models import AuditQuery
from app.audit.service import AuditService, InMemoryAuditRepository, set_audit_service
from app.manager_bot._config.storage import reset_config_storage, get_config_storage
from app.manager_bot.services import GroupConfigService


@pytest.fixture(autouse=True)
def _isolate_storage_and_audit(monkeypatch):
    reset_config_storage()
    get_config_storage("memory")
    set_audit_service(AuditService(InMemoryAuditRepository()))
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("AGENT_REACT_ENABLED", "false")


@pytest.mark.asyncio
async def test_phase1_group_config_service_updates():
    service = GroupConfigService()
    config = await service.update(
        chat_id=10,
        tenant_id="default",
        updated_by=99,
        updater=lambda cfg: setattr(cfg, "welcome_enabled", True),
    )
    assert config.welcome_enabled is True
    assert config.updated_by == 99


def test_phase1_registry_rejects_duplicates():
    registry = ActionRegistry()
    register_pilot_actions(registry)
    with pytest.raises(ActionError):
        register_pilot_actions(registry)


def test_phase2_permission_policy_alias():
    policy = ActionPermissionPolicy()
    context = ActionContext(chat_id=1, tenant_id="default", user_id=1, roles=["sudo"])
    allowed, _ = policy.check(context, ["admin"])
    assert allowed is True
    denied, reason = policy.check(ActionContext(chat_id=1, tenant_id="default", user_id=1, roles=["user"]), ["admin"])
    assert denied is False
    assert reason == "insufficient_role"


@pytest.mark.asyncio
async def test_phase3_dry_run_and_confirm():
    registry = ActionRegistry()
    register_pilot_actions(registry)
    executor = ActionExecutor(registry)
    context = ActionContext(chat_id=5, tenant_id="default", user_id=1, roles=["admin"])

    preview = await executor.execute("welcome.toggle", context, {"enabled": True}, dry_run=True)
    assert preview.status == "preview"

    confirm = await executor.execute("welcome.set_text", context, {"text": "Hola"})
    assert confirm.status == "confirm"


@pytest.mark.asyncio
async def test_phase4_audit_logs_previous_state():
    registry = ActionRegistry()
    register_pilot_actions(registry)
    executor = ActionExecutor(registry)
    context = ActionContext(chat_id=20, tenant_id="default", user_id=7, roles=["admin"])

    audit = AuditService(InMemoryAuditRepository())
    set_audit_service(audit)

    result = await executor.execute("welcome.toggle", context, {"enabled": True})
    assert result.status == "ok"
    assert result.data.get("previous_state") == {"welcome_enabled": False}
    events = audit.query(AuditQuery(tenant_id="default"))
    assert events
    assert events[0].metadata.get("previous_state") is not None


@pytest.mark.asyncio
async def test_phase5_template_messages():
    registry = ActionRegistry()
    register_pilot_actions(registry)
    executor = ActionExecutor(registry)
    context = ActionContext(chat_id=1, tenant_id="default", user_id=1, roles=[])
    result = await executor.execute("welcome.toggle", context, {"enabled": True})
    assert result.status == "denied"
    assert "No autorizado" in result.message


@pytest.mark.asyncio
async def test_phase6_action_parser_and_slots_and_state():
    parser = ActionParser(llm_enabled=False)
    decision = parser.parse("activar antispam")
    assert decision.action_id == "antispam.toggle"

    registry = ActionRegistry()
    register_pilot_actions(registry)
    resolver = SlotResolver()
    schema = registry.get("welcome.set_text").schema
    resolution = resolver.missing(schema, {})
    assert "text" in resolution.missing_fields

    service = GroupConfigService()
    await service.update(
        chat_id=30,
        tenant_id="default",
        updated_by=1,
        updater=lambda cfg: setattr(cfg, "antispam_enabled", True),
    )
    state_provider = ActionStateProvider()
    state = await state_provider.get_state(
        "antispam.toggle",
        ActionContext(chat_id=30, tenant_id="default", user_id=1, roles=["admin"]),
    )
    assert state["antispam_enabled"] is True


@pytest.mark.asyncio
async def test_phase6_agentcore_action_integration(monkeypatch):
    monkeypatch.setenv("AGENT_ACTIONS_ENABLED", "true")
    monkeypatch.setenv("ACTION_PARSER_LLM_ENABLED", "false")

    agent = AgentCore()
    context = AgentContext(chat_id=40, tenant_id="default", user_id="10", metadata={"roles": ["admin"]})
    response = await agent.process_async("activar antispam", context)
    assert response.source == "action"
    assert "Antispam" in response.response

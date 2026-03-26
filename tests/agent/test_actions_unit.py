import pytest

from app.agent.actions import (
    ActionContext,
    ActionExecutor,
    ActionParser,
    SlotResolver,
)
from app.agent.actions.registry import ActionRegistry
from app.agent.actions.pilot_actions import register_pilot_actions
from app.audit.service import AuditService, InMemoryAuditRepository, set_audit_service
from app.manager_bot._config.storage import reset_config_storage, get_config_storage


@pytest.fixture(autouse=True)
def _isolated_storage_and_audit():
    reset_config_storage()
    get_config_storage("memory")
    set_audit_service(AuditService(InMemoryAuditRepository()))


def _build_executor():
    registry = ActionRegistry()
    register_pilot_actions(registry)
    return ActionExecutor(registry), registry


def test_action_parser_welcome_toggle_on():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Activa bienvenida")
    assert result.action_id == "welcome.toggle"
    assert result.payload["enabled"] is True


def test_action_parser_welcome_set_text():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("bienvenida: Hola equipo")
    assert result.action_id == "welcome.set_text"
    assert result.payload["text"] == "Hola equipo"


def test_slot_resolver_missing_required():
    executor, registry = _build_executor()
    resolver = SlotResolver()
    schema = registry.get("welcome.set_text").schema
    resolution = resolver.missing(schema, {})
    assert "text" in resolution.missing_fields


@pytest.mark.asyncio
async def test_action_executor_permission_denied():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=1, tenant_id="default", user_id=10, roles=[])
    result = await executor.execute("welcome.toggle", context, {"enabled": True})
    assert result.status == "denied"


@pytest.mark.asyncio
async def test_action_executor_dry_run_preview():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=2, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute(
        "welcome.toggle",
        context,
        {"enabled": True},
        dry_run=True,
    )
    assert result.status == "preview"
    assert result.data["current"] is False
    assert result.data["next"] is True


@pytest.mark.asyncio
async def test_action_executor_confirm_required():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=3, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute(
        "welcome.set_text",
        context,
        {"text": "Hola"},
    )
    assert result.status == "confirm"
    assert "preview" in result.data


@pytest.mark.asyncio
async def test_action_executor_execute_and_rollback():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=4, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute("welcome.toggle", context, {"enabled": True})
    assert result.status == "ok"
    assert result.data["welcome_enabled"] is True
    previous_state = result.data.get("previous_state")
    assert previous_state == {"welcome_enabled": False}

    rollback = await executor.rollback(
        "welcome.toggle",
        context,
        {"enabled": True},
        previous_state,
    )
    assert rollback.status == "ok"
    assert rollback.data["welcome_enabled"] is False

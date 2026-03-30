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
    assert result.status == "ok"
    assert "welcome_text" in result.data


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


def test_action_parser_antiflood_toggle():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Activa antiflood")
    assert result.action_id == "antiflood.toggle"
    assert result.payload["enabled"] is True


def test_action_parser_antiflood_limits():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Pon antiflood con 10 mensajes en 5 segundos")
    assert result.action_id == "antiflood.set_limits"
    assert result.payload["limit"] == 10
    assert result.payload["interval"] == 5


def test_action_parser_antiflood_action():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Antiflood con mute")
    assert result.action_id == "antiflood.set_action"
    assert result.payload["action"] == "mute"


def test_action_parser_goodbye_toggle():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Desactiva despedida")
    assert result.action_id == "goodbye.toggle"
    assert result.payload["enabled"] is False


def test_action_parser_goodbye_text():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("despedida: Hasta luego")
    assert result.action_id == "goodbye.set_text"
    assert result.payload["text"] == "Hasta luego"


def test_action_parser_filter_add_word():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Bloquear palabra spam")
    assert result.action_id == "filter.add_word"
    assert result.payload["word"] == "spam"


def test_action_parser_filter_remove_word():
    parser = ActionParser(llm_enabled=False)
    result = parser.parse("Quitar palabra mal")
    assert result.action_id == "filter.remove_word"
    assert result.payload["word"] == "mal"


@pytest.mark.asyncio
async def test_action_executor_antiflood_toggle():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=10, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute("antiflood.toggle", context, {"enabled": True})
    assert result.status == "ok"
    assert result.data["antiflood_enabled"] is True


@pytest.mark.asyncio
async def test_action_executor_antiflood_limits():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=11, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute(
        "antiflood.set_limits",
        context,
        {"limit": 10, "interval": 5},
    )
    assert result.status == "ok"
    assert result.data["antiflood_limit"] == 10
    assert result.data["antiflood_interval"] == 5


@pytest.mark.asyncio
async def test_action_executor_filter_add_word():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=12, tenant_id="default", user_id=10, roles=["admin"])
    result = await executor.execute("filter.add_word", context, {"word": "spam"})
    assert result.status == "ok"
    assert "spam" in result.data["blocked_words"]


@pytest.mark.asyncio
async def test_action_executor_filter_remove_word():
    executor, _ = _build_executor()
    context = ActionContext(chat_id=13, tenant_id="default", user_id=10, roles=["admin"])
    await executor.execute("filter.add_word", context, {"word": "test"})
    result = await executor.execute("filter.remove_word", context, {"word": "test"})
    assert result.status == "ok"
    assert "test" not in result.data["blocked_words"]


@pytest.mark.asyncio
async def test_full_flow_parse_and_execute():
    parser = ActionParser(llm_enabled=False)
    parse_result = parser.parse("Activa antiflood")
    
    assert parse_result.action_id == "antiflood.toggle"
    assert parse_result.payload == {"enabled": True}
    assert parse_result.confidence >= 0.5
    
    executor, _ = _build_executor()
    context = ActionContext(chat_id=20, tenant_id="default", user_id=10, roles=["admin"])
    action_result = await executor.execute(
        parse_result.action_id,
        context,
        parse_result.payload,
    )
    
    assert action_result.status == "ok"
    assert action_result.data["antiflood_enabled"] is True

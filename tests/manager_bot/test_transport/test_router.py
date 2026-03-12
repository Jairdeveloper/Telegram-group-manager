"""Tests for TelegramRouter."""

import pytest
from unittest.mock import Mock
from app.manager_bot.transport.telegram.router import TelegramRouter
from app.manager_bot.registry import ModuleRegistry


class TestTelegramRouter:
    """Tests for TelegramRouter class."""

    @pytest.fixture
    def registry(self):
        reg = ModuleRegistry()
        mock_module = Mock()
        mock_module.is_enabled.return_value = True
        mock_module.get_handlers.return_value = {"test_cmd": lambda x: x}
        reg.register(mock_module)
        return reg

    def test_route_update_classifies_ops_command(self, registry):
        router = TelegramRouter(registry)

        update = {
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "/health"},
        }

        result = router.route_update(update)

        assert result.kind == "ops_command"
        assert result.command == "/health"

    def test_route_update_classifies_enterprise_command(self, registry):
        router = TelegramRouter(registry)

        update = {
            "update_id": 2,
            "message": {"chat": {"id": 123}, "text": "/whoami"},
        }

        result = router.route_update(update)

        assert result.kind == "enterprise_command"
        assert result.command == "/whoami"

    def test_route_update_classifies_chat(self, registry):
        router = TelegramRouter(registry)

        update = {
            "update_id": 3,
            "message": {"chat": {"id": 123}, "text": "Hola bot"},
        }

        result = router.route_update(update)

        assert result.kind == "chat_message"

    def test_route_update_unsupported_message_type(self, registry):
        router = TelegramRouter(registry)

        update = {"inline_query": {"id": "123", "query": "test"}}

        result = router.route_update(update)

        assert result.kind == "unsupported"

    def test_route_update_missing_message(self, registry):
        router = TelegramRouter(registry)

        update = {"update_id": 4}

        result = router.route_update(update)

        assert result.kind == "unsupported"
        assert result.reason == "missing_message"

    def test_route_update_missing_text(self, registry):
        router = TelegramRouter(registry)

        update = {"update_id": 5, "message": {"chat": {"id": 123}, "text": ""}}

        result = router.route_update(update)

        assert result.kind == "unsupported"
        assert result.reason == "missing_text"

    def test_list_available_commands(self, registry):
        router = TelegramRouter(registry)

        commands = router.list_available_commands()

        assert isinstance(commands, list)

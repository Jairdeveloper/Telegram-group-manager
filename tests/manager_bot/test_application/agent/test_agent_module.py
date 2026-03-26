"""Tests for AgentModule."""

import pytest
import os
from unittest.mock import patch, Mock, AsyncMock


class TestAgentModule:
    """Tests for AgentModule class."""

    @patch.dict(os.environ, {"MANAGER_ENABLE_AGENT": "true"})
    def test_agent_module_enabled(self):
        from app.manager_bot._application.agent import AgentModule

        module = AgentModule()
        assert module.is_enabled() is True

    @patch.dict(os.environ, {"MANAGER_ENABLE_AGENT": "false"})
    def test_agent_module_disabled(self):
        from app.manager_bot._application.agent import AgentModule

        module = AgentModule()
        assert module.is_enabled() is False

    def test_agent_module_contract(self):
        from app.manager_bot._application.agent import AgentModule

        module = AgentModule()
        contract = module.contract

        assert contract.name == "agent"
        assert contract.version == "1.0.0"
        assert contract.feature_flag == "MANAGER_ENABLE_AGENT"

    def test_agent_module_has_handlers(self):
        from app.manager_bot._application.agent import AgentModule

        module = AgentModule()
        handlers = module.get_handlers()

        assert "/agent/chat" in handlers

    def test_agent_module_get_gateway(self):
        from app.manager_bot._application.agent import AgentModule, AgentGateway

        module = AgentModule()
        gateway = module.get_gateway()

        assert isinstance(gateway, AgentGateway)

    def test_agent_gateway_default_url(self):
        from app.manager_bot._application.agent import AgentGateway

        gateway = AgentGateway()
        assert gateway.agent_url == "http://localhost:8001"

    def test_agent_gateway_custom_url(self):
        from app.manager_bot._application.agent import AgentGateway

        gateway = AgentGateway(agent_url="http://custom:9000")
        assert gateway.agent_url == "http://custom:9000"

    def test_agent_gateway_is_available(self):
        from app.manager_bot._application.agent import AgentGateway

        gateway = AgentGateway()
        assert gateway.is_available() is True

    def test_agent_gateway_is_available_with_default(self):
        from app.manager_bot._application.agent import AgentGateway

        gateway = AgentGateway(agent_url=None)
        assert gateway.is_available() is True

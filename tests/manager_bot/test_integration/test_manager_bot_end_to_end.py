"""Tests for ManagerBot integration."""

import pytest
import os
from unittest.mock import patch


class TestManagerBotEndToEnd:
    """End-to-end tests for ManagerBot."""

    @patch.dict(
        os.environ,
        {
            "MANAGER_ENABLE_OPS": "true",
            "MANAGER_ENABLE_ENTERPRISE": "true",
            "MANAGER_ENABLE_AGENT": "false",
        },
    )
    def test_manager_bot_initialization(self):
        from app.manager_bot import ManagerBot

        manager = ManagerBot()

        assert manager is not None
        assert manager.registry is not None

    @patch.dict(
        os.environ,
        {
            "MANAGER_ENABLE_OPS": "true",
            "MANAGER_ENABLE_ENTERPRISE": "true",
            "MANAGER_ENABLE_AGENT": "false",
        },
    )
    def test_manager_bot_registers_ops_module(self):
        from app.manager_bot import ManagerBot

        manager = ManagerBot()
        ops_module = manager.registry.get_module("ops")

        assert ops_module is not None

    @patch.dict(
        os.environ,
        {
            "MANAGER_ENABLE_OPS": "true",
            "MANAGER_ENABLE_ENTERPRISE": "true",
            "MANAGER_ENABLE_AGENT": "false",
        },
    )
    def test_manager_bot_registers_enterprise_module(self):
        from app.manager_bot import ManagerBot

        manager = ManagerBot()
        enterprise_module = manager.registry.get_module("enterprise")

        assert enterprise_module is not None

    @patch.dict(
        os.environ,
        {
            "MANAGER_ENABLE_OPS": "true",
            "MANAGER_ENABLE_ENTERPRISE": "true",
            "MANAGER_ENABLE_AGENT": "false",
        },
    )
    def test_manager_bot_get_router(self):
        from app.manager_bot import ManagerBot

        manager = ManagerBot()
        router = manager.get_router()

        assert router is not None

    @patch.dict(
        os.environ,
        {
            "MANAGER_ENABLE_OPS": "true",
            "MANAGER_ENABLE_ENTERPRISE": "true",
            "MANAGER_ENABLE_AGENT": "false",
        },
    )
    def test_manager_bot_list_commands(self):
        from app.manager_bot import ManagerBot

        manager = ManagerBot()
        commands = manager.list_commands()

        assert "ops" in commands
        assert "enterprise" in commands
        assert len(commands["ops"]) == 4
        assert len(commands["enterprise"]) > 0


class TestFeatureFlags:
    """Tests for feature flags."""

    @patch.dict(os.environ, {"MANAGER_ENABLE_OPS": "false"})
    def test_ops_module_respects_feature_flag(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        assert module.is_enabled() is False

    @patch.dict(os.environ, {"MANAGER_ENABLE_ENTERPRISE": "false"})
    def test_enterprise_module_respects_feature_flag(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        assert module.is_enabled() is False

    @patch.dict(os.environ, {"MANAGER_ENABLE_AGENT": "true"})
    def test_agent_module_respects_feature_flag(self):
        from app.manager_bot.application.agent import AgentModule

        module = AgentModule()
        assert module.is_enabled() is True

"""Tests for OpsModule."""

import pytest
import os
from unittest.mock import patch


class TestOpsModule:
    """Tests for OpsModule class."""

    @patch.dict(os.environ, {"MANAGER_ENABLE_OPS": "true"})
    def test_ops_module_enabled(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        assert module.is_enabled() is True

    @patch.dict(os.environ, {"MANAGER_ENABLE_OPS": "false"})
    def test_ops_module_disabled(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        assert module.is_enabled() is False

    def test_ops_module_contract(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        contract = module.contract

        assert contract.name == "ops"
        assert contract.version == "1.0.0"
        assert contract.feature_flag == "MANAGER_ENABLE_OPS"
        assert "/health" in contract.routes
        assert "/e2e" in contract.routes

    def test_ops_module_has_handlers(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        handlers = module.get_handlers()

        assert "/health" in handlers
        assert "/e2e" in handlers
        assert "/webhookinfo" in handlers
        assert "/logs" in handlers

    def test_ops_module_health_check(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        health = module.health_check()

        assert health["status"] == "ok"
        assert health["module"] == "ops"
        assert "/health" in health["commands"]

    def test_ops_command_descriptions(self):
        from app.manager_bot.application.ops import OpsModule

        module = OpsModule()
        descriptions = module.get_command_descriptions()

        assert "/health" in descriptions
        assert "Estado" in descriptions["/health"] or "API" in descriptions["/health"]

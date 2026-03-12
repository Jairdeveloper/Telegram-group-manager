"""Tests for EnterpriseModule."""

import pytest
import os
from unittest.mock import patch


class TestEnterpriseModule:
    """Tests for EnterpriseModule class."""

    @patch.dict(os.environ, {"MANAGER_ENABLE_ENTERPRISE": "true"})
    def test_enterprise_module_enabled(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        assert module.is_enabled() is True

    @patch.dict(os.environ, {"MANAGER_ENABLE_ENTERPRISE": "false"})
    def test_enterprise_module_disabled(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        assert module.is_enabled() is False

    def test_enterprise_module_contract(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        contract = module.contract

        assert contract.name == "enterprise"
        assert contract.version == "1.0.0"
        assert contract.feature_flag == "MANAGER_ENABLE_ENTERPRISE"
        assert "/whoami" in contract.routes

    def test_enterprise_module_has_handlers(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        handlers = module.get_handlers()

        assert len(handlers) > 0
        assert "/whoami" in handlers

    def test_enterprise_module_health_check(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()
        health = module.health_check()

        assert health["status"] == "ok"
        assert health["module"] == "enterprise"

    def test_get_required_permissions(self):
        from app.manager_bot.application.enterprise import EnterpriseModule

        module = EnterpriseModule()

        perms = module.get_required_permissions("/whoami")
        assert isinstance(perms, list)

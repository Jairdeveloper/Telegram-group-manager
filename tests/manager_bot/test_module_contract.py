"""Tests for ModuleContract."""

import pytest
from pydantic import ValidationError
from app.manager_bot.core import ModuleContract


class TestModuleContract:
    """Tests for ModuleContract model."""

    def test_valid_contract(self):
        contract = ModuleContract(
            name="ops",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_OPS",
            routes=["/health", "/e2e"],
            permissions=["admin"],
        )

        assert contract.name == "ops"
        assert contract.version == "1.0.0"
        assert contract.feature_flag == "MANAGER_ENABLE_OPS"
        assert contract.routes == ["/health", "/e2e"]
        assert contract.permissions == ["admin"]

    def test_invalid_contract_missing_name(self):
        with pytest.raises(ValidationError):
            ModuleContract(
                version="1.0.0",
                feature_flag="MANAGER_ENABLE_TEST",
                routes=[],
                permissions=[],
            )

    def test_invalid_contract_missing_version(self):
        with pytest.raises(ValidationError):
            ModuleContract(
                name="test",
                feature_flag="MANAGER_ENABLE_TEST",
                routes=[],
                permissions=[],
            )

    def test_contract_with_empty_routes(self):
        contract = ModuleContract(
            name="test",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_TEST",
            routes=[],
            permissions=[],
        )

        assert contract.name == "test"
        assert contract.routes == []

    def test_contract_with_multiple_permissions(self):
        contract = ModuleContract(
            name="test",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_TEST",
            routes=["/test"],
            permissions=["user", "admin", "moderator"],
        )

        assert len(contract.permissions) == 3
        assert "admin" in contract.permissions

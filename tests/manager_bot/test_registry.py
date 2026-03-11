"""Tests for ManagerBot registry."""

import pytest
from unittest.mock import Mock
from app.manager_bot.registry import ModuleRegistry
from app.manager_bot.core import Module


class FakeModule(Module):
    """Módulo de prueba."""

    def __init__(self, name: str = "test", enabled: bool = True):
        self._name = name
        self._enabled = enabled
        self._contract = Mock()
        self._contract.name = name
        self._contract.feature_flag = "TEST_ENABLED"

    @property
    def contract(self):
        return self._contract

    def is_enabled(self) -> bool:
        return self._enabled

    def get_handlers(self) -> dict:
        return {"test_handler": lambda x: x}


class TestModuleRegistry:
    """Tests for ModuleRegistry class."""

    def test_register_module(self):
        registry = ModuleRegistry()
        module = FakeModule("test_module")

        registry.register(module)

        assert registry.get_module("test_module") == module

    def test_get_module_not_found(self):
        registry = ModuleRegistry()

        assert registry.get_module("nonexistent") is None

    def test_is_enabled_when_module_exists(self):
        registry = ModuleRegistry()
        module = FakeModule("test", enabled=True)
        registry.register(module)

        assert registry.is_enabled("test") is True

    def test_is_enabled_when_module_disabled(self):
        registry = ModuleRegistry()
        module = FakeModule("test", enabled=False)
        registry.register(module)

        assert registry.is_enabled("test") is False

    def test_is_enabled_when_module_not_exists(self):
        registry = ModuleRegistry()

        assert registry.is_enabled("nonexistent") is False

    def test_list_modules(self):
        registry = ModuleRegistry()
        registry.register(FakeModule("module1"))
        registry.register(FakeModule("module2"))

        modules = registry.list_modules()

        assert "module1" in modules
        assert "module2" in modules
        assert len(modules) == 2

    def test_list_enabled_modules(self):
        registry = ModuleRegistry()
        registry.register(FakeModule("enabled_module", enabled=True))
        registry.register(FakeModule("disabled_module", enabled=False))

        enabled = registry.list_enabled_modules()

        assert len(enabled) == 1
        assert enabled[0].contract.name == "enabled_module"

    def test_get_all_handlers(self):
        registry = ModuleRegistry()
        registry.register(FakeModule("module1", enabled=True))
        registry.register(FakeModule("module2", enabled=False))

        handlers = registry.get_all_handlers()

        assert "test_handler" in handlers
        assert len(handlers) == 1

    def test_unregister_module(self):
        registry = ModuleRegistry()
        module = FakeModule("test")
        registry.register(module)

        registry.unregister("test")

        assert registry.get_module("test") is None

    def test_register_duplicate_module_raises(self):
        registry = ModuleRegistry()
        module = FakeModule("test")
        registry.register(module)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(FakeModule("test"))

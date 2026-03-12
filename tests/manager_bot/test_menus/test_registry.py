"""Unit tests for menu registry."""

import pytest
from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.menus.registry import MenuRegistry


class TestMenuRegistry:
    """Tests for MenuRegistry class."""

    def test_create_empty_registry(self):
        registry = MenuRegistry()
        assert registry.list_menus() == []

    def test_register_menu(self):
        registry = MenuRegistry()
        menu = MenuDefinition(menu_id="main", title="Main Menu")
        
        registry.register(menu)
        
        assert "main" in registry.list_menus()
        assert registry.get("main") is menu

    def test_register_duplicate_raises_error(self):
        registry = MenuRegistry()
        menu1 = MenuDefinition(menu_id="main", title="Main")
        menu2 = MenuDefinition(menu_id="main", title="Main 2")
        
        registry.register(menu1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(menu2)

    def test_get_nonexistent_menu(self):
        registry = MenuRegistry()
        
        assert registry.get("nonexistent") is None

    def test_unregister_existing_menu(self):
        registry = MenuRegistry()
        menu = MenuDefinition(menu_id="main", title="Main")
        
        registry.register(menu)
        result = registry.unregister("main")
        
        assert result is True
        assert "main" not in registry.list_menus()

    def test_unregister_nonexistent_menu(self):
        registry = MenuRegistry()
        
        result = registry.unregister("nonexistent")
        
        assert result is False

    def test_clear_all_menus(self):
        registry = MenuRegistry()
        
        registry.register(MenuDefinition(menu_id="main", title="Main"))
        registry.register(MenuDefinition(menu_id="sub", title="Sub"))
        
        registry.clear()
        
        assert registry.list_menus() == []

"""Unit tests for navigation manager."""

import pytest
from app.manager_bot.menus.navigation import NavigationManager, NavigationContext


class TestNavigationManager:
    """Tests for NavigationManager class."""

    def test_create_empty_manager(self):
        manager = NavigationManager()
        assert manager.get_current(123) is None

    def test_push_menu_creates_context(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        
        ctx = manager.get_context(123)
        assert ctx is not None
        assert ctx.user_id == 123
        assert ctx.chat_id == 456
        assert ctx.current_menu == "main"
        assert ctx.menu_stack == []

    def test_push_menu_adds_to_stack(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        manager.push_menu(123, "settings", 456)
        
        ctx = manager.get_context(123)
        assert ctx.current_menu == "settings"
        assert "main" in ctx.menu_stack

    def test_pop_menu_returns_previous(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        manager.push_menu(123, "settings", 456)
        
        prev = manager.pop_menu(123)
        
        assert prev == "main"
        assert manager.get_current(123) == "main"

    def test_pop_menu_empty_stack_returns_none(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        
        prev = manager.pop_menu(123)
        
        assert prev is None

    def test_go_home_clears_stack(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        manager.push_menu(123, "settings", 456)
        manager.push_menu(123, "filters", 456)
        
        manager.go_home(123)
        
        ctx = manager.get_context(123)
        assert ctx.current_menu == "main"
        assert ctx.menu_stack == []

    def test_get_current_without_context(self):
        manager = NavigationManager()
        
        assert manager.get_current(999) is None

    def test_set_and_get_metadata(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        manager.set_metadata(123, "filter_id", "abc123")
        
        assert manager.get_metadata(123, "filter_id") == "abc123"

    def test_get_metadata_without_context(self):
        manager = NavigationManager()
        
        assert manager.get_metadata(999, "key") is None

    def test_clear_context(self):
        manager = NavigationManager()
        
        manager.push_menu(123, "main", 456)
        manager.clear_context(123)
        
        assert manager.get_context(123) is None


class TestNavigationContext:
    """Tests for NavigationContext dataclass."""

    def test_create_context(self):
        ctx = NavigationContext(
            user_id=123,
            chat_id=456,
            current_menu="main"
        )
        
        assert ctx.user_id == 123
        assert ctx.chat_id == 456
        assert ctx.current_menu == "main"
        assert ctx.menu_stack == []
        assert ctx.metadata == {}

    def test_context_with_stack(self):
        ctx = NavigationContext(
            user_id=123,
            chat_id=456,
            current_menu="settings",
            menu_stack=["main", "filters"]
        )
        
        assert ctx.menu_stack == ["main", "filters"]

    def test_context_with_metadata(self):
        ctx = NavigationContext(
            user_id=123,
            chat_id=456,
            current_menu="main",
            metadata={"key": "value"}
        )
        
        assert ctx.metadata["key"] == "value"

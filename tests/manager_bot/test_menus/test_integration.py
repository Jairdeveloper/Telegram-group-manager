"""Integration tests for menu system."""

import pytest
from unittest.mock import Mock

from app.manager_bot._menus import MenuRegistry, register_all_menus
from app.manager_bot._menus.base import MenuDefinition, MenuAction
from app.manager_bot._menus.navigation import NavigationManager
from app.manager_bot.config.storage import InMemoryConfigStorage
from app.manager_bot.config.group_config import GroupConfig
from app.manager_bot.transport.telegram.callback_router import CallbackRouter


class TestMenuIntegration:
    """Integration tests for complete menu flows."""

    def test_menu_registration(self):
        """Test that all menus are registered."""
        reg = MenuRegistry()
        register_all_menus(reg)
        
        menus = reg.list_menus()
        
        assert "main" in menus
        assert "mod" in menus
        assert "antispam" in menus
        assert "filters" in menus
        assert "welcome" in menus

    def test_navigation_push_pop(self):
        """Test navigation push and pop."""
        nav = NavigationManager()
        
        nav.push_menu(123, "main", 456)
        assert nav.get_current(123) == "main"
        
        nav.push_menu(123, "mod", 456)
        assert nav.get_current(123) == "mod"
        
        prev = nav.pop_menu(123)
        assert prev == "main"
        
        nav.go_home(123)
        assert nav.get_current(123) == "main"

    def test_config_storage_crud(self):
        """Test config storage operations."""
        storage = InMemoryConfigStorage()
        
        import asyncio
        
        async def run_test():
            config = GroupConfig(chat_id=123, tenant_id="test")
            config.antiflood_enabled = True
            
            await storage.set(config)
            
            retrieved = await storage.get(123)
            
            assert retrieved is not None
            assert retrieved.chat_id == 123
            assert retrieved.antiflood_enabled is True
            
            await storage.delete(123)
            
            deleted = await storage.get(123)
            assert deleted is None
        
        asyncio.run(run_test())

    def test_antispam_toggle(self):
        """Test antispam toggle via feature."""
        storage = InMemoryConfigStorage()
        
        import asyncio
        
        async def run_test():
            config = GroupConfig(chat_id=123, tenant_id="test")
            await storage.set(config)
            
            retrieved = await storage.get(123)
            assert retrieved.antispam_enabled is False
            
            retrieved.antispam_enabled = True
            await storage.set(retrieved)
            
            updated = await storage.get(123)
            assert updated.antispam_enabled is True
        
        asyncio.run(run_test())

    def test_callback_pattern_registration(self):
        """Test callback pattern registration."""
        router = CallbackRouter()
        
        matched = []
        
        async def handler(callback, bot, data):
            matched.append(data)
        
        router.register_prefix("antispam:", handler)
        
        patterns = router.list_handlers()
        assert any("antispam:" in p for p in patterns.keys())

    def test_menu_to_keyboard(self):
        """Test menu to keyboard conversion."""
        reg = MenuRegistry()
        register_all_menus(reg)
        
        menu = reg.get("main")
        assert menu is not None
        
        keyboard = menu.to_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0

    def test_navigation_context(self):
        """Test navigation context with metadata."""
        nav = NavigationManager()
        
        nav.push_menu(123, "main", 456)
        
        nav.set_metadata(123, "filter_count", 5)
        metadata = nav.get_metadata(123, "filter_count")
        
        assert metadata == 5

    def test_menu_back_navigation(self):
        """Test back button in menus."""
        reg = MenuRegistry()
        register_all_menus(reg)
        
        mod_menu = reg.get("mod")
        assert mod_menu is not None
        
        has_back = any(
            "nav:back" in action.callback_data
            for row in mod_menu.rows
            for action in row.actions
        )
        assert has_back

    def test_filter_crud(self):
        """Test filter CRUD operations."""
        storage = InMemoryConfigStorage()
        
        import asyncio
        
        async def run_test():
            config = GroupConfig(chat_id=123, tenant_id="test")
            config.filters = [{"pattern": "badword", "response": "Filtered"}]
            
            await storage.set(config)
            
            retrieved = await storage.get(123)
            assert len(retrieved.filters) == 1
            assert retrieved.filters[0]["pattern"] == "badword"
            
            retrieved.filters = []
            await storage.set(retrieved)
            
            updated = await storage.get(123)
            assert len(updated.filters) == 0
        
        asyncio.run(run_test())

    def test_welcome_config(self):
        """Test welcome configuration."""
        storage = InMemoryConfigStorage()
        
        import asyncio
        
        async def run_test():
            config = GroupConfig(chat_id=123, tenant_id="test")
            config.welcome_enabled = True
            config.welcome_text = "Welcome!"
            
            await storage.set(config)
            
            retrieved = await storage.get(123)
            assert retrieved.welcome_enabled is True
            assert retrieved.welcome_text == "Welcome!"
        
        asyncio.run(run_test())


class TestRateLimiter:
    """Tests for rate limiter."""

    def test_rate_limit_allows_within_limit(self):
        """Test rate limiter allows requests within limit."""
        from app.manager_bot.config.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_calls=5, window_seconds=60)
        
        for _ in range(5):
            assert limiter.is_allowed(123) is True

    def test_rate_limit_blocks_excess(self):
        """Test rate limiter blocks excess requests."""
        from app.manager_bot.config.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_calls=3, window_seconds=60)
        
        assert limiter.is_allowed(123) is True
        assert limiter.is_allowed(123) is True
        assert limiter.is_allowed(123) is True
        assert limiter.is_allowed(123) is False

    def test_rate_limit_different_users(self):
        """Test rate limit per user."""
        from app.manager_bot.config.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_calls=1, window_seconds=60)
        
        assert limiter.is_allowed(123, "action1") is True
        assert limiter.is_allowed(123, "action1") is False
        
        assert limiter.is_allowed(456, "action1") is True


class TestCacheMetrics:
    """Tests for cache metrics."""

    def test_cache_metrics_initial(self):
        """Test initial cache metrics."""
        from app.manager_bot.config.rate_limiter import CacheMetrics
        
        metrics = CacheMetrics()
        
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.hit_rate == 0.0

    def test_cache_metrics_calculation(self):
        """Test cache hit rate calculation."""
        from app.manager_bot.config.rate_limiter import CacheMetrics
        
        metrics = CacheMetrics(hits=80, misses=20)
        
        assert metrics.total == 100
        assert metrics.hit_rate == 0.8

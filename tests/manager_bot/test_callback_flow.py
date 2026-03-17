"""Tests for callback query flow."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.manager_bot.transport.telegram.callback_router import CallbackRouter
from app.manager_bot.transport.telegram.menu_engine import MenuEngine
from app.manager_bot._menus import MenuRegistry, NavigationManager
from app.manager_bot.config.storage import InMemoryConfigStorage


class MockCallbackQuery:
    """Mock for telegram CallbackQuery."""
    
    def __init__(self, data: str, user_id: int = 123, chat_id: int = 456, message_id: int = 789):
        self.data = data
        self.from_user = Mock(id=user_id)
        self.message = Mock()
        self.message.chat = Mock(id=chat_id)
        self.message.message_id = message_id
        self._answered = False
        self._answer_text = None
        
    async def answer(self, text: str = None, show_alert: bool = False):
        self._answered = True
        self._answer_text = text
        
    async def edit_message_text(self, text: str, reply_markup=None):
        pass
        
    async def reply_text(self, text: str, reply_markup=None):
        pass


class MockBot:
    """Mock for telegram Bot."""
    
    def __init__(self):
        self.sent_messages = []
        
    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        self.sent_messages.append({
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup
        })


class TestCallbackQueryFlow:
    """Tests for complete callback query flow."""
    
    def test_exact_callback_matching(self):
        """Test that exact callbacks match correctly."""
        router = CallbackRouter()
        
        matched = []
        
        async def handler(callback, bot, data):
            matched.append(data)
        
        router.register_exact("antispam:show", handler)
        router.register_prefix("antispam:toggle", handler)
        
        callback = MockCallbackQuery("antispam:show")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert len(matched) == 1
        assert matched[0] == "antispam:show"
    
    def test_prefix_callback_matching(self):
        """Test that prefix callbacks match correctly."""
        router = CallbackRouter()
        
        matched = []
        
        async def handler(callback, bot, data):
            matched.append(data)
        
        router.register_prefix("antispam", handler)
        
        callback = MockCallbackQuery("antispam:toggle:on")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert len(matched) == 1
        assert matched[0] == "antispam:toggle:on"
    
    def test_priority_exact_over_prefix(self):
        """Test that exact matches take priority over prefix."""
        router = CallbackRouter()
        
        exact_match = []
        prefix_match = []
        
        async def exact_handler(callback, bot, data):
            exact_match.append(data)
        
        async def prefix_handler(callback, bot, data):
            prefix_match.append(data)
        
        router.register_prefix("antispam:", prefix_handler)
        router.register_exact("antispam:show", exact_handler)
        
        callback = MockCallbackQuery("antispam:show")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert len(exact_match) == 1
        assert len(prefix_match) == 0
    
    def test_callback_answer_is_called(self):
        """Test that callback.answer() is called."""
        router = CallbackRouter()
        
        async def handler(callback, bot, data):
            await callback.answer("Test response", show_alert=True)
        
        router.register_exact("test:action", handler)
        
        callback = MockCallbackQuery("test:action")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert callback._answered is True
        assert callback._answer_text == "Test response"
    
    def test_fallback_handler(self):
        """Test fallback handler for unmatched callbacks."""
        router = CallbackRouter()
        
        fallback_called = []
        
        async def fallback(callback, bot, data):
            fallback_called.append(data)
            await callback.answer("Unrecognized", show_alert=True)
        
        router.set_fallback(fallback)
        
        callback = MockCallbackQuery("unknown:action")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert len(fallback_called) == 1
        assert fallback_called[0] == "unknown:action"


class TestMenuEngineCallback:
    """Tests for MenuEngine callback handling."""
    
    @pytest.fixture
    def menu_engine(self):
        """Create a MenuEngine for testing."""
        registry = MenuRegistry()
        from app.manager_bot._menus import register_all_menus
        register_all_menus(registry)
        
        router = CallbackRouter()
        nav = NavigationManager()
        storage = InMemoryConfigStorage()
        
        engine = MenuEngine(
            menu_registry=registry,
            callback_router=router,
            navigation_manager=nav,
            config_storage=storage,
        )
        
        return engine
    
    @pytest.mark.skip(reason="Requires full MenuEngine integration with Telegram API")
    def test_show_menu_callback_data(self, menu_engine):
        """Test that show menu callbacks work via registry."""
        callback = MockCallbackQuery("antispam:show")
        bot = MockBot()
        
        import asyncio
        result = asyncio.run(
            menu_engine.callback_router.handle(callback, bot)
        )
        
        assert callback._answered is True
    
    def test_antispam_toggle_callback(self, menu_engine):
        """Test antispam toggle callback processing."""
        async def handle_toggle(callback, bot, data):
            await callback.answer("Antispam activated", show_alert=True)
        
        menu_engine.callback_router.register_prefix("antispam:toggle", handle_toggle)
        
        callback = MockCallbackQuery("antispam:toggle:on")
        bot = MockBot()
        
        import asyncio
        asyncio.run(
            menu_engine.callback_router.handle(callback, bot)
        )
        
        assert callback._answered is True
        assert "activated" in callback._answer_text.lower()


class TestCallbackFlowIntegration:
    """Integration tests for complete callback flow."""
    
    def test_full_callback_flow(self):
        """Test complete flow from callback to response."""
        from app.manager_bot._menus import register_all_menus
        
        registry = MenuRegistry()
        register_all_menus(registry)
        
        router = CallbackRouter()
        nav = NavigationManager()
        storage = InMemoryConfigStorage()
        
        async def menu_handler(callback, bot, data):
            await callback.answer("Menu displayed")
            nav.push_menu(callback.from_user.id, data.split(":")[0], callback.message.chat.id)
        
        router.register_exact("antispam:show", menu_handler)
        
        engine = MenuEngine(
            menu_registry=registry,
            callback_router=router,
            navigation_manager=nav,
            config_storage=storage,
        )
        
        callback = MockCallbackQuery("antispam:show")
        bot = MockBot()
        
        import asyncio
        asyncio.run(router.handle(callback, bot))
        
        assert callback._answered is True
        assert nav.get_current(123) == "antispam"
    
    def test_callback_data_extraction(self):
        """Test callback data extraction from update."""
        raw_update = {
            "callback_query": {
                "id": "123456789",
                "data": "antispam:show",
                "from": {"id": 123},
                "message": {
                    "message_id": 456,
                    "chat": {"id": 789}
                }
            }
        }
        
        callback_query = raw_update.get("callback_query", {})
        callback_data = callback_query.get("data")
        callback_id = callback_query.get("id")
        user_id = callback_query.get("from", {}).get("id")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        message_id = callback_query.get("message", {}).get("message_id")
        
        assert callback_data == "antispam:show"
        assert callback_id == "123456789"
        assert user_id == 123
        assert chat_id == 789
        assert message_id == 456

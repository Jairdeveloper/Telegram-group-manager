"""Tests para runtime y transport."""

import pytest


def test_application_builder_import():
    """Test que los módulos de runtime se pueden importar."""
    from robot_ptb_compat.runtime import CompatApplicationBuilder
    from robot_ptb_compat.runtime import WebhookRunner
    from robot_ptb_compat.runtime import PollingRunner
    from robot_ptb_compat.transport import TelegramClient
    
    assert CompatApplicationBuilder is not None
    assert WebhookRunner is not None
    assert PollingRunner is not None
    assert TelegramClient is not None


def test_compat_application_builder_init():
    """Test de inicialización de CompatApplicationBuilder."""
    from robot_ptb_compat.runtime.application_builder import CompatApplicationBuilder
    
    builder = CompatApplicationBuilder(token="test_token")
    
    assert builder._token == "test_token"


def test_compat_application_builder_token():
    """Test del método token de CompatApplicationBuilder."""
    from robot_ptb_compat.runtime.application_builder import CompatApplicationBuilder
    
    builder = CompatApplicationBuilder()
    builder2 = builder.token("new_token")
    
    assert builder2._token == "new_token"


def test_compat_application_builder_manager_bot():
    """Test del método manager_bot de CompatApplicationBuilder."""
    from robot_ptb_compat.runtime.application_builder import CompatApplicationBuilder
    
    class MockManagerBot:
        pass
    
    builder = CompatApplicationBuilder()
    builder2 = builder.manager_bot(MockManagerBot())
    
    assert builder2._manager_bot is not None


def test_compat_application_builder_add_handler():
    """Test del método add_handler de CompatApplicationBuilder."""
    from robot_ptb_compat.runtime.application_builder import CompatApplicationBuilder
    
    class MockHandler:
        pass
    
    builder = CompatApplicationBuilder()
    builder2 = builder.add_handler(MockHandler())
    
    assert len(builder2._custom_handlers) == 1


def test_compat_application_builder_build():
    """Test del método build de CompatApplicationBuilder."""
    from robot_ptb_compat.runtime.application_builder import CompatApplicationBuilder
    
    builder = CompatApplicationBuilder(token="test_token")
    app = builder.build()
    
    assert app is not None


def test_fallback_application():
    """Test de FallbackApplication."""
    from robot_ptb_compat.runtime.application_builder import FallbackApplication
    
    app = FallbackApplication(token="test_token")
    
    assert app.token == "test_token"
    assert app._running == False
    
    app.add_handler("handler")
    assert len(app.handlers) == 1
    
    app.add_middleware("middleware")
    assert len(app.middlewares) == 1


def test_telegram_client_init():
    """Test de inicialización de TelegramClient."""
    from robot_ptb_compat.transport.telegram_client import TelegramClient
    
    client = TelegramClient(token="test_token")
    
    assert client.token == "test_token"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

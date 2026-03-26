"""Tests para handlers."""

import pytest
import asyncio


def test_base_adapter_import():
    """Test que los handlers se pueden importar."""
    from robot_ptb_compat.compat.handlers import BaseHandlerAdapter
    from robot_ptb_compat.compat.handlers import CommandAdapter
    from robot_ptb_compat.compat.handlers import MessageAdapter
    from robot_ptb_compat.compat.handlers import CallbackAdapter
    from robot_ptb_compat.compat.handlers import FiltersAdapter
    
    assert BaseHandlerAdapter is not None
    assert CommandAdapter is not None
    assert MessageAdapter is not None
    assert CallbackAdapter is not None
    assert FiltersAdapter is not None


def test_command_adapter_init():
    """Test de inicialización de CommandAdapter."""
    from robot_ptb_compat.compat.handlers.command_adapter import CommandAdapter
    
    async def dummy_callback(update, context):
        return "ok"
    
    adapter = CommandAdapter(
        commands=["start", "help"],
        callback=dummy_callback
    )
    
    assert "start" in adapter.get_commands()
    assert "help" in adapter.get_commands()


def test_command_adapter_add_command():
    """Test de agregar comando a CommandAdapter."""
    from robot_ptb_compat.compat.handlers.command_adapter import CommandAdapter
    
    async def dummy_callback(update, context):
        return "ok"
    
    adapter = CommandAdapter(commands=["start"], callback=dummy_callback)
    adapter.add_command("about")
    
    assert "about" in adapter.get_commands()


def test_command_dispatcher():
    """Test de CommandDispatcher."""
    from robot_ptb_compat.compat.handlers.command_adapter import CommandDispatcher
    
    dispatcher = CommandDispatcher()
    
    async def dummy_callback(update, context):
        return "ok"
    
    dispatcher.register(["start"], dummy_callback)
    
    assert "start" in dispatcher.get_registered_commands()


def test_message_adapter_init():
    """Test de inicialización de MessageAdapter."""
    from robot_ptb_compat.compat.handlers.message_adapter import MessageAdapter
    
    async def dummy_callback(update, context):
        return "ok"
    
    adapter = MessageAdapter(
        callback=dummy_callback,
        message_types=["text", "photo"]
    )
    
    assert "text" in adapter.get_message_types()
    assert "photo" in adapter.get_message_types()


def test_message_filters():
    """Test de MessageFilters."""
    from robot_ptb_compat.compat.handlers.message_adapter import MessageFilters
    
    class MockUpdate:
        class message:
            text = "Hello"
    
    update = MockUpdate()
    assert MessageFilters.text(update) == True


def test_filters_adapter():
    """Test de FiltersAdapter."""
    from robot_ptb_compat.compat.handlers.filters_adapter import FiltersAdapter
    
    text_filter = FiltersAdapter.text()
    assert text_filter is not None
    
    command_filter = FiltersAdapter.command()
    assert command_filter is not None
    
    photo_filter = FiltersAdapter.photo()
    assert photo_filter is not None


def test_filters_combined():
    """Test de filtros combinados."""
    from robot_ptb_compat.compat.handlers.filters_adapter import FiltersAdapter
    
    combined = FiltersAdapter.text() & FiltersAdapter.command()
    assert combined is not None
    
    combined_or = FiltersAdapter.text() | FiltersAdapter.photo()
    assert combined_or is not None
    
    inverted = ~FiltersAdapter.text()
    assert inverted is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

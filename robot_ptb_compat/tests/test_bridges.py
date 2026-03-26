"""Tests para bridges."""

import pytest


def test_update_bridge_import():
    """Test que los bridges se pueden importar."""
    from robot_ptb_compat.bridge import UpdateBridge
    from robot_ptb_compat.bridge import MessageBridge
    from robot_ptb_compat.bridge import UserBridge
    from robot_ptb_compat.bridge import ChatBridge
    from robot_ptb_compat.bridge import CallbackBridge
    from robot_ptb_compat.bridge import ContextBridge
    
    assert UpdateBridge is not None
    assert MessageBridge is not None
    assert UserBridge is not None
    assert ChatBridge is not None
    assert CallbackBridge is not None
    assert ContextBridge is not None


def test_user_bridge_to_simple_dict():
    """Test de UserBridge.to_simple_dict."""
    from robot_ptb_compat.bridge.user_bridge import UserBridge
    
    class MockUser:
        id = 12345
    
    result = UserBridge.to_simple_dict(MockUser())
    assert result == {"id": 12345}


def test_user_bridge_to_internal():
    """Test de UserBridge.to_internal."""
    from robot_ptb_compat.bridge.user_bridge import UserBridge
    
    result = UserBridge.to_internal(None)
    assert result is None


def test_chat_bridge_to_simple_dict():
    """Test de ChatBridge.to_simple_dict."""
    from robot_ptb_compat.bridge.chat_bridge import ChatBridge
    
    class MockChat:
        id = 67890
    
    result = ChatBridge.to_simple_dict(MockChat())
    assert result == {"id": 67890}


def test_chat_bridge_to_internal():
    """Test de ChatBridge.to_internal."""
    from robot_ptb_compat.bridge.chat_bridge import ChatBridge
    
    result = ChatBridge.to_internal(None)
    assert result is None


def test_context_bridge_extract_chat_id():
    """Test de ContextBridge.extract_chat_id."""
    from robot_ptb_compat.bridge.context_bridge import ContextBridge
    
    class MockContext:
        effective_chat = type('obj', (object,), {'id': 123})()
    
    result = ContextBridge.extract_chat_id(MockContext())
    assert result == 123


def test_context_bridge_extract_user_id():
    """Test de ContextBridge.extract_user_id."""
    from robot_ptb_compat.bridge.context_bridge import ContextBridge
    
    class MockContext:
        effective_user = type('obj', (object,), {'id': 456})()
    
    result = ContextBridge.extract_user_id(MockContext())
    assert result == 456


def test_context_bridge_extract_message_id():
    """Test de ContextBridge.extract_message_id."""
    from robot_ptb_compat.bridge.context_bridge import ContextBridge
    
    class MockContext:
        effective_message = type('obj', (object,), {'message_id': 789})()
    
    result = ContextBridge.extract_message_id(MockContext())
    assert result == 789


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

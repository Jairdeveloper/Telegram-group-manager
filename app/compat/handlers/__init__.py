"""Compat handlers using robot-ptb-compat."""

from typing import Any, Callable, Dict, Optional

try:
    from robot_ptb_compat.compat.handlers import (
        CommandAdapter,
        MessageAdapter,
        CallbackAdapter,
        FiltersAdapter,
    )
    from robot_ptb_compat.bridge import UpdateBridge, MessageBridge
    HAS_ROBOT_PTB_COMPAT = True
except ImportError:
    HAS_ROBOT_PTB_COMPAT = False
    CommandAdapter = None
    MessageAdapter = None
    CallbackAdapter = None
    FiltersAdapter = None
    UpdateBridge = None
    MessageBridge = None


__all__ = [
    "CommandAdapter",
    "MessageAdapter", 
    "CallbackAdapter",
    "FiltersAdapter",
    "UpdateBridge",
    "MessageBridge",
    "HAS_ROBOT_PTB_COMPAT",
    "create_command_handler",
    "create_message_handler",
    "create_callback_handler",
]


def create_command_handler(
    commands: list[str],
    callback: Callable,
    **kwargs
):
    """Create a command handler using robot-ptb-compat if available.
    
    Args:
        commands: List of commands (without /)
        callback: Callback function
        **kwargs: Additional arguments
        
    Returns:
        CommandAdapter or legacy handler
    """
    if HAS_ROBOT_PTB_COMPAT and CommandAdapter:
        return CommandAdapter(commands=commands, callback=callback, **kwargs)
    
    return None


def create_message_handler(
    callback: Callable,
    message_types: Optional[list[str]] = None,
    **kwargs
):
    """Create a message handler using robot-ptb-compat if available.
    
    Args:
        callback: Callback function
        message_types: List of message types to handle
        **kwargs: Additional arguments
        
    Returns:
        MessageAdapter or legacy handler
    """
    if HAS_ROBOT_PTB_COMPAT and MessageAdapter:
        return MessageAdapter(
            callback=callback,
            message_types=message_types or ["text"],
            **kwargs
        )
    
    return None


def create_callback_handler(
    callback: Callable,
    pattern: Optional[str] = None,
    **kwargs
):
    """Create a callback query handler using robot-ptb-compat if available.
    
    Args:
        callback: Callback function
        pattern: Regex pattern for callback data
        **kwargs: Additional arguments
        
    Returns:
        CallbackAdapter or legacy handler
    """
    if HAS_ROBOT_PTB_COMPAT and CallbackAdapter:
        return CallbackAdapter(callback=callback, pattern=pattern, **kwargs)
    
    return None


__all__ = [
    "HAS_ROBOT_PTB_COMPAT",
    "create_command_handler",
    "create_message_handler", 
    "create_callback_handler",
]

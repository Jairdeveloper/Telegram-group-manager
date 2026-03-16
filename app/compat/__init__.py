"""Compat module for robot-ptb-compat integration."""

from app.compat.handlers import (
    HAS_ROBOT_PTB_COMPAT,
    create_command_handler,
    create_message_handler,
    create_callback_handler,
)

__all__ = [
    "HAS_ROBOT_PTB_COMPAT",
    "create_command_handler",
    "create_message_handler",
    "create_callback_handler",
]

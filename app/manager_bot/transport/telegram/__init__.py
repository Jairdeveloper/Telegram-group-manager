"""Compatibility telegram transport package (aliases to _transport.telegram)."""

from app.manager_bot._transport.telegram.callback_router import CallbackRouter
from app.manager_bot._transport.telegram.keyboard_builder import KeyboardBuilder
from app.manager_bot._transport.telegram.menu_engine import MenuEngine, get_menu_engine, set_menu_engine
from app.manager_bot._transport.telegram.router import TelegramRouter

__all__ = [
    "CallbackRouter",
    "KeyboardBuilder",
    "MenuEngine",
    "get_menu_engine",
    "set_menu_engine",
    "TelegramRouter",
]


"""Unit tests for keyboard builder."""

import pytest
from telegram import InlineKeyboardButton
from app.manager_bot.transport.telegram.keyboard_builder import KeyboardBuilder


class TestKeyboardBuilder:
    """Tests for KeyboardBuilder class."""

    def test_create_empty_builder(self):
        builder = KeyboardBuilder.create()
        keyboard = builder.build()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 0

    def test_add_single_button(self):
        builder = KeyboardBuilder.create()
        builder.add_button("Test", "test:action")
        
        keyboard = builder.build()
        
        assert len(keyboard.inline_keyboard) == 1
        assert keyboard.inline_keyboard[0][0].text == "Test"
        assert keyboard.inline_keyboard[0][0].callback_data == "test:action"

    def test_add_button_with_emoji(self):
        builder = KeyboardBuilder.create()
        builder.add_button("Test", "test:action", "🔧")
        
        keyboard = builder.build()
        
        assert keyboard.inline_keyboard[0][0].text == "🔧 Test"

    def test_add_toggle_on(self):
        builder = KeyboardBuilder.create()
        builder.add_toggle("Feature", True, "feature:toggle")
        
        keyboard = builder.build()
        
        assert "✅ Feature: off" in keyboard.inline_keyboard[0][0].text

    def test_add_toggle_off(self):
        builder = KeyboardBuilder.create()
        builder.add_toggle("Feature", False, "feature:toggle")
        
        keyboard = builder.build()
        
        assert "❌ Feature: on" in keyboard.inline_keyboard[0][0].text

    def test_add_row(self):
        builder = KeyboardBuilder.create()
        builder.add_row(
            InlineKeyboardButton("A", callback_data="a"),
            InlineKeyboardButton("B", callback_data="b"),
        )
        
        keyboard = builder.build()
        
        assert len(keyboard.inline_keyboard[0]) == 2

    def test_add_back_button(self):
        builder = KeyboardBuilder.create()
        builder.add_back("main")
        
        keyboard = builder.build()
        
        assert keyboard.inline_keyboard[0][0].text == "🔙 Volver"
        assert keyboard.inline_keyboard[0][0].callback_data == "nav:back:main"

    def test_add_custom_back_button(self):
        builder = KeyboardBuilder.create()
        builder.add_back("settings", "🔙 Settings")
        
        keyboard = builder.build()
        
        assert keyboard.inline_keyboard[0][0].text == "🔙 Settings"

    def test_add_home_button(self):
        builder = KeyboardBuilder.create()
        builder.add_home()
        
        keyboard = builder.build()
        
        assert keyboard.inline_keyboard[0][0].text == "🏠 Menú Principal"
        assert keyboard.inline_keyboard[0][0].callback_data == "nav:home"

    def test_add_info_row(self):
        builder = KeyboardBuilder.create()
        builder.add_info_row("Usuarios", "42", "👥")
        
        keyboard = builder.build()
        
        assert "👥 Usuarios: 42" in keyboard.inline_keyboard[0][0].text

    def test_fluent_interface(self):
        builder = (
            KeyboardBuilder.create()
            .add_button("A", "a")
            .add_button("B", "b")
            .add_back("main")
        )
        
        keyboard = builder.build()
        
        assert len(keyboard.inline_keyboard) == 3

    def test_clear(self):
        builder = KeyboardBuilder.create()
        builder.add_button("Test", "test")
        builder.clear()
        
        keyboard = builder.build()
        
        assert len(keyboard.inline_keyboard) == 0

"""Unit tests for menu base classes."""

import pytest
from app.manager_bot.menus.base import MenuAction, MenuRow, MenuDefinition


class TestMenuAction:
    """Tests for MenuAction dataclass."""

    def test_create_action_without_emoji(self):
        action = MenuAction(callback_data="test:action", label="Test Action")
        assert action.callback_data == "test:action"
        assert action.label == "Test Action"
        assert action.emoji is None

    def test_create_action_with_emoji(self):
        action = MenuAction(
            callback_data="test:action",
            label="Test Action",
            emoji="🔧"
        )
        assert action.callback_data == "test:action"
        assert action.label == "🔧 Test Action"
        assert action.emoji == "🔧"

    def test_action_label_concatenation(self):
        action = MenuAction(callback_data="mod:toggle", label="Moderation", emoji="🛡️")
        assert action.label == "🛡️ Moderation"


class TestMenuRow:
    """Tests for MenuRow class."""

    def test_create_empty_row(self):
        row = MenuRow()
        assert row.actions == []

    def test_add_action_returns_self(self):
        row = MenuRow()
        result = row.add_action("test:action", "Test")
        assert result is row

    def test_add_multiple_actions(self):
        row = MenuRow()
        row.add_action("action1", "Action 1")
        row.add_action("action2", "Action 2")
        
        assert len(row.actions) == 2
        assert row.actions[0].callback_data == "action1"
        assert row.actions[1].callback_data == "action2"


class TestMenuDefinition:
    """Tests for MenuDefinition class."""

    def test_create_menu_definition(self):
        menu = MenuDefinition(menu_id="main", title="Main Menu")
        
        assert menu.menu_id == "main"
        assert menu.title == "Main Menu"
        assert menu.rows == []
        assert menu.back_button is None
        assert menu.parent_menu is None

    def test_add_row_returns_row(self):
        menu = MenuDefinition(menu_id="test", title="Test")
        result = menu.add_row()
        
        assert isinstance(result, MenuRow)
        assert len(menu.rows) == 1

    def test_menu_with_rows_and_actions(self):
        menu = MenuDefinition(menu_id="test", title="Test Menu")
        
        menu.add_row().add_action("action1", "Label 1")
        menu.add_row().add_action("action2", "Label 2", "🔧")
        
        assert len(menu.rows) == 2
        assert len(menu.rows[0].actions) == 1
        assert len(menu.rows[1].actions) == 1
        assert menu.rows[0].actions[0].callback_data == "action1"
        assert menu.rows[1].actions[0].label == "🔧 Label 2"

    def test_to_keyboard_returns_markup(self):
        menu = MenuDefinition(menu_id="test", title="Test")
        menu.add_row().add_action("action1", "Label 1")
        
        keyboard = menu.to_keyboard()
        
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
        assert len(keyboard.inline_keyboard) == 1

    def test_to_keyboard_with_context(self):
        menu = MenuDefinition(menu_id="test", title="Test")
        menu.add_row().add_action("action1", "Label 1")
        
        context = {"config": {"setting": "value"}}
        keyboard = menu.to_keyboard(context=context)
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1

    def test_with_back_button(self):
        menu = MenuDefinition(menu_id="sub", title="Sub Menu", parent_menu="main")
        menu.add_row().add_action("action1", "Action")
        
        menu.with_back_button()
        
        assert len(menu.rows) == 2
        assert menu.rows[1].actions[0].callback_data == "nav:back:main"

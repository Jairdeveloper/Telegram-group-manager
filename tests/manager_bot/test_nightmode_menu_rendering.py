"""Tests for nightmode menu rendering."""

import pytest

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.nightmode_menu import (
    create_nightmode_menu,
    create_mode_selection_menu,
    create_schedule_menu,
)


class TestNightModeMenuRendering:
    """Tests for nightmode menu rendering."""

    def test_menu_title_reflects_enabled_state(self):
        """Test that menu title reflects enabled state."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = True
        config.nightmode_silence = False

        menu = create_nightmode_menu(config)
        
        assert "Estado: 📸 Eliminación multimedia" in menu.title
        assert "🌙 Modo Nocturno" in menu.title

    def test_menu_title_reflects_silence_mode(self):
        """Test that menu title reflects silence mode."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = False
        config.nightmode_silence = True

        menu = create_nightmode_menu(config)
        
        assert "Estado: 🔇 Silencio global" in menu.title

    def test_menu_title_reflects_both_modes(self):
        """Test that menu title reflects both modes active."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = True
        config.nightmode_silence = True

        menu = create_nightmode_menu(config)
        
        assert "📸" in menu.title
        assert "🔇" in menu.title

    def test_menu_title_reflects_schedule(self):
        """Test that menu title reflects schedule."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_start = "22:00"
        config.nightmode_end = "08:00"

        menu = create_nightmode_menu(config)
        
        assert "22:00 - 08:00" in menu.title

    def test_menu_title_reflects_announcements_disabled(self):
        """Test that menu title reflects announcements disabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_announcements = False

        menu = create_nightmode_menu(config)
        
        assert "❌" in menu.title
        assert "Anuncios" in menu.title

    def test_menu_title_disabled_state(self):
        """Test that menu title reflects disabled state."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = False

        menu = create_nightmode_menu(config)
        
        assert "Activar" in menu.rows[0].actions[0].label

    def test_schedule_menu_reflects_times(self):
        """Test that schedule menu reflects configured times."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_start = "21:00"
        config.nightmode_end = "06:00"

        menu = create_schedule_menu(config)
        
        assert "21:00" in menu.title
        assert "06:00" in menu.title

    def test_mode_selection_reflects_delete_media_enabled(self):
        """Test that mode selection reflects delete_media enabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_delete_media = True
        config.nightmode_silence = False

        menu = create_mode_selection_menu(config)
        
        assert "✅" in menu.rows[0].actions[0].label

    def test_mode_selection_reflects_silence_enabled(self):
        """Test that mode selection reflects silence enabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_delete_media = False
        config.nightmode_silence = True

        menu = create_mode_selection_menu(config)
        
        assert "✅" in menu.rows[1].actions[0].label

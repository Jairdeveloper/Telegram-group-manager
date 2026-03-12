"""Unit tests for group config."""

import pytest
from datetime import datetime
from app.manager_bot.config.group_config import GroupConfig


class TestGroupConfig:
    """Tests for GroupConfig dataclass."""

    def test_create_default_config(self):
        config = GroupConfig(chat_id=123, tenant_id="test")
        
        assert config.chat_id == 123
        assert config.tenant_id == "test"
        assert config.antiflood_enabled is False
        assert config.antispam_enabled is False
        assert config.blocked_words == []
        assert config.filters == []

    def test_create_default_factory(self):
        config = GroupConfig.create_default(123, "test")
        
        assert config.chat_id == 123
        assert config.tenant_id == "test"

    def test_to_dict(self):
        config = GroupConfig(chat_id=123, tenant_id="test")
        config.antiflood_enabled = True
        
        data = config.to_dict()
        
        assert data["chat_id"] == 123
        assert data["antiflood_enabled"] is True
        assert "updated_at" in data

    def test_from_dict(self):
        data = {
            "chat_id": 123,
            "tenant_id": "test",
            "antiflood_enabled": True,
            "antiflood_limit": 10,
            "antichannel_enabled": False,
            "antilink_enabled": False,
            "antispam_enabled": False,
            "spamwatch_enabled": False,
            "sibyl_enabled": False,
            "captcha_enabled": False,
            "captcha_timeout": 300,
            "captcha_type": "button",
            "welcome_enabled": False,
            "welcome_text": "",
            "welcome_media": None,
            "goodbye_enabled": False,
            "goodbye_text": "",
            "blocked_words": [],
            "filters": [],
            "nightmode_enabled": False,
            "nightmode_start": "23:00",
            "nightmode_end": "07:00",
            "max_warnings": 3,
            "auto_ban_on_max": True,
            "updated_at": "2026-03-12T12:00:00",
            "updated_by": None,
        }
        
        config = GroupConfig.from_dict(data)
        
        assert config.chat_id == 123
        assert config.antiflood_enabled is True
        assert config.antiflood_limit == 10
        assert isinstance(config.updated_at, datetime)

    def test_from_dict_with_none_values(self):
        data = {
            "chat_id": 123,
            "tenant_id": "test",
            "antiflood_enabled": False,
            "antiflood_limit": 5,
            "antichannel_enabled": False,
            "antilink_enabled": False,
            "antispam_enabled": False,
            "spamwatch_enabled": False,
            "sibyl_enabled": False,
            "captcha_enabled": False,
            "captcha_timeout": 300,
            "captcha_type": "button",
            "welcome_enabled": False,
            "welcome_text": "",
            "welcome_media": None,
            "goodbye_enabled": False,
            "goodbye_text": "",
            "blocked_words": None,
            "filters": None,
            "nightmode_enabled": False,
            "nightmode_start": "23:00",
            "nightmode_end": "07:00",
            "max_warnings": 3,
            "auto_ban_on_max": True,
            "updated_at": "2026-03-12T12:00:00",
            "updated_by": None,
        }
        
        config = GroupConfig.from_dict(data)
        
        assert config.blocked_words == []
        assert config.filters == []

    def test_update_timestamp(self):
        config = GroupConfig(chat_id=123, tenant_id="test")
        
        config.update_timestamp(456)
        
        assert isinstance(config.updated_at, datetime)
        assert config.updated_by == 456

    def test_get_filter_count(self):
        config = GroupConfig(chat_id=123, tenant_id="test")
        config.filters = [
            {"pattern": "bad", "response": "removed"},
            {"pattern": "ugly", "response": "removed"},
        ]
        
        assert config.get_filter_count() == 2

    def test_is_filter_active(self):
        config = GroupConfig(chat_id=123, tenant_id="test")
        config.filters = [
            {"pattern": "bad", "response": "removed"},
        ]
        
        assert config.is_filter_active("bad") is True
        assert config.is_filter_active("good") is False

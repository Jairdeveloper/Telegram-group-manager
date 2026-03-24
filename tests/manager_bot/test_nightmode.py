"""Tests for night mode feature."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import time

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import InMemoryConfigStorage
from app.manager_bot._features.nightmode import NightModeFeature


class TestNightModeFeature:
    """Tests for NightModeFeature."""

    @pytest.fixture
    def storage(self):
        """Create in-memory config storage."""
        return InMemoryConfigStorage()

    @pytest.fixture
    def feature(self, storage):
        """Create night mode feature."""
        return NightModeFeature(storage)

    def test_default_values(self):
        """Test default configuration values."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")

        assert config.nightmode_enabled is False
        assert config.nightmode_start == "23:00"
        assert config.nightmode_end == "07:00"
        assert config.nightmode_mode == "multimedia"
        assert config.nightmode_delete_media is True
        assert config.nightmode_silence is False
        assert config.nightmode_announcements is True

    def test_nightmode_config_to_dict(self):
        """Test nightmode fields in to_dict."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_mode = "silencio"
        config.nightmode_delete_media = False
        config.nightmode_silence = True
        config.nightmode_announcements = False

        data = config.to_dict()

        assert "nightmode_enabled" in data
        assert "nightmode_mode" in data
        assert "nightmode_delete_media" in data
        assert "nightmode_silence" in data
        assert "nightmode_announcements" in data

    def test_nightmode_config_from_dict(self):
        """Test nightmode fields in from_dict."""
        data = {
            "chat_id": 12345,
            "tenant_id": "test",
            "nightmode_enabled": True,
            "nightmode_start": "22:00",
            "nightmode_end": "08:00",
            "nightmode_mode": "silencio",
            "nightmode_delete_media": False,
            "nightmode_silence": True,
            "nightmode_announcements": False,
        }

        config = GroupConfig.from_dict(data)

        assert config.nightmode_enabled is True
        assert config.nightmode_start == "22:00"
        assert config.nightmode_end == "08:00"
        assert config.nightmode_mode == "silencio"
        assert config.nightmode_delete_media is False
        assert config.nightmode_silence is True
        assert config.nightmode_announcements is False


class TestNightModeIsActive:
    """Tests for is_active method."""

    @pytest.fixture
    def storage(self):
        return InMemoryConfigStorage()

    @pytest.fixture
    def feature(self, storage):
        return NightModeFeature(storage)

    def test_not_active_when_disabled(self, feature):
        """Test is_active returns False when disabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = False

        assert feature.is_active(config) is False

    def test_not_active_without_any_mode(self, feature):
        """Test is_active returns False when no mode is enabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = False
        config.nightmode_silence = False

        assert feature.is_active(config) is False

    def test_should_delete_media(self, feature):
        """Test should_delete_media method."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = True

        assert feature.should_delete_media(config) is True

        config.nightmode_delete_media = False
        assert feature.should_delete_media(config) is False

    def test_should_silence(self, feature):
        """Test should_silence method."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_silence = True

        assert feature.should_silence(config) is True

        config.nightmode_silence = False
        assert feature.should_silence(config) is False

    def test_should_announce_default(self, feature):
        """Test should_announce returns True by default."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")

        assert feature.should_announce(config) is True

    def test_should_announce_disabled(self, feature):
        """Test should_announce returns False when disabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_announcements = False

        assert feature.should_announce(config) is False


class TestNightModeProcessMessage:
    """Tests for process_message method."""

    @pytest.fixture
    def storage(self):
        return InMemoryConfigStorage()

    @pytest.fixture
    def feature(self, storage):
        return NightModeFeature(storage)

    def test_process_message_not_active(self, feature):
        """Test process_message returns False when not active."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = False

        message = MagicMock()
        message.content_type = "photo"

        assert feature.process_message(message, config) is False

    def test_process_message_delete_media(self, feature):
        """Test process_message deletes media when enabled."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = True

        for media_type in ["photo", "video", "audio", "voice", "video_note", "document"]:
            message = MagicMock()
            message.content_type = media_type
            assert feature.process_message(message, config) is True

    def test_process_message_no_media(self, feature):
        """Test process_message returns False for non-media."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.nightmode_enabled = True
        config.nightmode_delete_media = True

        message = MagicMock()
        message.content_type = "text"

        assert feature.process_message(message, config) is False
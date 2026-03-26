"""Tests for report destination configuration."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import InMemoryConfigStorage
from app.manager_bot._features.reports.config_service import (
    DestinationType,
    ReportsConfigService,
)


class TestDestinationType:
    """Tests for DestinationType enum."""

    def test_destination_values(self):
        """Test that all destination types have correct values."""
        assert DestinationType.NINGUNO.value == "ninguno"
        assert DestinationType.FUNDADOR.value == "fundador"
        assert DestinationType.GRUPO_STAFF.value == "grupo_staff"

    def test_valid_destinations(self):
        """Test valid destinations set."""
        service = ReportsConfigService(MagicMock())
        assert "ninguno" in service.VALID_DESTINATIONS
        assert "fundador" in service.VALID_DESTINATIONS
        assert "grupo_staff" in service.VALID_DESTINATIONS
        assert len(service.VALID_DESTINATIONS) == 3


class TestReportsConfigService:
    """Tests for ReportsConfigService."""

    @pytest.fixture
    def storage(self):
        """Create in-memory config storage."""
        return InMemoryConfigStorage()

    @pytest.fixture
    def service(self, storage):
        """Create config service."""
        return ReportsConfigService(storage)

    def test_get_destination_default(self, service, storage):
        """Test get_destination returns default when no config exists."""
        async def run():
            return await service.get_destination(12345)
        result = asyncio.run(run())
        assert result == DestinationType.NINGUNO

    def test_get_destination_from_config(self, service, storage):
        """Test get_destination returns configured value."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "fundador"
            await storage.set(config)
            return await service.get_destination(12345)
        
        result = asyncio.run(run())
        assert result == DestinationType.FUNDADOR

    def test_set_destination(self, service, storage):
        """Test set_destination saves configuration."""
        async def run():
            await service.set_destination(12345, DestinationType.GRUPO_STAFF)
            config = await storage.get(12345)
            return config.report_destination
        
        result = asyncio.run(run())
        assert result == "grupo_staff"

    def test_set_destination_creates_config_if_missing(self, service, storage):
        """Test set_destination creates config if not exists."""
        async def run():
            await service.set_destination(99999, DestinationType.FUNDADOR)
            config = await storage.get(99999)
            return config.report_destination if config else None
        
        result = asyncio.run(run())
        assert result == "fundador"

    def test_is_enabled_default(self, service, storage):
        """Test is_enabled returns True by default."""
        async def run():
            return await service.is_enabled(12345)
        
        result = asyncio.run(run())
        assert result is True

    def test_is_enabled_from_config(self, service, storage):
        """Test is_enabled returns configured value."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination_enabled = False
            await storage.set(config)
            return await service.is_enabled(12345)
        
        result = asyncio.run(run())
        assert result is False

    def test_set_enabled(self, service, storage):
        """Test set_enabled updates configuration."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            await storage.set(config)
            
            await service.set_enabled(12345, False)
            config = await storage.get(12345)
            return config.report_destination_enabled
        
        result = asyncio.run(run())
        assert result is False

    def test_get_destination_recipients_disabled(self, service, storage):
        """Test get_destination_recipients returns empty when disabled."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "fundador"
            config.report_destination_enabled = False
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=100)
        
        result = asyncio.run(run())
        assert result == []

    def test_get_destination_recipients_ninguno(self, service, storage):
        """Test get_destination_recipients returns empty for ninguno."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "ninguno"
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=100, staff_ids=[200, 300])
        
        result = asyncio.run(run())
        assert result == []

    def test_get_destination_recipients_fundador(self, service, storage):
        """Test get_destination_recipients returns founder."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "fundador"
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=100, staff_ids=[200, 300])
        
        result = asyncio.run(run())
        assert result == [100]

    def test_get_destination_recipients_fundador_no_id(self, service, storage):
        """Test get_destination_recipients returns empty when no founder_id."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "fundador"
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=None, staff_ids=[200, 300])
        
        result = asyncio.run(run())
        assert result == []

    def test_get_destination_recipients_grupo_staff(self, service, storage):
        """Test get_destination_recipients returns staff_ids."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "grupo_staff"
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=100, staff_ids=[200, 300])
        
        result = asyncio.run(run())
        assert result == [200, 300]

    def test_get_destination_recipients_grupo_staff_empty(self, service, storage):
        """Test get_destination_recipients returns empty when no staff_ids."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "grupo_staff"
            await storage.set(config)
            return await service.get_destination_recipients(12345, founder_id=100, staff_ids=None)
        
        result = asyncio.run(run())
        assert result == []

    def test_validate_destination_valid(self, service):
        """Test validate_destination returns True for valid values."""
        assert service.validate_destination("ninguno") is True
        assert service.validate_destination("fundador") is True
        assert service.validate_destination("grupo_staff") is True

    def test_validate_destination_invalid(self, service):
        """Test validate_destination returns False for invalid values."""
        assert service.validate_destination("invalid") is False
        assert service.validate_destination("") is False
        assert service.validate_destination("ADMIN") is False

    def test_invalid_destination_falls_back_to_ninguno(self, service, storage):
        """Test invalid destination values fall back to ninguno."""
        async def run():
            config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
            config.report_destination = "invalid_value"
            await storage.set(config)
            return await service.get_destination(12345)
        
        result = asyncio.run(run())
        assert result == DestinationType.NINGUNO


class TestGroupConfigDestination:
    """Tests for GroupConfig destination fields."""

    def test_default_destination_values(self):
        """Test default values for destination fields."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")

        assert config.report_destination == "ninguno"
        assert config.report_destination_enabled is True

    def test_destination_in_to_dict(self):
        """Test destination fields are included in to_dict."""
        config = GroupConfig.create_default(chat_id=12345, tenant_id="test")
        config.report_destination = "fundador"
        config.report_destination_enabled = False

        data = config.to_dict()

        assert "report_destination" in data
        assert data["report_destination"] == "fundador"
        assert "report_destination_enabled" in data
        assert data["report_destination_enabled"] is False

    def test_destination_in_from_dict(self):
        """Test destination fields are restored from from_dict."""
        data = {
            "chat_id": 12345,
            "tenant_id": "test",
            "report_destination": "grupo_staff",
            "report_destination_enabled": True,
        }

        config = GroupConfig.from_dict(data)

        assert config.report_destination == "grupo_staff"
        assert config.report_destination_enabled is True

"""Tests for tenant repository and data isolation."""
import pytest
from app.database.repositories.tenant_repository import (
    TenantRepository, InMemoryTenantRepository, PostgresTenantRepository
)
from app.database.models import Tenant


class TestTenantModels:
    def test_tenant_creation(self):
        tenant = Tenant(
            tenant_id="tenant_1",
            name="Test Company",
            is_active=1,
            settings={"key": "value"}
        )
        
        assert tenant.tenant_id == "tenant_1"
        assert tenant.name == "Test Company"
        assert tenant.is_active == 1


class TestInMemoryTenantRepository:
    @pytest.fixture
    def tenant_repo(self):
        return InMemoryTenantRepository()

    def test_create_tenant(self, tenant_repo):
        tenant = Tenant(tenant_id="tenant_1", name="Company A", is_active=1)
        result = tenant_repo.create(tenant)
        
        assert result.tenant_id == "tenant_1"

    def test_get_tenant(self, tenant_repo):
        tenant = Tenant(tenant_id="tenant_1", name="Company A", is_active=1)
        tenant_repo.create(tenant)
        
        result = tenant_repo.get("tenant_1")
        
        assert result is not None
        assert result.name == "Company A"

    def test_get_nonexistent_tenant(self, tenant_repo):
        result = tenant_repo.get("nonexistent")
        
        assert result is None

    def test_update_tenant(self, tenant_repo):
        tenant = Tenant(tenant_id="tenant_1", name="Company A", is_active=1)
        tenant_repo.create(tenant)
        
        tenant.name = "Company B"
        result = tenant_repo.update(tenant)
        
        assert result.name == "Company B"

    def test_delete_tenant(self, tenant_repo):
        tenant = Tenant(tenant_id="tenant_1", name="Company A", is_active=1)
        tenant_repo.create(tenant)
        
        result = tenant_repo.delete("tenant_1")
        
        assert result is True
        assert tenant_repo.get("tenant_1") is None

    def test_list_all_tenants(self, tenant_repo):
        tenant_repo.create(Tenant(tenant_id="tenant_1", name="Company A", is_active=1))
        tenant_repo.create(Tenant(tenant_id="tenant_2", name="Company B", is_active=1))
        
        tenants = tenant_repo.list_all()
        
        assert len(tenants) == 2

    def test_get_active_tenants(self, tenant_repo):
        tenant_repo.create(Tenant(tenant_id="tenant_1", name="Company A", is_active=1))
        tenant_repo.create(Tenant(tenant_id="tenant_2", name="Company B", is_active=0))
        
        active = tenant_repo.get_active_tenants()
        
        assert len(active) == 1

    def test_suspend_tenant(self, tenant_repo):
        tenant_repo.create(Tenant(tenant_id="tenant_1", name="Company A", is_active=1))
        
        result = tenant_repo.suspend("tenant_1", "Non-payment")
        
        assert result is True
        tenant = tenant_repo.get("tenant_1")
        assert tenant.is_active == 0

    def test_activate_tenant(self, tenant_repo):
        tenant = Tenant(tenant_id="tenant_1", name="Company A", is_active=0)
        tenant.settings = {"suspension_reason": "Non-payment"}
        tenant_repo.create(tenant)
        
        result = tenant_repo.activate("tenant_1")
        
        assert result is True
        tenant = tenant_repo.get("tenant_1")
        assert tenant.is_active == 1


class TestTenantIsolation:
    @pytest.fixture
    def tenant_repo(self):
        return InMemoryTenantRepository()

    def test_tenant_data_isolation(self, tenant_repo):
        tenant1 = Tenant(tenant_id="tenant_1", name="Company A", is_active=1)
        tenant2 = Tenant(tenant_id="tenant_2", name="Company B", is_active=1)
        
        tenant_repo.create(tenant1)
        tenant_repo.create(tenant2)
        
        result1 = tenant_repo.get("tenant_1")
        result2 = tenant_repo.get("tenant_2")
        
        assert result1.name == "Company A"
        assert result2.name == "Company B"
        assert result1.tenant_id != result2.tenant_id

    def test_delete_isolation(self, tenant_repo):
        tenant_repo.create(Tenant(tenant_id="tenant_1", name="Company A", is_active=1))
        tenant_repo.create(Tenant(tenant_id="tenant_2", name="Company B", is_active=1))
        
        tenant_repo.delete("tenant_1")
        
        assert tenant_repo.get("tenant_1") is None
        assert tenant_repo.get("tenant_2") is not None


class TestUserRepositoryTenantIsolation:
    @pytest.fixture
    def user_repo(self):
        from app.database.repositories import InMemoryUserRepository
        return InMemoryUserRepository()

    def test_user_isolation_by_tenant(self, user_repo):
        from app.database.repositories import User
        
        user1 = User(
            user_id="user_1",
            tenant_id="tenant_1",
            email="user1@companyA.com",
            username="user1",
            hashed_password="hash1",
            role="user"
        )
        user2 = User(
            user_id="user_2",
            tenant_id="tenant_2",
            email="user2@companyB.com",
            username="user2",
            hashed_password="hash2",
            role="user"
        )
        
        user_repo.save(user1)
        user_repo.save(user2)
        
        found_user1 = user_repo.get_by_username("user1", "tenant_1")
        found_user2 = user_repo.get_by_username("user2", "tenant_2")
        
        assert found_user1 is not None
        assert found_user2 is not None
        assert found_user1.tenant_id == "tenant_1"
        assert found_user2.tenant_id == "tenant_2"

    def test_cross_tenant_lookup_fails(self, user_repo):
        from app.database.repositories import User
        
        user_repo.save(User(
            user_id="user_1",
            tenant_id="tenant_1",
            email="user@company.com",
            username="sameusername",
            hashed_password="hash",
            role="user"
        ))
        
        result = user_repo.get_by_username("sameusername", "tenant_2")
        
        assert result is None

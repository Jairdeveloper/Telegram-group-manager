"""Tenant repository for multi-tenant isolation."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database.models import Tenant


class TenantRepository(ABC):
    """Abstract base class for tenant management."""

    @abstractmethod
    def get(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass

    @abstractmethod
    def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        pass

    @abstractmethod
    def update(self, tenant: Tenant) -> Tenant:
        """Update an existing tenant."""
        pass

    @abstractmethod
    def delete(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        pass

    @abstractmethod
    def list_all(self) -> List[Tenant]:
        """List all tenants (admin only)."""
        pass

    @abstractmethod
    def get_active_tenants(self) -> List[Tenant]:
        """List all active tenants."""
        pass

    @abstractmethod
    def suspend(self, tenant_id: str, reason: str = None) -> bool:
        """Suspend a tenant."""
        pass

    @abstractmethod
    def activate(self, tenant_id: str) -> bool:
        """Activate a suspended tenant."""
        pass


class PostgresTenantRepository(TenantRepository):
    """PostgreSQL implementation of TenantRepository."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str) -> Optional[Tenant]:
        session = self._get_session()
        try:
            return session.query(Tenant).filter(
                Tenant.tenant_id == tenant_id
            ).first()
        finally:
            session.close()

    def create(self, tenant: Tenant) -> Tenant:
        session = self._get_session()
        try:
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
            return tenant
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update(self, tenant: Tenant) -> Tenant:
        session = self._get_session()
        try:
            existing = session.query(Tenant).filter(
                Tenant.tenant_id == tenant.tenant_id
            ).first()
            if existing:
                existing.name = tenant.name
                existing.settings = tenant.settings
                existing.is_active = tenant.is_active
                session.commit()
                session.refresh(existing)
                return existing
            return None
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str) -> bool:
        session = self._get_session()
        try:
            result = session.query(Tenant).filter(
                Tenant.tenant_id == tenant_id
            ).delete()
            session.commit()
            return result > 0
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_all(self) -> List[Tenant]:
        session = self._get_session()
        try:
            return session.query(Tenant).all()
        finally:
            session.close()

    def get_active_tenants(self) -> List[Tenant]:
        session = self._get_session()
        try:
            return session.query(Tenant).filter(
                Tenant.is_active == 1
            ).all()
        finally:
            session.close()

    def suspend(self, tenant_id: str, reason: str = None) -> bool:
        session = self._get_session()
        try:
            tenant = session.query(Tenant).filter(
                Tenant.tenant_id == tenant_id
            ).first()
            if tenant:
                tenant.is_active = 0
                if tenant.settings is None:
                    tenant.settings = {}
                tenant.settings["suspension_reason"] = reason
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def activate(self, tenant_id: str) -> bool:
        session = self._get_session()
        try:
            tenant = session.query(Tenant).filter(
                Tenant.tenant_id == tenant_id
            ).first()
            if tenant:
                tenant.is_active = 1
                if "suspension_reason" in (tenant.settings or {}):
                    del tenant.settings["suspension_reason"]
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class InMemoryTenantRepository(TenantRepository):
    """In-memory implementation of TenantRepository."""

    def __init__(self):
        self._tenants: dict = {}

    def get(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    def create(self, tenant: Tenant) -> Tenant:
        self._tenants[tenant.tenant_id] = tenant
        return tenant

    def update(self, tenant: Tenant) -> Tenant:
        if tenant.tenant_id in self._tenants:
            self._tenants[tenant.tenant_id] = tenant
            return tenant
        return None

    def delete(self, tenant_id: str) -> bool:
        if tenant_id in self._tenants:
            del self._tenants[tenant_id]
            return True
        return False

    def list_all(self) -> List[Tenant]:
        return list(self._tenants.values())

    def get_active_tenants(self) -> List[Tenant]:
        return [t for t in self._tenants.values() if t.is_active == 1]

    def suspend(self, tenant_id: str, reason: str = None) -> bool:
        tenant = self._tenants.get(tenant_id)
        if tenant:
            tenant.is_active = 0
            if tenant.settings is None:
                tenant.settings = {}
            tenant.settings["suspension_reason"] = reason
            return True
        return False

    def activate(self, tenant_id: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if tenant:
            tenant.is_active = 1
            if tenant.settings and "suspension_reason" in tenant.settings:
                del tenant.settings["suspension_reason"]
            return True
        return False


_tenant_repo_instance: Optional[TenantRepository] = None


def get_tenant_repository() -> TenantRepository:
    global _tenant_repo_instance
    if _tenant_repo_instance is None:
        _tenant_repo_instance = InMemoryTenantRepository()
    return _tenant_repo_instance


def set_tenant_repository(repo: TenantRepository) -> None:
    global _tenant_repo_instance
    _tenant_repo_instance = repo

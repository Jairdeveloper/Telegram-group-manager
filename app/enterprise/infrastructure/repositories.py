"""Repositories for EnterpriseRobot users and bans."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, Optional, Protocol, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import load_api_settings
from app.database.models import EnterpriseBan as EnterpriseBanModel
from app.database.models import EnterpriseUser as EnterpriseUserModel

from app.enterprise.domain.entities import EnterpriseUser, BanRecord
from app.enterprise.domain.roles import EnterpriseRole, parse_role


class EnterpriseUserRepository(Protocol):
    def get(self, tenant_id: str, user_id: int) -> Optional[EnterpriseUser]:
        ...

    def upsert(self, user: EnterpriseUser) -> EnterpriseUser:
        ...

    def delete(self, tenant_id: str, user_id: int) -> None:
        ...

    def list(self, tenant_id: str) -> Iterable[EnterpriseUser]:
        ...

    def count(self, tenant_id: str) -> int:
        ...


class BanRepository(Protocol):
    def get(self, tenant_id: str, user_id: int) -> Optional[BanRecord]:
        ...

    def ban(self, record: BanRecord) -> BanRecord:
        ...

    def unban(self, tenant_id: str, user_id: int) -> None:
        ...

    def list(self, tenant_id: str) -> Iterable[BanRecord]:
        ...


class InMemoryEnterpriseUserRepository:
    def __init__(self):
        self._users: Dict[Tuple[str, int], EnterpriseUser] = {}

    def get(self, tenant_id: str, user_id: int) -> Optional[EnterpriseUser]:
        return self._users.get((tenant_id, user_id))

    def upsert(self, user: EnterpriseUser) -> EnterpriseUser:
        self._users[(user.tenant_id, user.user_id)] = user
        return user

    def delete(self, tenant_id: str, user_id: int) -> None:
        self._users.pop((tenant_id, user_id), None)

    def list(self, tenant_id: str) -> Iterable[EnterpriseUser]:
        return [u for (t_id, _), u in self._users.items() if t_id == tenant_id]

    def count(self, tenant_id: str) -> int:
        return len([1 for (t_id, _), _u in self._users.items() if t_id == tenant_id])


class InMemoryBanRepository:
    def __init__(self):
        self._bans: Dict[Tuple[str, int], BanRecord] = {}

    def get(self, tenant_id: str, user_id: int) -> Optional[BanRecord]:
        return self._bans.get((tenant_id, user_id))

    def ban(self, record: BanRecord) -> BanRecord:
        self._bans[(record.tenant_id, record.user_id)] = record
        return record

    def unban(self, tenant_id: str, user_id: int) -> None:
        self._bans.pop((tenant_id, user_id), None)

    def list(self, tenant_id: str) -> Iterable[BanRecord]:
        return [b for (t_id, _), b in self._bans.items() if t_id == tenant_id]


_user_repo: Optional[InMemoryEnterpriseUserRepository] = None
_ban_repo: Optional[InMemoryBanRepository] = None
_pg_user_repo: Optional["PostgresEnterpriseUserRepository"] = None
_pg_ban_repo: Optional["PostgresBanRepository"] = None


class PostgresEnterpriseUserRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, user_id: int) -> Optional[EnterpriseUser]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseUserModel).filter(
                EnterpriseUserModel.tenant_id == tenant_id,
                EnterpriseUserModel.user_id == user_id,
            ).first()
            if not row:
                return None
            role = _safe_role(row.role)
            return EnterpriseUser(
                user_id=row.user_id,
                tenant_id=row.tenant_id,
                role=role,
                status=row.status,
                created_at=row.created_at,
            )
        finally:
            session.close()

    def upsert(self, user: EnterpriseUser) -> EnterpriseUser:
        session = self._get_session()
        try:
            row = session.query(EnterpriseUserModel).filter(
                EnterpriseUserModel.tenant_id == user.tenant_id,
                EnterpriseUserModel.user_id == user.user_id,
            ).first()
            if row is None:
                row = EnterpriseUserModel(
                    tenant_id=user.tenant_id,
                    user_id=user.user_id,
                    role=user.role.value if hasattr(user.role, "value") else str(user.role),
                    status=user.status,
                )
                session.add(row)
            else:
                row.role = user.role.value if hasattr(user.role, "value") else str(user.role)
                row.status = user.status
                row.updated_at = datetime.utcnow()
            session.commit()
            return user
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str, user_id: int) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseUserModel).filter(
                EnterpriseUserModel.tenant_id == tenant_id,
                EnterpriseUserModel.user_id == user_id,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str) -> Iterable[EnterpriseUser]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseUserModel).filter(
                EnterpriseUserModel.tenant_id == tenant_id
            ).all()
            return [ _row_to_user(row) for row in rows ]
        finally:
            session.close()

    def count(self, tenant_id: str) -> int:
        session = self._get_session()
        try:
            return session.query(EnterpriseUserModel).filter(
                EnterpriseUserModel.tenant_id == tenant_id
            ).count()
        finally:
            session.close()


class PostgresBanRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, user_id: int) -> Optional[BanRecord]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseBanModel).filter(
                EnterpriseBanModel.tenant_id == tenant_id,
                EnterpriseBanModel.user_id == user_id,
            ).first()
            if not row:
                return None
            return BanRecord(
                tenant_id=row.tenant_id,
                user_id=row.user_id,
                banned_by=row.banned_by,
                reason=row.reason,
                created_at=row.created_at,
                expires_at=row.expires_at,
            )
        finally:
            session.close()

    def ban(self, record: BanRecord) -> BanRecord:
        session = self._get_session()
        try:
            row = session.query(EnterpriseBanModel).filter(
                EnterpriseBanModel.tenant_id == record.tenant_id,
                EnterpriseBanModel.user_id == record.user_id,
            ).first()
            if row is None:
                row = EnterpriseBanModel(
                    tenant_id=record.tenant_id,
                    user_id=record.user_id,
                    banned_by=record.banned_by,
                    reason=record.reason,
                    created_at=record.created_at,
                    expires_at=record.expires_at,
                )
                session.add(row)
            else:
                row.banned_by = record.banned_by
                row.reason = record.reason
                row.expires_at = record.expires_at
            session.commit()
            return record
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def unban(self, tenant_id: str, user_id: int) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseBanModel).filter(
                EnterpriseBanModel.tenant_id == tenant_id,
                EnterpriseBanModel.user_id == user_id,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str) -> Iterable[BanRecord]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseBanModel).filter(
                EnterpriseBanModel.tenant_id == tenant_id
            ).all()
            return [
                BanRecord(
                    tenant_id=row.tenant_id,
                    user_id=row.user_id,
                    banned_by=row.banned_by,
                    reason=row.reason,
                    created_at=row.created_at,
                    expires_at=row.expires_at,
                )
                for row in rows
            ]
        finally:
            session.close()


def _postgres_enabled() -> bool:
    settings = load_api_settings()
    return settings.is_postgres_enabled() and not settings.is_storage_disabled()


def _safe_role(raw: str) -> EnterpriseRole:
    try:
        return parse_role(raw)
    except Exception:
        return EnterpriseRole.USER


def _row_to_user(row: EnterpriseUserModel) -> EnterpriseUser:
    return EnterpriseUser(
        user_id=row.user_id,
        tenant_id=row.tenant_id,
        role=_safe_role(row.role),
        status=row.status,
        created_at=row.created_at,
    )


def get_user_repo() -> EnterpriseUserRepository:
    global _user_repo, _pg_user_repo
    if _postgres_enabled():
        if _pg_user_repo is None:
            _pg_user_repo = PostgresEnterpriseUserRepository(load_api_settings().database_url)
        return _pg_user_repo
    if _user_repo is None:
        _user_repo = InMemoryEnterpriseUserRepository()
    return _user_repo


def get_ban_repo() -> BanRepository:
    global _ban_repo, _pg_ban_repo
    if _postgres_enabled():
        if _pg_ban_repo is None:
            _pg_ban_repo = PostgresBanRepository(load_api_settings().database_url)
        return _pg_ban_repo
    if _ban_repo is None:
        _ban_repo = InMemoryBanRepository()
    return _ban_repo

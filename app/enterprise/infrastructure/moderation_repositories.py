"""Repositories for EnterpriseRobot moderation (antispam, blacklist, antichannel)."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, Optional, Protocol, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import load_api_settings
from app.database.models import (
    EnterpriseAntiChannel as EnterpriseAntiChannelModel,
    EnterpriseAntiSpam as EnterpriseAntiSpamModel,
    EnterpriseBlacklist as EnterpriseBlacklistModel,
    EnterpriseStickerBlacklist as EnterpriseStickerBlacklistModel,
)
from app.enterprise.domain.entities import (
    EnterpriseAntiChannelConfig,
    EnterpriseAntiSpamConfig,
    EnterpriseBlacklistEntry,
    EnterpriseStickerBlacklistEntry,
)


class EnterpriseAntiSpamRepository(Protocol):
    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiSpamConfig]:
        ...

    def set(self, config: EnterpriseAntiSpamConfig) -> EnterpriseAntiSpamConfig:
        ...


class EnterpriseBlacklistRepository(Protocol):
    def add(self, entry: EnterpriseBlacklistEntry) -> EnterpriseBlacklistEntry:
        ...

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        ...

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseBlacklistEntry]:
        ...


class EnterpriseStickerBlacklistRepository(Protocol):
    def add(self, entry: EnterpriseStickerBlacklistEntry) -> EnterpriseStickerBlacklistEntry:
        ...

    def delete(self, tenant_id: str, chat_id: int, sticker_file_id: str) -> None:
        ...

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseStickerBlacklistEntry]:
        ...


class EnterpriseAntiChannelRepository(Protocol):
    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiChannelConfig]:
        ...

    def set(self, config: EnterpriseAntiChannelConfig) -> EnterpriseAntiChannelConfig:
        ...


class InMemoryAntiSpamRepository:
    def __init__(self):
        self._configs: Dict[Tuple[str, int], EnterpriseAntiSpamConfig] = {}

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiSpamConfig]:
        return self._configs.get((tenant_id, chat_id))

    def set(self, config: EnterpriseAntiSpamConfig) -> EnterpriseAntiSpamConfig:
        self._configs[(config.tenant_id, config.chat_id)] = config
        return config


class InMemoryBlacklistRepository:
    def __init__(self):
        self._items: Dict[Tuple[str, int, str], EnterpriseBlacklistEntry] = {}

    def add(self, entry: EnterpriseBlacklistEntry) -> EnterpriseBlacklistEntry:
        self._items[(entry.tenant_id, entry.chat_id, entry.pattern)] = entry
        return entry

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        self._items.pop((tenant_id, chat_id, pattern), None)

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseBlacklistEntry]:
        return [
            item
            for (t_id, c_id, _), item in self._items.items()
            if t_id == tenant_id and c_id == chat_id
        ]


class InMemoryStickerBlacklistRepository:
    def __init__(self):
        self._items: Dict[Tuple[str, int, str], EnterpriseStickerBlacklistEntry] = {}

    def add(self, entry: EnterpriseStickerBlacklistEntry) -> EnterpriseStickerBlacklistEntry:
        self._items[(entry.tenant_id, entry.chat_id, entry.sticker_file_id)] = entry
        return entry

    def delete(self, tenant_id: str, chat_id: int, sticker_file_id: str) -> None:
        self._items.pop((tenant_id, chat_id, sticker_file_id), None)

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseStickerBlacklistEntry]:
        return [
            item
            for (t_id, c_id, _), item in self._items.items()
            if t_id == tenant_id and c_id == chat_id
        ]


class InMemoryAntiChannelRepository:
    def __init__(self):
        self._configs: Dict[Tuple[str, int], EnterpriseAntiChannelConfig] = {}

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiChannelConfig]:
        return self._configs.get((tenant_id, chat_id))

    def set(self, config: EnterpriseAntiChannelConfig) -> EnterpriseAntiChannelConfig:
        self._configs[(config.tenant_id, config.chat_id)] = config
        return config


class PostgresAntiSpamRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiSpamConfig]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseAntiSpamModel).filter(
                EnterpriseAntiSpamModel.tenant_id == tenant_id,
                EnterpriseAntiSpamModel.chat_id == chat_id,
            ).first()
            if not row:
                return None
            return EnterpriseAntiSpamConfig(
                tenant_id=row.tenant_id,
                chat_id=row.chat_id,
                enabled=bool(row.enabled),
                spamwatch_enabled=bool(row.spamwatch_enabled),
                sibyl_enabled=bool(row.sibyl_enabled),
                created_at=row.created_at,
            )
        finally:
            session.close()

    def set(self, config: EnterpriseAntiSpamConfig) -> EnterpriseAntiSpamConfig:
        session = self._get_session()
        try:
            row = session.query(EnterpriseAntiSpamModel).filter(
                EnterpriseAntiSpamModel.tenant_id == config.tenant_id,
                EnterpriseAntiSpamModel.chat_id == config.chat_id,
            ).first()
            if row is None:
                row = EnterpriseAntiSpamModel(
                    tenant_id=config.tenant_id,
                    chat_id=config.chat_id,
                    enabled=1 if config.enabled else 0,
                    spamwatch_enabled=1 if config.spamwatch_enabled else 0,
                    sibyl_enabled=1 if config.sibyl_enabled else 0,
                )
                session.add(row)
            else:
                row.enabled = 1 if config.enabled else 0
                row.spamwatch_enabled = 1 if config.spamwatch_enabled else 0
                row.sibyl_enabled = 1 if config.sibyl_enabled else 0
                row.updated_at = datetime.utcnow()
            session.commit()
            return config
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class PostgresBlacklistRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def add(self, entry: EnterpriseBlacklistEntry) -> EnterpriseBlacklistEntry:
        session = self._get_session()
        try:
            row = session.query(EnterpriseBlacklistModel).filter(
                EnterpriseBlacklistModel.tenant_id == entry.tenant_id,
                EnterpriseBlacklistModel.chat_id == entry.chat_id,
                EnterpriseBlacklistModel.pattern == entry.pattern,
            ).first()
            if row is None:
                row = EnterpriseBlacklistModel(
                    tenant_id=entry.tenant_id,
                    chat_id=entry.chat_id,
                    pattern=entry.pattern,
                )
                session.add(row)
            else:
                row.updated_at = datetime.utcnow()
            session.commit()
            return entry
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseBlacklistModel).filter(
                EnterpriseBlacklistModel.tenant_id == tenant_id,
                EnterpriseBlacklistModel.chat_id == chat_id,
                EnterpriseBlacklistModel.pattern == pattern,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseBlacklistEntry]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseBlacklistModel).filter(
                EnterpriseBlacklistModel.tenant_id == tenant_id,
                EnterpriseBlacklistModel.chat_id == chat_id,
            ).all()
            return [
                EnterpriseBlacklistEntry(
                    tenant_id=row.tenant_id,
                    chat_id=row.chat_id,
                    pattern=row.pattern,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        finally:
            session.close()


class PostgresStickerBlacklistRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def add(self, entry: EnterpriseStickerBlacklistEntry) -> EnterpriseStickerBlacklistEntry:
        session = self._get_session()
        try:
            row = session.query(EnterpriseStickerBlacklistModel).filter(
                EnterpriseStickerBlacklistModel.tenant_id == entry.tenant_id,
                EnterpriseStickerBlacklistModel.chat_id == entry.chat_id,
                EnterpriseStickerBlacklistModel.sticker_file_id == entry.sticker_file_id,
            ).first()
            if row is None:
                row = EnterpriseStickerBlacklistModel(
                    tenant_id=entry.tenant_id,
                    chat_id=entry.chat_id,
                    sticker_file_id=entry.sticker_file_id,
                )
                session.add(row)
            else:
                row.updated_at = datetime.utcnow()
            session.commit()
            return entry
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str, chat_id: int, sticker_file_id: str) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseStickerBlacklistModel).filter(
                EnterpriseStickerBlacklistModel.tenant_id == tenant_id,
                EnterpriseStickerBlacklistModel.chat_id == chat_id,
                EnterpriseStickerBlacklistModel.sticker_file_id == sticker_file_id,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseStickerBlacklistEntry]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseStickerBlacklistModel).filter(
                EnterpriseStickerBlacklistModel.tenant_id == tenant_id,
                EnterpriseStickerBlacklistModel.chat_id == chat_id,
            ).all()
            return [
                EnterpriseStickerBlacklistEntry(
                    tenant_id=row.tenant_id,
                    chat_id=row.chat_id,
                    sticker_file_id=row.sticker_file_id,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        finally:
            session.close()


class PostgresAntiChannelRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseAntiChannelConfig]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseAntiChannelModel).filter(
                EnterpriseAntiChannelModel.tenant_id == tenant_id,
                EnterpriseAntiChannelModel.chat_id == chat_id,
            ).first()
            if not row:
                return None
            return EnterpriseAntiChannelConfig(
                tenant_id=row.tenant_id,
                chat_id=row.chat_id,
                enabled=bool(row.enabled),
                created_at=row.created_at,
            )
        finally:
            session.close()

    def set(self, config: EnterpriseAntiChannelConfig) -> EnterpriseAntiChannelConfig:
        session = self._get_session()
        try:
            row = session.query(EnterpriseAntiChannelModel).filter(
                EnterpriseAntiChannelModel.tenant_id == config.tenant_id,
                EnterpriseAntiChannelModel.chat_id == config.chat_id,
            ).first()
            if row is None:
                row = EnterpriseAntiChannelModel(
                    tenant_id=config.tenant_id,
                    chat_id=config.chat_id,
                    enabled=1 if config.enabled else 0,
                )
                session.add(row)
            else:
                row.enabled = 1 if config.enabled else 0
                row.updated_at = datetime.utcnow()
            session.commit()
            return config
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


_antispam_repo: Optional[InMemoryAntiSpamRepository] = None
_blacklist_repo: Optional[InMemoryBlacklistRepository] = None
_sticker_blacklist_repo: Optional[InMemoryStickerBlacklistRepository] = None
_antichannel_repo: Optional[InMemoryAntiChannelRepository] = None
_pg_antispam_repo: Optional[PostgresAntiSpamRepository] = None
_pg_blacklist_repo: Optional[PostgresBlacklistRepository] = None
_pg_sticker_blacklist_repo: Optional[PostgresStickerBlacklistRepository] = None
_pg_antichannel_repo: Optional[PostgresAntiChannelRepository] = None


def _postgres_enabled() -> bool:
    settings = load_api_settings()
    return settings.is_postgres_enabled() and not settings.is_storage_disabled()


def get_antispam_repo() -> EnterpriseAntiSpamRepository:
    global _antispam_repo, _pg_antispam_repo
    if _postgres_enabled():
        if _pg_antispam_repo is None:
            _pg_antispam_repo = PostgresAntiSpamRepository(load_api_settings().database_url)
        return _pg_antispam_repo
    if _antispam_repo is None:
        _antispam_repo = InMemoryAntiSpamRepository()
    return _antispam_repo


def get_blacklist_repo() -> EnterpriseBlacklistRepository:
    global _blacklist_repo, _pg_blacklist_repo
    if _postgres_enabled():
        if _pg_blacklist_repo is None:
            _pg_blacklist_repo = PostgresBlacklistRepository(load_api_settings().database_url)
        return _pg_blacklist_repo
    if _blacklist_repo is None:
        _blacklist_repo = InMemoryBlacklistRepository()
    return _blacklist_repo


def get_sticker_blacklist_repo() -> EnterpriseStickerBlacklistRepository:
    global _sticker_blacklist_repo, _pg_sticker_blacklist_repo
    if _postgres_enabled():
        if _pg_sticker_blacklist_repo is None:
            _pg_sticker_blacklist_repo = PostgresStickerBlacklistRepository(load_api_settings().database_url)
        return _pg_sticker_blacklist_repo
    if _sticker_blacklist_repo is None:
        _sticker_blacklist_repo = InMemoryStickerBlacklistRepository()
    return _sticker_blacklist_repo


def get_antichannel_repo() -> EnterpriseAntiChannelRepository:
    global _antichannel_repo, _pg_antichannel_repo
    if _postgres_enabled():
        if _pg_antichannel_repo is None:
            _pg_antichannel_repo = PostgresAntiChannelRepository(load_api_settings().database_url)
        return _pg_antichannel_repo
    if _antichannel_repo is None:
        _antichannel_repo = InMemoryAntiChannelRepository()
    return _antichannel_repo

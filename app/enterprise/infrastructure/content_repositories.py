"""Repositories for EnterpriseRobot content (rules, welcome, notes, filters)."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, Optional, Protocol, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import load_api_settings
from app.database.models import (
    EnterpriseRule as EnterpriseRuleModel,
    EnterpriseWelcome as EnterpriseWelcomeModel,
    EnterpriseNote as EnterpriseNoteModel,
    EnterpriseFilter as EnterpriseFilterModel,
)
from app.enterprise.domain.entities import (
    EnterpriseFilter,
    EnterpriseNote,
    EnterpriseRule,
    EnterpriseWelcome,
)


class EnterpriseRulesRepository(Protocol):
    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseRule]:
        ...

    def set(self, rule: EnterpriseRule) -> EnterpriseRule:
        ...


class EnterpriseWelcomeRepository(Protocol):
    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseWelcome]:
        ...

    def set(self, welcome: EnterpriseWelcome) -> EnterpriseWelcome:
        ...


class EnterpriseNotesRepository(Protocol):
    def get(self, tenant_id: str, chat_id: int, note_key: str) -> Optional[EnterpriseNote]:
        ...

    def set(self, note: EnterpriseNote) -> EnterpriseNote:
        ...

    def delete(self, tenant_id: str, chat_id: int, note_key: str) -> None:
        ...

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseNote]:
        ...


class EnterpriseFiltersRepository(Protocol):
    def add(self, item: EnterpriseFilter) -> EnterpriseFilter:
        ...

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        ...

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseFilter]:
        ...


class InMemoryRulesRepository:
    def __init__(self):
        self._rules: Dict[Tuple[str, int], EnterpriseRule] = {}

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseRule]:
        return self._rules.get((tenant_id, chat_id))

    def set(self, rule: EnterpriseRule) -> EnterpriseRule:
        self._rules[(rule.tenant_id, rule.chat_id)] = rule
        return rule


class InMemoryWelcomeRepository:
    def __init__(self):
        self._welcome: Dict[Tuple[str, int], EnterpriseWelcome] = {}

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseWelcome]:
        return self._welcome.get((tenant_id, chat_id))

    def set(self, welcome: EnterpriseWelcome) -> EnterpriseWelcome:
        self._welcome[(welcome.tenant_id, welcome.chat_id)] = welcome
        return welcome


class InMemoryNotesRepository:
    def __init__(self):
        self._notes: Dict[Tuple[str, int, str], EnterpriseNote] = {}

    def get(self, tenant_id: str, chat_id: int, note_key: str) -> Optional[EnterpriseNote]:
        return self._notes.get((tenant_id, chat_id, note_key))

    def set(self, note: EnterpriseNote) -> EnterpriseNote:
        self._notes[(note.tenant_id, note.chat_id, note.note_key)] = note
        return note

    def delete(self, tenant_id: str, chat_id: int, note_key: str) -> None:
        self._notes.pop((tenant_id, chat_id, note_key), None)

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseNote]:
        return [n for (t_id, c_id, _), n in self._notes.items() if t_id == tenant_id and c_id == chat_id]


class InMemoryFiltersRepository:
    def __init__(self):
        self._filters: Dict[Tuple[str, int, str], EnterpriseFilter] = {}

    def add(self, item: EnterpriseFilter) -> EnterpriseFilter:
        self._filters[(item.tenant_id, item.chat_id, item.pattern)] = item
        return item

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        self._filters.pop((tenant_id, chat_id, pattern), None)

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseFilter]:
        return [f for (t_id, c_id, _), f in self._filters.items() if t_id == tenant_id and c_id == chat_id]


class PostgresRulesRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseRule]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseRuleModel).filter(
                EnterpriseRuleModel.tenant_id == tenant_id,
                EnterpriseRuleModel.chat_id == chat_id,
            ).first()
            if not row:
                return None
            return EnterpriseRule(tenant_id=row.tenant_id, chat_id=row.chat_id, rules_text=row.rules_text, created_at=row.created_at)
        finally:
            session.close()

    def set(self, rule: EnterpriseRule) -> EnterpriseRule:
        session = self._get_session()
        try:
            row = session.query(EnterpriseRuleModel).filter(
                EnterpriseRuleModel.tenant_id == rule.tenant_id,
                EnterpriseRuleModel.chat_id == rule.chat_id,
            ).first()
            if row is None:
                row = EnterpriseRuleModel(
                    tenant_id=rule.tenant_id,
                    chat_id=rule.chat_id,
                    rules_text=rule.rules_text,
                )
                session.add(row)
            else:
                row.rules_text = rule.rules_text
                row.updated_at = datetime.utcnow()
            session.commit()
            return rule
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class PostgresWelcomeRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, chat_id: int) -> Optional[EnterpriseWelcome]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseWelcomeModel).filter(
                EnterpriseWelcomeModel.tenant_id == tenant_id,
                EnterpriseWelcomeModel.chat_id == chat_id,
            ).first()
            if not row:
                return None
            return EnterpriseWelcome(
                tenant_id=row.tenant_id,
                chat_id=row.chat_id,
                welcome_text=row.welcome_text,
                enabled=bool(row.enabled),
                created_at=row.created_at,
            )
        finally:
            session.close()

    def set(self, welcome: EnterpriseWelcome) -> EnterpriseWelcome:
        session = self._get_session()
        try:
            row = session.query(EnterpriseWelcomeModel).filter(
                EnterpriseWelcomeModel.tenant_id == welcome.tenant_id,
                EnterpriseWelcomeModel.chat_id == welcome.chat_id,
            ).first()
            if row is None:
                row = EnterpriseWelcomeModel(
                    tenant_id=welcome.tenant_id,
                    chat_id=welcome.chat_id,
                    welcome_text=welcome.welcome_text,
                    enabled=1 if welcome.enabled else 0,
                )
                session.add(row)
            else:
                row.welcome_text = welcome.welcome_text
                row.enabled = 1 if welcome.enabled else 0
                row.updated_at = datetime.utcnow()
            session.commit()
            return welcome
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class PostgresNotesRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def get(self, tenant_id: str, chat_id: int, note_key: str) -> Optional[EnterpriseNote]:
        session = self._get_session()
        try:
            row = session.query(EnterpriseNoteModel).filter(
                EnterpriseNoteModel.tenant_id == tenant_id,
                EnterpriseNoteModel.chat_id == chat_id,
                EnterpriseNoteModel.note_key == note_key,
            ).first()
            if not row:
                return None
            return EnterpriseNote(
                tenant_id=row.tenant_id,
                chat_id=row.chat_id,
                note_key=row.note_key,
                content_type=row.content_type,
                content_text=row.content_text,
                file_id=row.file_id,
                created_at=row.created_at,
            )
        finally:
            session.close()

    def set(self, note: EnterpriseNote) -> EnterpriseNote:
        session = self._get_session()
        try:
            row = session.query(EnterpriseNoteModel).filter(
                EnterpriseNoteModel.tenant_id == note.tenant_id,
                EnterpriseNoteModel.chat_id == note.chat_id,
                EnterpriseNoteModel.note_key == note.note_key,
            ).first()
            if row is None:
                row = EnterpriseNoteModel(
                    tenant_id=note.tenant_id,
                    chat_id=note.chat_id,
                    note_key=note.note_key,
                    content_type=note.content_type,
                    content_text=note.content_text,
                    file_id=note.file_id,
                )
                session.add(row)
            else:
                row.content_type = note.content_type
                row.content_text = note.content_text
                row.file_id = note.file_id
                row.updated_at = datetime.utcnow()
            session.commit()
            return note
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str, chat_id: int, note_key: str) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseNoteModel).filter(
                EnterpriseNoteModel.tenant_id == tenant_id,
                EnterpriseNoteModel.chat_id == chat_id,
                EnterpriseNoteModel.note_key == note_key,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseNote]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseNoteModel).filter(
                EnterpriseNoteModel.tenant_id == tenant_id,
                EnterpriseNoteModel.chat_id == chat_id,
            ).all()
            return [
                EnterpriseNote(
                    tenant_id=row.tenant_id,
                    chat_id=row.chat_id,
                    note_key=row.note_key,
                    content_type=row.content_type,
                    content_text=row.content_text,
                    file_id=row.file_id,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        finally:
            session.close()


class PostgresFiltersRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def add(self, item: EnterpriseFilter) -> EnterpriseFilter:
        session = self._get_session()
        try:
            row = session.query(EnterpriseFilterModel).filter(
                EnterpriseFilterModel.tenant_id == item.tenant_id,
                EnterpriseFilterModel.chat_id == item.chat_id,
                EnterpriseFilterModel.pattern == item.pattern,
            ).first()
            if row is None:
                row = EnterpriseFilterModel(
                    tenant_id=item.tenant_id,
                    chat_id=item.chat_id,
                    pattern=item.pattern,
                    response_text=item.response_text,
                )
                session.add(row)
            else:
                row.response_text = item.response_text
                row.updated_at = datetime.utcnow()
            session.commit()
            return item
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, tenant_id: str, chat_id: int, pattern: str) -> None:
        session = self._get_session()
        try:
            session.query(EnterpriseFilterModel).filter(
                EnterpriseFilterModel.tenant_id == tenant_id,
                EnterpriseFilterModel.chat_id == chat_id,
                EnterpriseFilterModel.pattern == pattern,
            ).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list(self, tenant_id: str, chat_id: int) -> Iterable[EnterpriseFilter]:
        session = self._get_session()
        try:
            rows = session.query(EnterpriseFilterModel).filter(
                EnterpriseFilterModel.tenant_id == tenant_id,
                EnterpriseFilterModel.chat_id == chat_id,
            ).all()
            return [
                EnterpriseFilter(
                    tenant_id=row.tenant_id,
                    chat_id=row.chat_id,
                    pattern=row.pattern,
                    response_text=row.response_text,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        finally:
            session.close()


_rules_repo: Optional[InMemoryRulesRepository] = None
_welcome_repo: Optional[InMemoryWelcomeRepository] = None
_notes_repo: Optional[InMemoryNotesRepository] = None
_filters_repo: Optional[InMemoryFiltersRepository] = None
_pg_rules_repo: Optional[PostgresRulesRepository] = None
_pg_welcome_repo: Optional[PostgresWelcomeRepository] = None
_pg_notes_repo: Optional[PostgresNotesRepository] = None
_pg_filters_repo: Optional[PostgresFiltersRepository] = None


def _postgres_enabled() -> bool:
    settings = load_api_settings()
    return settings.is_postgres_enabled() and not settings.is_storage_disabled()


def get_rules_repo() -> EnterpriseRulesRepository:
    global _rules_repo, _pg_rules_repo
    if _postgres_enabled():
        if _pg_rules_repo is None:
            _pg_rules_repo = PostgresRulesRepository(load_api_settings().database_url)
        return _pg_rules_repo
    if _rules_repo is None:
        _rules_repo = InMemoryRulesRepository()
    return _rules_repo


def get_welcome_repo() -> EnterpriseWelcomeRepository:
    global _welcome_repo, _pg_welcome_repo
    if _postgres_enabled():
        if _pg_welcome_repo is None:
            _pg_welcome_repo = PostgresWelcomeRepository(load_api_settings().database_url)
        return _pg_welcome_repo
    if _welcome_repo is None:
        _welcome_repo = InMemoryWelcomeRepository()
    return _welcome_repo


def get_notes_repo() -> EnterpriseNotesRepository:
    global _notes_repo, _pg_notes_repo
    if _postgres_enabled():
        if _pg_notes_repo is None:
            _pg_notes_repo = PostgresNotesRepository(load_api_settings().database_url)
        return _pg_notes_repo
    if _notes_repo is None:
        _notes_repo = InMemoryNotesRepository()
    return _notes_repo


def get_filters_repo() -> EnterpriseFiltersRepository:
    global _filters_repo, _pg_filters_repo
    if _postgres_enabled():
        if _pg_filters_repo is None:
            _pg_filters_repo = PostgresFiltersRepository(load_api_settings().database_url)
        return _pg_filters_repo
    if _filters_repo is None:
        _filters_repo = InMemoryFiltersRepository()
    return _filters_repo

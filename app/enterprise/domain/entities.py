"""Enterprise domain entities."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .roles import EnterpriseRole


@dataclass(frozen=True)
class EnterpriseUser:
    user_id: int
    tenant_id: str
    role: EnterpriseRole
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BanRecord:
    tenant_id: str
    user_id: int
    banned_by: int
    reason: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass(frozen=True)
class EnterpriseRule:
    tenant_id: str
    chat_id: int
    rules_text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseWelcome:
    tenant_id: str
    chat_id: int
    welcome_text: str
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseNote:
    tenant_id: str
    chat_id: int
    note_key: str
    content_type: str
    content_text: Optional[str]
    file_id: Optional[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseFilter:
    tenant_id: str
    chat_id: int
    pattern: str
    response_text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseAntiSpamConfig:
    tenant_id: str
    chat_id: int
    enabled: bool = False
    spamwatch_enabled: bool = False
    sibyl_enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseBlacklistEntry:
    tenant_id: str
    chat_id: int
    pattern: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseStickerBlacklistEntry:
    tenant_id: str
    chat_id: int
    sticker_file_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EnterpriseAntiChannelConfig:
    tenant_id: str
    chat_id: int
    enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

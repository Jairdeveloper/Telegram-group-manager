"""SQLAlchemy models for database."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})
    is_active = Column(Integer, default=1)

    def __repr__(self):
        return f"<Tenant(tenant_id={self.tenant_id}, name={self.name})>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    session_id = Column(String(255), index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSON, default={})

    __table_args__ = (
        Index("ix_conversations_tenant_session", "tenant_id", "session_id"),
    )

    def __repr__(self):
        return f"<Conversation(tenant_id={self.tenant_id}, session_id={self.session_id})>"


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(64), unique=True, index=True, nullable=False)
    tenant_id = Column(String(255), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False)
    permissions = Column(JSON, default=[])
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ApiKey(key_id={self.key_id}, tenant_id={self.tenant_id})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    tenant_id = Column(String(255), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    mfa_enabled = Column(Integer, default=0)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class EnterpriseUser(Base):
    __tablename__ = "enterprise_users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    user_id = Column(BigInteger, nullable=False)
    role = Column(String(50), nullable=False, default="user")
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_enterprise_users_tenant_user", "tenant_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<EnterpriseUser(tenant_id={self.tenant_id}, user_id={self.user_id}, role={self.role})>"


class EnterpriseBan(Base):
    __tablename__ = "enterprise_bans"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    user_id = Column(BigInteger, nullable=False)
    banned_by = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_enterprise_bans_tenant_user", "tenant_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<EnterpriseBan(tenant_id={self.tenant_id}, user_id={self.user_id})>"


class EnterpriseRule(Base):
    __tablename__ = "enterprise_rules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    rules_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_enterprise_rules_tenant_chat", "tenant_id", "chat_id", unique=True),
    )


class EnterpriseWelcome(Base):
    __tablename__ = "enterprise_welcome"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    welcome_text = Column(Text, nullable=False)
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_enterprise_welcome_tenant_chat", "tenant_id", "chat_id", unique=True),
    )


class EnterpriseNote(Base):
    __tablename__ = "enterprise_notes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    note_key = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False, default="text")
    content_text = Column(Text, nullable=True)
    file_id = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_enterprise_notes_tenant_chat_key",
            "tenant_id",
            "chat_id",
            "note_key",
            unique=True,
        ),
    )


class EnterpriseFilter(Base):
    __tablename__ = "enterprise_filters"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    pattern = Column(String(255), nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_enterprise_filters_tenant_chat_pattern",
            "tenant_id",
            "chat_id",
            "pattern",
            unique=True,
        ),
    )


class EnterpriseAntiSpam(Base):
    __tablename__ = "enterprise_antispam"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    enabled = Column(Integer, default=0)
    spamwatch_enabled = Column(Integer, default=0)
    sibyl_enabled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_enterprise_antispam_tenant_chat", "tenant_id", "chat_id", unique=True),
    )


class EnterpriseBlacklist(Base):
    __tablename__ = "enterprise_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    pattern = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_enterprise_blacklist_tenant_chat_pattern",
            "tenant_id",
            "chat_id",
            "pattern",
            unique=True,
        ),
    )


class EnterpriseStickerBlacklist(Base):
    __tablename__ = "enterprise_sticker_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    sticker_file_id = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_enterprise_sticker_blacklist_tenant_chat",
            "tenant_id",
            "chat_id",
            "sticker_file_id",
            unique=True,
        ),
    )


class EnterpriseAntiChannel(Base):
    __tablename__ = "enterprise_antichannel"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=False, default="default")
    chat_id = Column(BigInteger, nullable=False)
    enabled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_enterprise_antichannel_tenant_chat", "tenant_id", "chat_id", unique=True),
    )

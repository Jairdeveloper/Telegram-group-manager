"""Application services for EnterpriseRobot permissions, content, and moderation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import random
import re
from typing import Iterable, Optional, Sequence

import pytz

from app.audit.models import AuditEventType
from app.audit.service import get_audit_service
from app.guardrails.middleware import apply_guardrails
from app.policies import Action, PolicyEngine
from app.enterprise.domain.entities import (
    BanRecord,
    EnterpriseAntiChannelConfig,
    EnterpriseAntiSpamConfig,
    EnterpriseBlacklistEntry,
    EnterpriseFilter,
    EnterpriseNote,
    EnterpriseRule,
    EnterpriseStickerBlacklistEntry,
    EnterpriseUser,
    EnterpriseWelcome,
)
from app.enterprise.domain.roles import EnterpriseRole, has_role_at_least, parse_role
from app.enterprise.infrastructure.content_repositories import (
    EnterpriseFiltersRepository,
    EnterpriseNotesRepository,
    EnterpriseRulesRepository,
    EnterpriseWelcomeRepository,
)
from app.enterprise.infrastructure.repositories import (
    BanRepository,
    EnterpriseUserRepository,
)
from app.enterprise.infrastructure.moderation_repositories import (
    EnterpriseAntiChannelRepository,
    EnterpriseAntiSpamRepository,
    EnterpriseBlacklistRepository,
    EnterpriseStickerBlacklistRepository,
)


@dataclass(frozen=True)
class EnterpriseCommandResult:
    status: str
    response_text: str
    data: Optional[dict] = None


class EnterpriseUserService:
    def __init__(
        self,
        *,
        user_repo: EnterpriseUserRepository,
        ban_repo: BanRepository,
        policy_engine: Optional[PolicyEngine] = None,
        owner_ids: Optional[Sequence[int]] = None,
        sardegna_ids: Optional[Sequence[int]] = None,
        tenant_id: str = "default",
    ):
        self.user_repo = user_repo
        self.ban_repo = ban_repo
        self.policy_engine = policy_engine or PolicyEngine()
        self.owner_ids = set(owner_ids or ())
        self.sardegna_ids = set(sardegna_ids or ())
        self.tenant_id = tenant_id
        self.audit = get_audit_service()

    def ensure_actor(self, actor_id: int) -> EnterpriseUser:
        user = self.user_repo.get(self.tenant_id, actor_id)
        if user is not None:
            return user

        role = self._bootstrap_role(actor_id)
        user = EnterpriseUser(user_id=actor_id, tenant_id=self.tenant_id, role=role)
        return self.user_repo.upsert(user)

    def _bootstrap_role(self, actor_id: int) -> EnterpriseRole:
        if actor_id in self.sardegna_ids:
            return EnterpriseRole.SARDEGNA
        if actor_id in self.owner_ids:
            return EnterpriseRole.OWNER
        if self.user_repo.count(self.tenant_id) == 0:
            return EnterpriseRole.OWNER
        return EnterpriseRole.USER

    def list_users(self) -> Iterable[EnterpriseUser]:
        return self.user_repo.list(self.tenant_id)

    def upsert_user(self, actor_id: int, target_id: int, role_raw: str) -> EnterpriseUser:
        actor = self.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, EnterpriseRole.DEV):
            raise PermissionError("Insufficient permissions for user management")

        role = parse_role(role_raw)
        if role == EnterpriseRole.SARDEGNA and not has_role_at_least(actor.role, EnterpriseRole.OWNER):
            raise PermissionError("Only OWNER can assign SARDEGNA")

        user = EnterpriseUser(user_id=target_id, tenant_id=self.tenant_id, role=role)
        user = self.user_repo.upsert(user)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.USER_UPDATE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="enterprise_user",
            resource_id=str(target_id),
            action="upsert_user",
        )
        return user

    def delete_user(self, actor_id: int, target_id: int) -> None:
        actor = self.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, EnterpriseRole.OWNER):
            raise PermissionError("Only OWNER can delete users")
        self.user_repo.delete(self.tenant_id, target_id)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.USER_DELETE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="enterprise_user",
            resource_id=str(target_id),
            action="delete_user",
        )

    def ban_user(self, actor_id: int, target_id: int, reason: str) -> BanRecord:
        actor = self.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, EnterpriseRole.SUDO):
            raise PermissionError("Insufficient permissions to ban users")

        record = BanRecord(
            tenant_id=self.tenant_id,
            user_id=target_id,
            banned_by=actor_id,
            reason=reason or "no reason",
        )
        record = self.ban_repo.ban(record)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.POLICY_VIOLATION,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="ban",
            resource_id=str(target_id),
            action="ban_user",
            metadata={"reason": record.reason},
        )
        return record

    def unban_user(self, actor_id: int, target_id: int, reason: str) -> None:
        actor = self.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, EnterpriseRole.SUDO):
            raise PermissionError("Insufficient permissions to unban users")

        self.ban_repo.unban(self.tenant_id, target_id)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.POLICY_VIOLATION,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="ban",
            resource_id=str(target_id),
            action="unban_user",
            metadata={"reason": reason or "no reason"},
        )

    def evaluate_policy(self, actor_id: int, message: str) -> EnterpriseCommandResult:
        action, message_text = self.policy_engine.evaluate(
            self.tenant_id,
            {
                "tenant_id": self.tenant_id,
                "user_id": actor_id,
                "message": message or "",
            },
        )
        if action == Action.DENY:
            return EnterpriseCommandResult(status="denied", response_text=message_text or "Policy denied")
        if action == Action.THROTTLE:
            return EnterpriseCommandResult(status="throttled", response_text=message_text or "Policy throttled")
        if action == Action.WARN:
            return EnterpriseCommandResult(status="warn", response_text=message_text or "Policy warning")
        return EnterpriseCommandResult(status="ok", response_text="")

    def guardrails_check(self, message: str) -> Optional[str]:
        result = apply_guardrails(message or "")
        if not result.allowed:
            return result.reason or "Guardrails blocked content"
        return None


class EnterpriseContentService:
    def __init__(
        self,
        *,
        user_service: EnterpriseUserService,
        rules_repo: EnterpriseRulesRepository,
        welcome_repo: EnterpriseWelcomeRepository,
        notes_repo: EnterpriseNotesRepository,
        filters_repo: EnterpriseFiltersRepository,
        tenant_id: str = "default",
    ):
        self.user_service = user_service
        self.rules_repo = rules_repo
        self.welcome_repo = welcome_repo
        self.notes_repo = notes_repo
        self.filters_repo = filters_repo
        self.tenant_id = tenant_id
        self.audit = get_audit_service()

    def _ensure_role(self, actor_id: int, required_role: EnterpriseRole) -> EnterpriseUser:
        actor = self.user_service.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, required_role):
            raise PermissionError("Insufficient permissions")
        return actor

    def set_rules(self, actor_id: int, chat_id: int, rules_text: str) -> EnterpriseRule:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        rule = EnterpriseRule(tenant_id=self.tenant_id, chat_id=chat_id, rules_text=rules_text)
        rule = self.rules_repo.set(rule)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="rules",
            resource_id=str(chat_id),
            action="set_rules",
        )
        return rule

    def get_rules(self, chat_id: int) -> Optional[EnterpriseRule]:
        return self.rules_repo.get(self.tenant_id, chat_id)

    def set_welcome(self, actor_id: int, chat_id: int, welcome_text: str) -> EnterpriseWelcome:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        welcome = EnterpriseWelcome(tenant_id=self.tenant_id, chat_id=chat_id, welcome_text=welcome_text)
        welcome = self.welcome_repo.set(welcome)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="welcome",
            resource_id=str(chat_id),
            action="set_welcome",
        )
        return welcome

    def get_welcome(self, chat_id: int) -> Optional[EnterpriseWelcome]:
        return self.welcome_repo.get(self.tenant_id, chat_id)

    def set_note(
        self,
        actor_id: int,
        chat_id: int,
        note_key: str,
        content_text: Optional[str],
        content_type: str = "text",
        file_id: Optional[str] = None,
    ) -> EnterpriseNote:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        note = EnterpriseNote(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            note_key=note_key,
            content_type=content_type,
            content_text=content_text,
            file_id=file_id,
        )
        note = self.notes_repo.set(note)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="note",
            resource_id=f"{chat_id}:{note_key}",
            action="set_note",
        )
        return note

    def get_note(self, chat_id: int, note_key: str) -> Optional[EnterpriseNote]:
        return self.notes_repo.get(self.tenant_id, chat_id, note_key)

    def delete_note(self, actor_id: int, chat_id: int, note_key: str) -> None:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        self.notes_repo.delete(self.tenant_id, chat_id, note_key)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="note",
            resource_id=f"{chat_id}:{note_key}",
            action="delete_note",
        )

    def list_notes(self, chat_id: int) -> Iterable[EnterpriseNote]:
        return self.notes_repo.list(self.tenant_id, chat_id)

    def add_filter(self, actor_id: int, chat_id: int, pattern: str, response_text: str) -> EnterpriseFilter:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        item = EnterpriseFilter(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            pattern=pattern,
            response_text=response_text,
        )
        item = self.filters_repo.add(item)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="filter",
            resource_id=f"{chat_id}:{pattern}",
            action="add_filter",
        )
        return item

    def delete_filter(self, actor_id: int, chat_id: int, pattern: str) -> None:
        self._ensure_role(actor_id, EnterpriseRole.SUPPORT)
        self.filters_repo.delete(self.tenant_id, chat_id, pattern)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="filter",
            resource_id=f"{chat_id}:{pattern}",
            action="delete_filter",
        )

    def list_filters(self, chat_id: int) -> Iterable[EnterpriseFilter]:
        return self.filters_repo.list(self.tenant_id, chat_id)


@dataclass(frozen=True)
class EnterpriseModerationDecision:
    status: str
    response_text: str
    reason: str = ""
    source: str = ""


class EnterpriseModerationService:
    def __init__(
        self,
        *,
        user_service: EnterpriseUserService,
        antispam_repo: EnterpriseAntiSpamRepository,
        blacklist_repo: EnterpriseBlacklistRepository,
        sticker_blacklist_repo: EnterpriseStickerBlacklistRepository,
        antichannel_repo: EnterpriseAntiChannelRepository,
        spamwatch_client=None,
        sibyl_client=None,
        tenant_id: str = "default",
    ):
        self.user_service = user_service
        self.antispam_repo = antispam_repo
        self.blacklist_repo = blacklist_repo
        self.sticker_blacklist_repo = sticker_blacklist_repo
        self.antichannel_repo = antichannel_repo
        self.spamwatch_client = spamwatch_client
        self.sibyl_client = sibyl_client
        self.tenant_id = tenant_id
        self.audit = get_audit_service()

    def _ensure_role(self, actor_id: int, required_role: EnterpriseRole) -> EnterpriseUser:
        actor = self.user_service.ensure_actor(actor_id)
        if not has_role_at_least(actor.role, required_role):
            raise PermissionError("Insufficient permissions")
        return actor

    def _validate_blacklist_pattern(self, pattern: str) -> None:
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValueError(f"Invalid pattern: {exc}") from exc

    def set_antispam(
        self,
        actor_id: int,
        chat_id: int,
        *,
        enabled: bool,
        spamwatch_enabled: bool,
        sibyl_enabled: bool,
    ) -> EnterpriseAntiSpamConfig:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        config = EnterpriseAntiSpamConfig(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            enabled=enabled,
            spamwatch_enabled=spamwatch_enabled,
            sibyl_enabled=sibyl_enabled,
        )
        config = self.antispam_repo.set(config)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="antispam",
            resource_id=str(chat_id),
            action="set_antispam",
            metadata={
                "enabled": enabled,
                "spamwatch_enabled": spamwatch_enabled,
                "sibyl_enabled": sibyl_enabled,
            },
        )
        return config

    def get_antispam(self, chat_id: int) -> Optional[EnterpriseAntiSpamConfig]:
        return self.antispam_repo.get(self.tenant_id, chat_id)

    def set_antichannel(self, actor_id: int, chat_id: int, *, enabled: bool) -> EnterpriseAntiChannelConfig:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        config = EnterpriseAntiChannelConfig(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            enabled=enabled,
        )
        config = self.antichannel_repo.set(config)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="antichannel",
            resource_id=str(chat_id),
            action="set_antichannel",
            metadata={"enabled": enabled},
        )
        return config

    def get_antichannel(self, chat_id: int) -> Optional[EnterpriseAntiChannelConfig]:
        return self.antichannel_repo.get(self.tenant_id, chat_id)

    def add_blacklist(self, actor_id: int, chat_id: int, pattern: str) -> EnterpriseBlacklistEntry:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        self._validate_blacklist_pattern(pattern)
        entry = EnterpriseBlacklistEntry(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            pattern=pattern,
        )
        entry = self.blacklist_repo.add(entry)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="blacklist",
            resource_id=f"{chat_id}:{pattern}",
            action="add_blacklist",
        )
        return entry

    def delete_blacklist(self, actor_id: int, chat_id: int, pattern: str) -> None:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        self.blacklist_repo.delete(self.tenant_id, chat_id, pattern)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="blacklist",
            resource_id=f"{chat_id}:{pattern}",
            action="delete_blacklist",
        )

    def list_blacklist(self, chat_id: int) -> Iterable[EnterpriseBlacklistEntry]:
        return self.blacklist_repo.list(self.tenant_id, chat_id)

    def add_sticker_blacklist(
        self, actor_id: int, chat_id: int, sticker_file_id: str
    ) -> EnterpriseStickerBlacklistEntry:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        entry = EnterpriseStickerBlacklistEntry(
            tenant_id=self.tenant_id,
            chat_id=chat_id,
            sticker_file_id=sticker_file_id,
        )
        entry = self.sticker_blacklist_repo.add(entry)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="sticker_blacklist",
            resource_id=f"{chat_id}:{sticker_file_id}",
            action="add_sticker_blacklist",
        )
        return entry

    def delete_sticker_blacklist(self, actor_id: int, chat_id: int, sticker_file_id: str) -> None:
        self._ensure_role(actor_id, EnterpriseRole.SUDO)
        self.sticker_blacklist_repo.delete(self.tenant_id, chat_id, sticker_file_id)
        self.audit.log(
            tenant_id=self.tenant_id,
            event_type=AuditEventType.CONFIG_CHANGE,
            actor_id=str(actor_id),
            actor_type="enterprise_user",
            resource_type="sticker_blacklist",
            resource_id=f"{chat_id}:{sticker_file_id}",
            action="delete_sticker_blacklist",
        )

    def list_sticker_blacklist(self, chat_id: int) -> Iterable[EnterpriseStickerBlacklistEntry]:
        return self.sticker_blacklist_repo.list(self.tenant_id, chat_id)

    def _is_exempt(self, actor_id: int) -> bool:
        actor = self.user_service.ensure_actor(actor_id)
        return has_role_at_least(actor.role, EnterpriseRole.WHITELIST)

    def evaluate_message(
        self,
        *,
        actor_id: int,
        chat_id: int,
        text: str,
        sticker_file_id: Optional[str],
        sender_chat_type: Optional[str],
    ) -> EnterpriseModerationDecision:
        if self._is_exempt(actor_id):
            return EnterpriseModerationDecision(status="allowed", response_text="")

        antichannel = self.get_antichannel(chat_id)
        if antichannel and antichannel.enabled and (sender_chat_type or "").lower() == "channel":
            self.audit.log(
                tenant_id=self.tenant_id,
                event_type=AuditEventType.POLICY_VIOLATION,
                actor_id=str(actor_id),
                actor_type="enterprise_user",
                resource_type="chat",
                resource_id=str(chat_id),
                action="antichannel_block",
            )
            return EnterpriseModerationDecision(
                status="blocked",
                response_text="Mensaje bloqueado (antichannel activo).",
                reason="antichannel",
                source="antichannel",
            )

        if sticker_file_id:
            for entry in self.list_sticker_blacklist(chat_id):
                if entry.sticker_file_id == sticker_file_id:
                    self.audit.log(
                        tenant_id=self.tenant_id,
                        event_type=AuditEventType.POLICY_VIOLATION,
                        actor_id=str(actor_id),
                        actor_type="enterprise_user",
                        resource_type="chat",
                        resource_id=str(chat_id),
                        action="sticker_blacklist_block",
                        metadata={"sticker_file_id": sticker_file_id},
                    )
                    return EnterpriseModerationDecision(
                        status="blocked",
                        response_text="Mensaje bloqueado (sticker en blacklist).",
                        reason="sticker_blacklist",
                        source="sticker_blacklist",
                    )

        if text:
            for entry in self.list_blacklist(chat_id):
                try:
                    if re.search(entry.pattern, text, re.IGNORECASE):
                        self.audit.log(
                            tenant_id=self.tenant_id,
                            event_type=AuditEventType.POLICY_VIOLATION,
                            actor_id=str(actor_id),
                            actor_type="enterprise_user",
                            resource_type="chat",
                            resource_id=str(chat_id),
                            action="blacklist_block",
                            metadata={"pattern": entry.pattern},
                        )
                        return EnterpriseModerationDecision(
                            status="blocked",
                            response_text="Mensaje bloqueado (texto en blacklist).",
                            reason="blacklist",
                            source="blacklist",
                        )
                except re.error:
                    continue

        antispam = self.get_antispam(chat_id)
        if antispam and antispam.enabled:
            if antispam.spamwatch_enabled and self.spamwatch_client is not None:
                result = self.spamwatch_client.check_user(actor_id)
                if result and result.banned:
                    self.audit.log(
                        tenant_id=self.tenant_id,
                        event_type=AuditEventType.POLICY_VIOLATION,
                        actor_id=str(actor_id),
                        actor_type="enterprise_user",
                        resource_type="chat",
                        resource_id=str(chat_id),
                        action="spamwatch_block",
                        metadata={"reason": result.reason},
                    )
                    reason_text = result.reason or "SpamWatch report"
                    return EnterpriseModerationDecision(
                        status="blocked",
                        response_text=f"Mensaje bloqueado (SpamWatch: {reason_text}).",
                        reason="spamwatch",
                        source="spamwatch",
                    )

            if antispam.sibyl_enabled and self.sibyl_client is not None:
                result = self.sibyl_client.check_user(actor_id)
                if result and result.banned:
                    self.audit.log(
                        tenant_id=self.tenant_id,
                        event_type=AuditEventType.POLICY_VIOLATION,
                        actor_id=str(actor_id),
                        actor_type="enterprise_user",
                        resource_type="chat",
                        resource_id=str(chat_id),
                        action="sibyl_block",
                        metadata={"reason": result.reason},
                    )
                    reason_text = result.reason or "Sibyl report"
                    return EnterpriseModerationDecision(
                        status="blocked",
                        response_text=f"Mensaje bloqueado (Sibyl: {reason_text}).",
                        reason="sibyl",
                        source="sibyl",
                    )

        return EnterpriseModerationDecision(status="allowed", response_text="")


class EnterpriseUtilityService:
    def __init__(
        self,
        *,
        feature_flags: dict,
        default_timezone: str = "UTC",
        anilist_client=None,
    ):
        self.feature_flags = feature_flags
        self.default_timezone = default_timezone or "UTC"
        self.anilist_client = anilist_client

    def is_enabled(self, module: str) -> bool:
        return bool(self.feature_flags.get(module, False))

    def get_time(self, tz_name: Optional[str] = None) -> str:
        tz_name = (tz_name or self.default_timezone or "UTC").strip()
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            return "Zona horaria invalida. Ej: UTC, Europe/Madrid, America/Mexico_City"
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")

    def random_fun(self) -> str:
        jokes = [
            "Si el robot se queda sin energia, es un dia de mantenimiento.",
            "Debugging: cuando te das cuenta de que el bug eras tu.",
            "Los bots tambien sueñan con bytes electricos.",
            "Manual de usuario: leer antes de presionar todos los botones.",
            "Hoy el cafe esta en modo turbo. El robot tambien.",
        ]
        return random.choice(jokes)

    def reaction_for_text(self, text: str) -> str:
        normalized = (text or "").strip().lower()
        if not normalized:
            return "Dime algo para reaccionar."
        mapping = {
            "hola": ["Hola!", "Hey!", "Buenas!"],
            "gracias": ["De nada!", "A ti!", "Un placer."],
            "ok": ["OK", "Perfecto", "Listo"],
            "bien": ["Genial", "Me alegro", "Excelente"],
            "mal": ["Animo", "Vamos a solucionarlo", "Lo siento"],
        }
        for key, options in mapping.items():
            if key in normalized:
                return random.choice(options)
        reactions = ["👍", "✅", "🤝", "✨", "😄", "🚀"]
        return random.choice(reactions)

    def wallpaper_suggestion(self, query: str | None = None) -> str:
        suggestions = [
            "Nebula Violet",
            "Cyber Grid",
            "Mountain Dawn",
            "Desert Dusk",
            "Ocean Lines",
            "City Rain",
        ]
        base = random.choice(suggestions)
        if query:
            return f"Sugerencia '{query}': {base}"
        return f"Sugerencia: {base}"

    def anilist_search(self, query: str) -> str:
        if not self.anilist_client:
            return "Anilist no configurado."
        result = self.anilist_client.search(query)
        if not result:
            return "No se encontro resultado en Anilist."
        title = result.get("title") or "Titulo desconocido"
        media_format = result.get("format") or "N/A"
        status = result.get("status") or "N/A"
        url = result.get("url") or ""
        if url:
            return f"{title} | {media_format} | {status}\n{url}"
        return f"{title} | {media_format} | {status}"

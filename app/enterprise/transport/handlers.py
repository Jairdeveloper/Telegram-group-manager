"""Enterprise command handlers (transport -> application)."""

from __future__ import annotations

from typing import Sequence

from app.config.settings import load_enterprise_settings
from app.enterprise.application.services import (
    EnterpriseContentService,
    EnterpriseModerationService,
    EnterpriseUtilityService,
    EnterpriseUserService,
)
from app.enterprise.domain.entities import EnterpriseAntiSpamConfig
from app.enterprise.infrastructure.content_repositories import (
    get_filters_repo,
    get_notes_repo,
    get_rules_repo,
    get_welcome_repo,
)
from app.enterprise.infrastructure.external.sibyl import SibylClient
from app.enterprise.infrastructure.external.spamwatch import SpamWatchClient
from app.enterprise.infrastructure.external.anilist import AnilistClient
from app.enterprise.infrastructure.moderation_repositories import (
    get_antichannel_repo,
    get_antispam_repo,
    get_blacklist_repo,
    get_sticker_blacklist_repo,
)
from app.enterprise.infrastructure.repositories import get_ban_repo, get_user_repo
from app.policies import PolicyEngine


_policy_engine = PolicyEngine()


def _build_spamwatch_client(settings) -> SpamWatchClient | None:
    if not settings.enterprise_spamwatch_url:
        return None
    return SpamWatchClient(
        base_url=settings.enterprise_spamwatch_url,
        token=settings.enterprise_spamwatch_token,
        timeout=settings.enterprise_spamwatch_timeout,
    )


def _build_sibyl_client(settings) -> SibylClient | None:
    if not settings.enterprise_sibyl_url:
        return None
    return SibylClient(
        base_url=settings.enterprise_sibyl_url,
        token=settings.enterprise_sibyl_token,
        timeout=settings.enterprise_sibyl_timeout,
    )


def _build_anilist_client(settings) -> AnilistClient | None:
    if not settings.enterprise_anilist_url:
        return None
    return AnilistClient(
        base_url=settings.enterprise_anilist_url,
        timeout=settings.enterprise_anilist_timeout,
    )


def _build_services() -> tuple[
    EnterpriseUserService,
    EnterpriseContentService,
    EnterpriseModerationService,
    EnterpriseUtilityService,
]:
    settings = load_enterprise_settings()
    user_service = EnterpriseUserService(
        user_repo=get_user_repo(),
        ban_repo=get_ban_repo(),
        policy_engine=_policy_engine,
        owner_ids=settings.owner_ids,
        sardegna_ids=settings.sardegna_ids,
        tenant_id=settings.default_tenant_id,
    )
    content_service = EnterpriseContentService(
        user_service=user_service,
        rules_repo=get_rules_repo(),
        welcome_repo=get_welcome_repo(),
        notes_repo=get_notes_repo(),
        filters_repo=get_filters_repo(),
        tenant_id=settings.default_tenant_id,
    )
    moderation_service = EnterpriseModerationService(
        user_service=user_service,
        antispam_repo=get_antispam_repo(),
        blacklist_repo=get_blacklist_repo(),
        sticker_blacklist_repo=get_sticker_blacklist_repo(),
        antichannel_repo=get_antichannel_repo(),
        spamwatch_client=_build_spamwatch_client(settings),
        sibyl_client=_build_sibyl_client(settings),
        tenant_id=settings.default_tenant_id,
    )
    utility_service = EnterpriseUtilityService(
        feature_flags={
            "fun": settings.enterprise_feature_fun,
            "reactions": settings.enterprise_feature_reactions,
            "anilist": settings.enterprise_feature_anilist,
            "wallpaper": settings.enterprise_feature_wallpaper,
            "gettime": settings.enterprise_feature_gettime,
        },
        default_timezone=settings.enterprise_default_timezone,
        anilist_client=_build_anilist_client(settings),
    )
    return user_service, content_service, moderation_service, utility_service


def _parse_user_id(raw: str) -> int:
    return int(raw.strip())


def _extract_media_info(update: dict | None) -> tuple[str, str | None]:
    """Return (content_type, file_id) for media messages."""
    if not update:
        return "text", None
    message = update.get("message") or update.get("edited_message") or {}
    if message.get("photo"):
        return "photo", message["photo"][-1]["file_id"]
    if message.get("document"):
        return "document", message["document"].get("file_id")
    if message.get("video"):
        return "video", message["video"].get("file_id")
    if message.get("sticker"):
        return "sticker", message["sticker"].get("file_id")
    return "text", None


def _extract_moderation_payload(update: dict | None, fallback_text: str = "") -> tuple[str, str | None, str | None]:
    """Return (text, sticker_file_id, sender_chat_type) for moderation checks."""
    if not update:
        return fallback_text or "", None, None
    message = update.get("message") or update.get("edited_message") or {}
    text = message.get("text") or message.get("caption") or fallback_text or ""
    sticker = message.get("sticker") or {}
    sticker_file_id = sticker.get("file_id")
    sender_chat = message.get("sender_chat") or {}
    sender_chat_type = sender_chat.get("type")
    return text, sticker_file_id, sender_chat_type


def handle_enterprise_command(
    *,
    actor_id: int | None,
    chat_id: int | None,
    command: str,
    args: Sequence[str],
    raw_text: str,
    raw_update: dict | None = None,
) -> dict:
    """Handle an EnterpriseRobot command and return response dict."""
    if actor_id is None:
        return {"status": "error", "response_text": "No se pudo identificar el usuario"}

    settings = load_enterprise_settings()
    if not settings.enterprise_enabled:
        return {"status": "disabled", "response_text": "Enterprise deshabilitado."}

    user_service, content_service, moderation_service, utility_service = _build_services()

    policy_result = user_service.evaluate_policy(actor_id, raw_text)
    if policy_result.status in ("denied", "throttled"):
        return {"status": policy_result.status, "response_text": policy_result.response_text}

    guardrail_error = user_service.guardrails_check(raw_text)
    if guardrail_error:
        return {"status": "blocked", "response_text": f"Guardrails: {guardrail_error}"}

    normalized = (command or "").strip().lower()
    args = tuple(args or ())

    if normalized in ("/adminhelp",):
        return {
            "status": "ok",
            "response_text": (
                "Comandos Enterprise:\n"
                "/user add <user_id> <role>\n"
                "/user role <user_id> <role>\n"
                "/user del <user_id>\n"
                "/user list\n"
                "/ban <user_id> [reason]\n"
                "/unban <user_id> [reason]\n"
                "/whoami\n"
                "/setrules <texto>\n"
                "/rules\n"
                "/setwelcome <texto>\n"
                "/welcome\n"
                "/setnote <nombre> <texto|media>\n"
                "/note <nombre>\n"
                "/notes\n"
                "/delnote <nombre>\n"
                "/filter add <patron> <respuesta>\n"
                "/filter del <patron>\n"
                "/filter list\n"
                "/antispam <on|off|status>\n"
                "/antispam spamwatch <on|off>\n"
                "/antispam sibyl <on|off>\n"
                "/blacklist add <patron>\n"
                "/blacklist del <patron>\n"
                "/blacklist list\n"
                "/stickerblacklist add <file_id>\n"
                "/stickerblacklist del <file_id>\n"
                "/stickerblacklist list\n"
                "/antichannel <on|off|status>\n"
                "/fun\n"
                "/reactions <texto>\n"
                "/anilist <titulo>\n"
                "/wallpaper [tema]\n"
                "/gettime [zona_horaria]"
            ),
        }

    if normalized == "/whoami":
        actor = user_service.ensure_actor(actor_id)
        return {
            "status": "ok",
            "response_text": f"Tu rol: {actor.role.value}",
        }

    if normalized in ("/user", "/users"):
        if not args:
            return {"status": "error", "response_text": "Uso: /user <add|role|del|list> ..."}

        action = args[0].lower()
        if action == "list":
            users = list(user_service.list_users())
            if not users:
                return {"status": "ok", "response_text": "Sin usuarios registrados."}
            lines = ["Usuarios:"]
            for user in users:
                lines.append(f"- {user.user_id}: {user.role.value}")
            return {"status": "ok", "response_text": "\n".join(lines)}

        if action in ("add", "role"):
            if len(args) < 3:
                return {"status": "error", "response_text": "Uso: /user add <user_id> <role>"}
            target_id = _parse_user_id(args[1])
            role_raw = args[2]
            try:
                user = user_service.upsert_user(actor_id, target_id, role_raw)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Usuario {user.user_id} -> {user.role.value}"}

        if action == "del":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /user del <user_id>"}
            target_id = _parse_user_id(args[1])
            try:
                user_service.delete_user(actor_id, target_id)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Usuario {target_id} eliminado"}

        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    if normalized == "/ban":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /ban <user_id> [reason]"}
        target_id = _parse_user_id(args[0])
        reason = " ".join(args[1:]).strip()
        try:
            record = user_service.ban_user(actor_id, target_id, reason)
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {
            "status": "ok",
            "response_text": f"Usuario {record.user_id} baneado. Reason: {record.reason}",
        }

    if normalized == "/unban":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /unban <user_id> [reason]"}
        target_id = _parse_user_id(args[0])
        reason = " ".join(args[1:]).strip()
        try:
            user_service.unban_user(actor_id, target_id, reason)
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {"status": "ok", "response_text": f"Usuario {target_id} desbaneado"}

    if chat_id is None:
        return {"status": "error", "response_text": "No se pudo identificar el chat"}

    if normalized == "/setrules":
        if not args:
            return {"status": "error", "response_text": "Uso: /setrules <texto>"}
        rules_text = " ".join(args).strip()
        try:
            content_service.set_rules(actor_id, chat_id, rules_text)
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {"status": "ok", "response_text": "Reglas actualizadas"}

    if normalized == "/rules":
        rules = content_service.get_rules(chat_id)
        if not rules:
            return {"status": "ok", "response_text": "No hay reglas configuradas."}
        return {"status": "ok", "response_text": rules.rules_text}

    if normalized == "/setwelcome":
        if not args:
            return {"status": "error", "response_text": "Uso: /setwelcome <texto>"}
        welcome_text = " ".join(args).strip()
        try:
            content_service.set_welcome(actor_id, chat_id, welcome_text)
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {"status": "ok", "response_text": "Welcome actualizado"}

    if normalized == "/welcome":
        welcome = content_service.get_welcome(chat_id)
        if not welcome:
            return {"status": "ok", "response_text": "No hay welcome configurado."}
        return {"status": "ok", "response_text": welcome.welcome_text}

    if normalized == "/setnote":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /setnote <nombre> <texto|media>"}
        note_key = args[0].strip().lower()
        content_text = " ".join(args[1:]).strip() if len(args) > 1 else None
        content_type, file_id = _extract_media_info(raw_update)
        try:
            content_service.set_note(
                actor_id,
                chat_id,
                note_key,
                content_text,
                content_type=content_type,
                file_id=file_id,
            )
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {"status": "ok", "response_text": f"Nota {note_key} guardada"}

    if normalized == "/note":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /note <nombre>"}
        note_key = args[0].strip().lower()
        note = content_service.get_note(chat_id, note_key)
        if not note:
            return {"status": "ok", "response_text": "Nota no encontrada."}
        if note.content_type != "text":
            return {"status": "ok", "response_text": f"Nota {note_key} (media: {note.content_type})"}
        return {"status": "ok", "response_text": note.content_text or ""}

    if normalized == "/notes":
        notes = list(content_service.list_notes(chat_id))
        if not notes:
            return {"status": "ok", "response_text": "Sin notas."}
        names = ", ".join(sorted({n.note_key for n in notes}))
        return {"status": "ok", "response_text": f"Notas: {names}"}

    if normalized == "/delnote":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /delnote <nombre>"}
        note_key = args[0].strip().lower()
        try:
            content_service.delete_note(actor_id, chat_id, note_key)
        except PermissionError as exc:
            return {"status": "unauthorized", "response_text": str(exc)}
        return {"status": "ok", "response_text": f"Nota {note_key} eliminada"}

    if normalized == "/filter":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /filter <add|del|list> ..."}
        action = args[0].lower()
        if action == "list":
            items = list(content_service.list_filters(chat_id))
            if not items:
                return {"status": "ok", "response_text": "Sin filtros."}
            lines = ["Filtros:"]
            for item in items:
                lines.append(f"- {item.pattern} -> {item.response_text}")
            return {"status": "ok", "response_text": "\n".join(lines)}
        if action == "add":
            if len(args) < 3:
                return {"status": "error", "response_text": "Uso: /filter add <patron> <respuesta>"}
            pattern = args[1]
            response_text = " ".join(args[2:]).strip()
            try:
                content_service.add_filter(actor_id, chat_id, pattern, response_text)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Filtro agregado: {pattern}"}
        if action == "del":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /filter del <patron>"}
            pattern = args[1]
            try:
                content_service.delete_filter(actor_id, chat_id, pattern)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Filtro eliminado: {pattern}"}
        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    if normalized == "/fun":
        if not utility_service.is_enabled("fun"):
            return {"status": "disabled", "response_text": "Modulo fun deshabilitado."}
        return {"status": "ok", "response_text": utility_service.random_fun()}

    if normalized == "/reactions":
        if not utility_service.is_enabled("reactions"):
            return {"status": "disabled", "response_text": "Modulo reactions deshabilitado."}
        if not args:
            return {"status": "error", "response_text": "Uso: /reactions <texto>"}
        text = " ".join(args).strip()
        return {"status": "ok", "response_text": utility_service.reaction_for_text(text)}

    if normalized == "/anilist":
        if not utility_service.is_enabled("anilist"):
            return {"status": "disabled", "response_text": "Modulo anilist deshabilitado."}
        if not args:
            return {"status": "error", "response_text": "Uso: /anilist <titulo>"}
        query = " ".join(args).strip()
        return {"status": "ok", "response_text": utility_service.anilist_search(query)}

    if normalized == "/wallpaper":
        if not utility_service.is_enabled("wallpaper"):
            return {"status": "disabled", "response_text": "Modulo wallpaper deshabilitado."}
        query = " ".join(args).strip() if args else None
        return {"status": "ok", "response_text": utility_service.wallpaper_suggestion(query)}

    if normalized == "/gettime":
        if not utility_service.is_enabled("gettime"):
            return {"status": "disabled", "response_text": "Modulo gettime deshabilitado."}
        tz_name = args[0].strip() if args else None
        return {"status": "ok", "response_text": utility_service.get_time(tz_name)}

    if normalized == "/antispam":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /antispam <on|off|status|spamwatch|sibyl> [on|off]"}
        action = args[0].lower()
        current = moderation_service.get_antispam(chat_id)
        if not current:
            current = EnterpriseAntiSpamConfig(
                tenant_id=user_service.tenant_id,
                chat_id=chat_id,
                enabled=False,
                spamwatch_enabled=False,
                sibyl_enabled=False,
            )
        enabled = current.enabled
        spamwatch_enabled = current.spamwatch_enabled
        sibyl_enabled = current.sibyl_enabled

        if action in ("on", "off"):
            enabled = action == "on"
            try:
                moderation_service.set_antispam(
                    actor_id,
                    chat_id,
                    enabled=enabled,
                    spamwatch_enabled=spamwatch_enabled,
                    sibyl_enabled=sibyl_enabled,
                )
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Antispam {'activado' if enabled else 'desactivado'}"}

        if action == "status":
            status_text = "on" if enabled else "off"
            sw_text = "on" if spamwatch_enabled else "off"
            sibyl_text = "on" if sibyl_enabled else "off"
            return {
                "status": "ok",
                "response_text": f"Antispam: {status_text} | SpamWatch: {sw_text} | Sibyl: {sibyl_text}",
            }

        if action in ("spamwatch", "sibyl"):
            if len(args) < 2:
                return {"status": "error", "response_text": f"Uso: /antispam {action} <on|off>"}
            toggle = args[1].lower()
            if toggle not in ("on", "off"):
                return {"status": "error", "response_text": f"Uso: /antispam {action} <on|off>"}
            if action == "spamwatch":
                spamwatch_enabled = toggle == "on"
            else:
                sibyl_enabled = toggle == "on"
            try:
                moderation_service.set_antispam(
                    actor_id,
                    chat_id,
                    enabled=enabled,
                    spamwatch_enabled=spamwatch_enabled,
                    sibyl_enabled=sibyl_enabled,
                )
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Antispam {action} {'activado' if toggle == 'on' else 'desactivado'}"}

        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    if normalized == "/blacklist":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /blacklist <add|del|list> ..."}
        action = args[0].lower()
        if action == "list":
            items = list(moderation_service.list_blacklist(chat_id))
            if not items:
                return {"status": "ok", "response_text": "Blacklist vacia."}
            lines = ["Blacklist:"]
            for item in items:
                lines.append(f"- {item.pattern}")
            return {"status": "ok", "response_text": "\n".join(lines)}
        if action == "add":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /blacklist add <patron>"}
            pattern = args[1]
            try:
                moderation_service.add_blacklist(actor_id, chat_id, pattern)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            except ValueError as exc:
                return {"status": "error", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Blacklist agregado: {pattern}"}
        if action == "del":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /blacklist del <patron>"}
            pattern = args[1]
            try:
                moderation_service.delete_blacklist(actor_id, chat_id, pattern)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Blacklist eliminado: {pattern}"}
        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    if normalized == "/stickerblacklist":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /stickerblacklist <add|del|list> ..."}
        action = args[0].lower()
        if action == "list":
            items = list(moderation_service.list_sticker_blacklist(chat_id))
            if not items:
                return {"status": "ok", "response_text": "Sticker blacklist vacia."}
            lines = ["Sticker blacklist:"]
            for item in items:
                lines.append(f"- {item.sticker_file_id}")
            return {"status": "ok", "response_text": "\n".join(lines)}
        if action == "add":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /stickerblacklist add <file_id>"}
            sticker_file_id = args[1]
            try:
                moderation_service.add_sticker_blacklist(actor_id, chat_id, sticker_file_id)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": "Sticker agregado a blacklist."}
        if action == "del":
            if len(args) < 2:
                return {"status": "error", "response_text": "Uso: /stickerblacklist del <file_id>"}
            sticker_file_id = args[1]
            try:
                moderation_service.delete_sticker_blacklist(actor_id, chat_id, sticker_file_id)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": "Sticker eliminado de blacklist."}
        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    if normalized == "/antichannel":
        if len(args) < 1:
            return {"status": "error", "response_text": "Uso: /antichannel <on|off|status>"}
        action = args[0].lower()
        if action in ("on", "off"):
            enabled = action == "on"
            try:
                moderation_service.set_antichannel(actor_id, chat_id, enabled=enabled)
            except PermissionError as exc:
                return {"status": "unauthorized", "response_text": str(exc)}
            return {"status": "ok", "response_text": f"Antichannel {'activado' if enabled else 'desactivado'}"}
        if action == "status":
            config = moderation_service.get_antichannel(chat_id)
            status_text = "on" if config and config.enabled else "off"
            return {"status": "ok", "response_text": f"Antichannel: {status_text}"}
        return {"status": "error", "response_text": f"Accion no soportada: {action}"}

    return {"status": "unsupported", "response_text": f"Unsupported command: {normalized}"}


def handle_enterprise_moderation(
    *,
    actor_id: int | None,
    chat_id: int | None,
    raw_text: str,
    raw_update: dict | None = None,
) -> dict:
    """Evaluate non-command messages against Enterprise moderation rules."""
    if actor_id is None or chat_id is None:
        return {"status": "ok"}

    settings = load_enterprise_settings()
    if not settings.enterprise_enabled or not settings.enterprise_moderation_enabled:
        return {"status": "ok"}

    user_service, _content_service, moderation_service, _utility_service = _build_services()
    text, sticker_file_id, sender_chat_type = _extract_moderation_payload(raw_update, raw_text)
    decision = moderation_service.evaluate_message(
        actor_id=actor_id,
        chat_id=chat_id,
        text=text,
        sticker_file_id=sticker_file_id,
        sender_chat_type=sender_chat_type,
    )
    return {
        "status": decision.status,
        "response_text": decision.response_text,
        "reason": decision.reason,
        "source": decision.source,
    }

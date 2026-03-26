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
                "/config - Menú de configuración\n"
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

    if normalized == "/config":
        return {"status": "menu", "menu_id": "main"}

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

    if normalized == "/report":
        return _handle_report_command(actor_id, chat_id, args, raw_update)

    if normalized == "/reports":
        return _handle_reports_command(actor_id, chat_id, args, raw_update)

    return {"status": "unsupported", "response_text": f"Unsupported command: {normalized}"}


def _handle_report_command(
    actor_id: int,
    chat_id: int,
    args: tuple,
    raw_update: dict | None,
) -> dict:
    """Handle /report command - report a user for inappropriate behavior."""
    from app.manager_bot._features.reports import ReportAction, ReportsFeature

    message = raw_update.get("message") or raw_update.get("edited_message") or {} if raw_update else {}

    reported_id = None
    reason = None
    message_id = None

    if args and len(args) >= 1:
        first_arg = args[0].strip()
        if first_arg.isdigit():
            reported_id = int(first_arg)
            reason = " ".join(args[1:]).strip() if len(args) > 1 else "Sin razón"
        else:
            reason = " ".join(args).strip()

    if not reported_id and message.get("reply_to_message"):
        reply_msg = message.get("reply_to_message")
        if reply_msg:
            user = reply_msg.get("from")
            if user:
                reported_id = user.get("id")
                message_id = reply_msg.get("message_id")
                if not reason:
                    reason = " ".join(args).strip() if args else "Reporte sin razón"

    if not reported_id:
        return {
            "status": "error",
            "response_text": "Uso: /report <user_id> <razón>\nO responde a un mensaje con /report <razón>",
        }

    if not reason:
        reason = "Sin razón especificada"

    if reported_id == actor_id:
        return {"status": "error", "response_text": "No puedes reportarte a ti mismo"}

    from app.manager_bot._config.storage import get_config_storage
    from app.manager_bot._features.reports.repository import ReportRepository
    from app.config.settings import load_api_settings

    config_storage = get_config_storage()
    settings = load_api_settings()
    repository = None

    if settings.database_url:
        try:
            repository = ReportRepository(settings.database_url)
        except Exception:
            pass

    reports_feature = ReportsFeature(config_storage, repository)
    report = reports_feature.create_report(
        chat_id=chat_id,
        reporter_id=actor_id,
        reported_id=reported_id,
        reason=reason,
        message_id=message_id,
    )

    return {
        "status": "ok",
        "response_text": f"Reporte creado ID: {report.report_id[:8]}...\nEl equipo de administración será notificado.",
    }


def _handle_reports_command(
    actor_id: int,
    chat_id: int,
    args: tuple,
    raw_update: dict | None,
) -> dict:
    """Handle /reports command - list reports or show reports menu."""
    from app.manager_bot._features.reports import ReportStatus, ReportsFeature
    from app.manager_bot._config.storage import get_config_storage
    from app.manager_bot._features.reports.repository import ReportRepository
    from app.config.settings import load_api_settings

    config_storage = get_config_storage()
    settings = load_api_settings()
    repository = None

    if settings.database_url:
        try:
            repository = ReportRepository(settings.database_url)
        except Exception:
            pass

    reports_feature = ReportsFeature(config_storage, repository)

    if not args:
        return {"status": "menu", "menu_id": "reports"}

    subcmd = args[0].lower()

    if subcmd == "abiertos":
        reports = reports_feature.get_reports(chat_id, ReportStatus.OPEN)
        if not reports:
            return {"status": "ok", "response_text": "No hay reportes abiertos."}

        lines = ["📋 Reportes abiertos:"]
        for r in reports[:10]:
            lines.append(f"• ID: {r.report_id[:8]} | Usuario: {r.reported_id} | Razón: {r.reason[:30]}")
        return {"status": "ok", "response_text": "\n".join(lines)}

    if subcmd == "resueltos":
        reports = reports_feature.get_reports(chat_id, ReportStatus.RESOLVED)
        if not reports:
            return {"status": "ok", "response_text": "No hay reportes resueltos."}

        lines = ["✅ Reportes resueltos:"]
        for r in reports[:10]:
            action = r.action.value if r.action else "N/A"
            lines.append(f"• ID: {r.report_id[:8]} | Acción: {action} | Razón: {r.reason[:30]}")
        return {"status": "ok", "response_text": "\n".join(lines)}

    if subcmd in ("stats", "estadisticas"):
        stats = reports_feature.get_stats(chat_id)
        return {
            "status": "ok",
            "response_text": (
                f"📊 Estadísticas de Reportes:\n"
                f"• Total: {stats.total}\n"
                f"• Abiertos: {stats.open}\n"
                f"• Resueltos: {stats.resolved}\n"
                f"• Descartados: {stats.dismissed}"
            ),
        }

    if subcmd in ("export", "exportar"):
        return _handle_reports_export(actor_id, chat_id, args[1:] if len(args) > 1 else ())

    if subcmd in ("top", "mas_reportados"):
        if not repository:
            return {"status": "error", "response_text": "Base de datos no configurada"}
        top_users = repository.get_top_reported_users(chat_id)
        if not top_users:
            return {"status": "ok", "response_text": "No hay usuarios reportados."}
        lines = ["👤 Usuarios más reportados:"]
        for u in top_users:
            lines.append(f"• User ID: {u['user_id']} - {u['count']} reportes")
        return {"status": "ok", "response_text": "\n".join(lines)}

    return {
        "status": "error",
        "response_text": "Uso: /reports [abiertos|resueltos|stats|export|top]",
    }


def _handle_reports_export(
    actor_id: int,
    chat_id: int,
    args: tuple,
) -> dict:
    """Handle /reports export command."""
    from app.manager_bot._features.reports.repository import ReportRepository
    from app.config.settings import load_api_settings

    settings = load_api_settings()
    if not settings.database_url:
        return {"status": "error", "response_text": "Base de datos no configurada"}

    try:
        repository = ReportRepository(settings.database_url)
    except Exception as e:
        return {"status": "error", "response_text": f"Error: {str(e)}"}

    export_format = args[0].lower() if args else "json"

    if export_format == "csv":
        csv_data = repository.export_to_csv(chat_id)
        return {
            "status": "file",
            "content": csv_data,
            "filename": f"reports_{chat_id}.csv",
            "content_type": "text/csv",
        }
    else:
        json_data = repository.export_to_json(chat_id)
        return {
            "status": "file",
            "content": json_data,
            "filename": f"reports_{chat_id}.json",
            "content_type": "application/json",
        }


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

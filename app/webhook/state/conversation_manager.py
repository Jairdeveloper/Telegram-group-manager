"""Conversation state management for webhook processor."""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from app.manager_bot._config.storage import get_config_storage
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menu_service import get_conversation_state
from app.manager_bot._utils.duration_parser import parse_duration_to_seconds


logger = logging.getLogger(__name__)


@dataclass
class ProcessorResult:
    """Result from processing a conversation state."""
    reply: Optional[str] = None
    menu_to_show: Optional[str] = None
    error: Optional[str] = None


async def handle_welcome_text(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_welcome_text state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.welcome_text = text
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(
        reply=f"Mensaje de bienvenida guardado:\n\n{text}",
        menu_to_show="welcome_customize",
    )


async def handle_welcome_media(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_welcome_media state."""
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    message = dispatch.raw_update.get("message") or dispatch.raw_update.get("edited_message") or {}
    file_id = None
    if message.get("photo"):
        file_id = message["photo"][-1].get("file_id")
    elif message.get("video"):
        file_id = message["video"].get("file_id")
    elif message.get("document"):
        file_id = message["document"].get("file_id")
    elif message.get("animation"):
        file_id = message["animation"].get("file_id")
    elif message.get("sticker"):
        file_id = message["sticker"].get("file_id")

    if not file_id:
        return ProcessorResult(reply="Envia una foto o video para configurar la bienvenida.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.welcome_media = file_id
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(
        reply="Multimedia de bienvenida guardada.",
        menu_to_show="welcome_customize",
    )


async def handle_goodbye_text(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_goodbye_text state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.goodbye_text = text
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply=f"Mensaje de despedida guardado:\n\n{text}")


async def handle_antiflood_warn_duration(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_antiflood_warn_duration state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show="antiflood")

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.antiflood_warn_duration_sec = seconds
    config.antiflood_action = "warn"
    config.antiflood_enabled = True
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion de advertencia guardada.", menu_to_show="antiflood")


async def handle_antiflood_ban_duration(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_antiflood_ban_duration state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show="antiflood")

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.antiflood_ban_duration_sec = seconds
    config.antiflood_action = "ban"
    config.antiflood_enabled = True
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion de ban guardada.", menu_to_show="antiflood")


async def handle_antiflood_mute_duration(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_antiflood_mute_duration state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show="antiflood")

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.antiflood_mute_duration_sec = seconds
    config.antiflood_action = "mute"
    config.antiflood_enabled = True
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion de silenciar guardada.", menu_to_show="antiflood")


async def handle_antispan_duration(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_antispan_*_duration states."""
    text = dispatch.text
    state_name = state.get("state", "")
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        scope = state_name.replace("waiting_antispan_", "").split("_")[0]
        menu_to_show = f"antispan:{scope}" if scope else "antispan"
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show=menu_to_show)

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")

    suffix = state_name.replace("waiting_antispan_", "")
    if suffix.endswith("_mute_duration"):
        scope = suffix[:-len("_mute_duration")]
        kind = "mute"
    else:
        scope = suffix[:-len("_ban_duration")]
        kind = "ban"

    if scope == "telegram":
        if kind == "mute":
            config.antispan_telegram_mute_duration_sec = seconds
            config.antispan_telegram_action = "mute"
        else:
            config.antispan_telegram_ban_duration_sec = seconds
            config.antispan_telegram_action = "ban"
    elif scope == "forward":
        if kind == "mute":
            config.antispan_forward_mute_duration_sec = seconds
        else:
            config.antispan_forward_ban_duration_sec = seconds
    elif scope == "quotes":
        if kind == "mute":
            config.antispan_quotes_mute_duration_sec = seconds
        else:
            config.antispan_quotes_ban_duration_sec = seconds
    elif scope == "internet":
        if kind == "mute":
            config.antispan_internet_mute_duration_sec = seconds
            config.antispan_internet_action = "mute"
        else:
            config.antispan_internet_ban_duration_sec = seconds
            config.antispan_internet_action = "ban"

    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion guardada.", menu_to_show=f"antispan:{scope}")


async def handle_antispan_exceptions(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_antispan_*_exceptions_add/remove states."""
    text = dispatch.text
    state_name = state.get("state", "")
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        scope = state_name.replace("waiting_antispan_", "").split("_")[0]
        menu_to_show = f"antispan:{scope}" if scope else "antispan"
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show=menu_to_show)

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")

    suffix = state_name.replace("waiting_antispan_", "")
    if suffix.endswith("_exceptions_add"):
        scope = suffix[:-len("_exceptions_add")]
        mode = "add"
    else:
        scope = suffix[:-len("_exceptions_remove")]
        mode = "remove"

    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return ProcessorResult(reply="No se encontraron enlaces o usernames.")

    if scope == "telegram":
        entries = list(config.antispan_telegram_exceptions)
    elif scope == "forward":
        entries = list(config.antispan_forward_exceptions)
    elif scope == "quotes":
        entries = list(config.antispan_quotes_exceptions)
    elif scope == "internet":
        entries = list(config.antispan_internet_exceptions)
    else:
        entries = []

    if mode == "add":
        for line in lines:
            if line not in entries:
                entries.append(line)
        reply = "Excepciones agregadas."
    else:
        for line in lines:
            if line in entries:
                entries.remove(line)
        reply = "Excepciones eliminadas."

    if scope == "telegram":
        config.antispan_telegram_exceptions = entries
    elif scope == "forward":
        config.antispan_forward_exceptions = entries
    elif scope == "quotes":
        config.antispan_quotes_exceptions = entries
    elif scope == "internet":
        config.antispan_internet_exceptions = entries

    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply=reply, menu_to_show=f"antispan:{scope}")


async def handle_multimedia_duration_mute(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_multimedia_duration_mute state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show="multimedia:duration")

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.multimedia_mute_duration_sec = seconds
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion de silenciar para multimedia guardada.", menu_to_show="multimedia:duration")


async def handle_multimedia_duration_ban(
    state: Dict[str, Any],
    dispatch: Any,
    user_id: int,
    chat_id: int,
) -> Optional[ProcessorResult]:
    """Handle waiting_multimedia_duration_ban state."""
    text = dispatch.text
    config_storage = get_config_storage()
    conversation = get_conversation_state()

    if (text or "").strip().lower() in ("cancel", "/cancel", "cancelar"):
        conversation.clear_state(user_id, chat_id)
        return ProcessorResult(reply="Operacion cancelada.", menu_to_show="multimedia:duration")

    seconds = parse_duration_to_seconds(text or "")
    if not seconds or seconds < 30 or seconds > 365 * 24 * 60 * 60:
        return ProcessorResult(reply="Duracion invalida. Minimo 30 segundos, maximo 365 dias.")

    config = await config_storage.get(chat_id)
    if not config:
        config = GroupConfig.create_default(chat_id, "default")
    config.multimedia_ban_duration_sec = seconds
    config.update_timestamp(user_id)
    await config_storage.set(config)
    conversation.clear_state(user_id, chat_id)

    return ProcessorResult(reply="Duracion de ban para multimedia guardada.", menu_to_show="multimedia:duration")


class ConversationStateManager:
    """Manager for conversation state handling."""

    STATE_HANDLERS: Dict[str, Callable] = {
        "waiting_welcome_text": handle_welcome_text,
        "waiting_welcome_media": handle_welcome_media,
        "waiting_goodbye_text": handle_goodbye_text,
        "waiting_antiflood_warn_duration": handle_antiflood_warn_duration,
        "waiting_antiflood_ban_duration": handle_antiflood_ban_duration,
        "waiting_antiflood_mute_duration": handle_antiflood_mute_duration,
        "waiting_multimedia_duration_mute": handle_multimedia_duration_mute,
        "waiting_multimedia_duration_ban": handle_multimedia_duration_ban,
    }

    def __init__(self):
        self._handlers = dict(self.STATE_HANDLERS)

    def register_handler(
        self,
        state_name: str,
        handler: Callable,
    ) -> None:
        """Register a custom handler for a state."""
        self._handlers[state_name] = handler

    async def process(
        self,
        state: Dict[str, Any],
        dispatch: Any,
        user_id: int,
        chat_id: int,
    ) -> Optional[ProcessorResult]:
        """Process a state and return the result."""
        if not state:
            return None

        state_name = state.get("state")
        if not state_name:
            return None

        if state_name.startswith("waiting_antispan_"):
            if state_name.endswith("_mute_duration") or state_name.endswith("_ban_duration"):
                return await handle_antispan_duration(state, dispatch, user_id, chat_id)
            if state_name.endswith("_exceptions_add") or state_name.endswith("_exceptions_remove"):
                return await handle_antispan_exceptions(state, dispatch, user_id, chat_id)

        handler = self._handlers.get(state_name)
        if handler:
            return await handler(state, dispatch, user_id, chat_id)

        return None

    def get_available_states(self) -> list[str]:
        """Get list of available states."""
        return list(self._handlers.keys())


_conversation_state_manager = None


def get_conversation_state_manager() -> ConversationStateManager:
    """Get or create ConversationStateManager singleton."""
    global _conversation_state_manager
    if _conversation_state_manager is None:
        _conversation_state_manager = ConversationStateManager()
    return _conversation_state_manager

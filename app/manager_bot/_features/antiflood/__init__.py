"""AntiFlood feature module."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class AntiFloodFeature(FeatureModule):
    """Feature module for anti-flood protection."""

    MENU_ID = "antiflood"
    FEATURE_NAME = "AntiFlood"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for anti-flood."""

        async def _show_menu(callback: "CallbackQuery", bot: "Bot", menu_factory):
            from app.manager_bot._menus.antiflood_menu import (
                create_antiflood_menu,
            )

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = menu_factory(config) if menu_factory else create_antiflood_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.antiflood_enabled = enabled
            if not enabled:
                config.antiflood_action = "off"
            elif config.antiflood_action == "off":
                config.antiflood_action = "warn"
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Anti-Flood {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_action(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            action = parts[-1]

            valid_actions = {"off", "warn", "kick", "mute", "ban"}
            if action not in valid_actions:
                await callback.answer("Accion invalida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.antiflood_action = action
            config.antiflood_enabled = action != "off"
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer("Castigo actualizado", show_alert=True)

            from app.manager_bot._menus.antiflood_menu import create_antiflood_menu
            await _show_menu(callback, bot, create_antiflood_menu)

        async def handle_delete_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.antiflood_delete_messages = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer("Borrar mensajes actualizado", show_alert=True)

            from app.manager_bot._menus.antiflood_menu import create_antiflood_menu
            await _show_menu(callback, bot, create_antiflood_menu)

        async def handle_limit(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            limit = int(parts[-1])

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.antiflood_limit = limit
            config.antiflood_enabled = True
            if config.antiflood_action == "off":
                config.antiflood_action = "warn"
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Límite configurado: {limit} mensajes",
                show_alert=True
            )

        async def handle_interval(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            interval = int(parts[-1])

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.antiflood_interval = interval
            config.antiflood_enabled = True
            if config.antiflood_action == "off":
                config.antiflood_action = "warn"
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Intervalo configurado: {interval} segundos",
                show_alert=True
            )

        async def handle_show_main(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antiflood_menu import create_antiflood_menu
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            conversation = get_conversation_state()
            state = conversation.get_state(callback.from_user.id, chat_id)
            if state and state.get("state", "").startswith("waiting_antiflood_"):
                conversation.clear_state(callback.from_user.id, chat_id)
            await _show_menu(callback, bot, create_antiflood_menu)

        async def handle_show_limit(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antiflood_menu import create_antiflood_limit_menu
            await _show_menu(callback, bot, create_antiflood_limit_menu)

        async def handle_show_interval(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antiflood_menu import create_antiflood_interval_menu
            await _show_menu(callback, bot, create_antiflood_interval_menu)

        async def handle_show_warn_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antiflood_menu import create_antiflood_warn_duration_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    "waiting_antiflood_warn_duration",
                )
            await _show_menu(callback, bot, create_antiflood_warn_duration_menu)

        async def handle_show_ban_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antiflood_menu import create_antiflood_ban_duration_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    "waiting_antiflood_ban_duration",
                )
            await _show_menu(callback, bot, create_antiflood_ban_duration_menu)

        async def handle_show_mute_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antiflood_menu import create_antiflood_mute_duration_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    "waiting_antiflood_mute_duration",
                )
            await _show_menu(callback, bot, create_antiflood_mute_duration_menu)

        async def handle_clear_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            target = parts[-1] if parts else ""

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            if target == "warn":
                config.antiflood_warn_duration_sec = None
            elif target == "ban":
                config.antiflood_ban_duration_sec = None
            elif target == "mute":
                config.antiflood_mute_duration_sec = None

            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer("Duracion eliminada", show_alert=True)

            from app.manager_bot._menus.antiflood_menu import create_antiflood_menu
            await _show_menu(callback, bot, create_antiflood_menu)

        router.register_callback("mod:antiflood:toggle", handle_toggle)
        router.register_callback("mod:antiflood:limit", handle_limit)
        router.register_callback("mod:antiflood:interval", handle_interval)
        router.register_exact("mod:antiflood:show", handle_show_main)
        router.register_exact("mod:antiflood:limit:show", handle_show_limit)
        router.register_exact("mod:antiflood:interval:show", handle_show_interval)
        router.register_exact("mod:antiflood:warn:duration:show", handle_show_warn_duration)
        router.register_exact("mod:antiflood:ban:duration:show", handle_show_ban_duration)
        router.register_exact("mod:antiflood:mute:duration:show", handle_show_mute_duration)
        router.register_callback("mod:antiflood:action", handle_action)
        router.register_callback("mod:antiflood:delete:toggle", handle_delete_toggle)
        router.register_callback("mod:antiflood:duration:clear", handle_clear_duration)

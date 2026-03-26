"""Multimedia feature module."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class MultimediaFeature(FeatureModule):
    """Feature module for multimedia content moderation."""

    MENU_ID = "multimedia"
    FEATURE_NAME = "Multimedia"

    MULTIMEDIA_ACTIONS = [
        "story", "photo", "video", "album", "gif", "voice", "audio",
        "sticker", "animated_sticker", "game_sticker", "animated_emoji",
        "custom_emoji", "file", "game", "contact", "poll", "checklist",
        "location", "caps", "payment", "inline_bot", "spoiler",
        "spoiler_media", "video_note", "giveaway",
    ]

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for multimedia."""

        async def _show_menu(callback: "CallbackQuery", bot: "Bot", menu_factory):
            from app.manager_bot._menus.multimedia_menu import (
                create_multimedia_menu,
                create_multimedia_page2_menu,
                create_multimedia_duration_menu,
                create_multimedia_mute_duration_menu,
                create_multimedia_ban_duration_menu,
            )

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = menu_factory(config) if menu_factory else create_multimedia_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_action(callback: "CallbackQuery", bot: "Bot", data: str):
            # Formato: multimedia:story:action:warn
            parts = data.split(":")
            
            if len(parts) < 4:
                await callback.answer("Accion no reconocida", show_alert=True)
                return
            
            tipo = parts[1]  # "story"
            action = parts[3]  # "warn"
            
            valid_actions = {"off", "warn", "mute", "delete", "kick", "ban"}
            if action not in valid_actions:
                await callback.answer("Accion no reconocida", show_alert=True)
                return
            
            if tipo not in self.MULTIMEDIA_ACTIONS:
                await callback.answer("Tipo no reconocido", show_alert=True)
                return
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return
            
            config_field = f"multimedia_{tipo}_action"

            def _apply(cfg: GroupConfig) -> None:
                setattr(cfg, config_field, action)

            await self.update_config_and_refresh(callback, bot, "multimedia", _apply)

        async def handle_show_main(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.multimedia_menu import create_multimedia_menu
            await _show_menu(callback, bot, create_multimedia_menu)

        async def handle_show_page2(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.multimedia_menu import create_multimedia_page2_menu
            await _show_menu(callback, bot, create_multimedia_page2_menu)

        async def handle_show_page1(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.multimedia_menu import create_multimedia_menu
            await _show_menu(callback, bot, create_multimedia_menu)

        async def handle_show_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.multimedia_menu import create_multimedia_duration_menu
            await _show_menu(callback, bot, create_multimedia_duration_menu)

        async def handle_show_mute_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.multimedia_menu import create_multimedia_mute_duration_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    "waiting_multimedia_duration_mute",
                )
            await _show_menu(callback, bot, create_multimedia_mute_duration_menu)

        async def handle_show_ban_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.multimedia_menu import create_multimedia_ban_duration_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    "waiting_multimedia_duration_ban",
                )
            await _show_menu(callback, bot, create_multimedia_ban_duration_menu)

        async def handle_clear_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            target = parts[-1] if parts else ""

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                if target == "mute":
                    cfg.multimedia_mute_duration_sec = None
                elif target == "ban":
                    cfg.multimedia_ban_duration_sec = None
                else:
                    cfg.multimedia_mute_duration_sec = None
                    cfg.multimedia_ban_duration_sec = None

            menu_id = "multimedia:duration"
            await self.update_config_and_refresh(callback, bot, menu_id, _apply)

        router.register_exact("multimedia:show", handle_show_main)
        router.register_exact("multimedia:page2:show", handle_show_page2)
        router.register_exact("multimedia:page1:show", handle_show_page1)
        router.register_exact("multimedia:duration:show", handle_show_duration)
        router.register_exact("multimedia:duration:mute:show", handle_show_mute_duration)
        router.register_exact("multimedia:duration:ban:show", handle_show_ban_duration)
        router.register_callback("multimedia:duration:clear", handle_clear_duration)

        for media_type in self.MULTIMEDIA_ACTIONS:
            router.register_callback(f"multimedia:{media_type}", handle_action)

"""Filters feature module."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class FiltersFeature(FeatureModule):
    """Feature module for content filters."""

    MENU_ID = "filters"
    FEATURE_NAME = "Filters"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for filters."""

        async def handle_add_filter(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer("Usa /filter add <patron> <respuesta> para agregar un filtro")

        async def handle_del_filter(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 3:
                pattern = parts[2]
            else:
                await callback.answer("Patron no especificado", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            original_count = len(config.filters)
            new_filters = [f for f in config.filters if f.get("pattern") != pattern]
            if len(new_filters) == original_count:
                await callback.answer(f"Filtro '{pattern}' no encontrado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.filters = new_filters

            await self.update_config_and_refresh(callback, bot, "filters:list", _apply)

        async def handle_add_word(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer("Usa /blacklist add <palabra> para bloquear una palabra")

        async def handle_del_word(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 4:
                word = parts[3]
            else:
                await callback.answer("Palabra no especificada", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            if word not in config.blocked_words:
                await callback.answer(f"Palabra '{word}' no encontrada", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                if word in cfg.blocked_words:
                    cfg.blocked_words.remove(word)

            await self.update_config_and_refresh(callback, bot, "filters:words", _apply)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filters_menu import create_filters_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filters_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_words(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filters_menu import create_blocked_words_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_blocked_words_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_sticker(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filters_menu import create_sticker_blacklist_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_sticker_blacklist_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_list(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filters_menu import create_filters_list_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filters_list_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_exact("filters:add", handle_add_filter)
        router.register_callback("filters:del", handle_del_filter)
        router.register_exact("filters:words:show", handle_show_words)
        router.register_callback("filters:words:del", handle_del_word)
        router.register_callback("filters:words:add", handle_add_word)
        router.register_exact("filters:sticker:show", handle_show_sticker)
        router.register_callback("filters:sticker:add", handle_add_filter)
        router.register_exact("filters:list", handle_show_list)
        router.register_exact("filters:show", handle_show_menu)

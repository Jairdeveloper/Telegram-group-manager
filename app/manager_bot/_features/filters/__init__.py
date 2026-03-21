"""Filters feature module for contenido filters."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class FiltroContenidoFeature(FeatureModule):
    """Feature module for contenido filters."""

    MENU_ID = "filtro_contenido"
    FEATURE_NAME = "Filtros de Contenido"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for filtro contenido."""

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

            await self.update_config_and_refresh(callback, bot, "filtro_contenido:list", _apply)

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

            await self.update_config_and_refresh(callback, bot, "filtro_contenido:words", _apply)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_contenido_menu import create_filtro_contenido_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filtro_contenido_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_words(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_contenido_menu import create_filtro_contenido_words_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filtro_contenido_words_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_sticker(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_contenido_menu import create_filtro_contenido_sticker_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filtro_contenido_sticker_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_list(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_contenido_menu import create_filtro_contenido_list_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filtro_contenido_list_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_exact("filtro_contenido:show", handle_show_menu)
        router.register_exact("filtro_contenido:add", handle_add_filter)
        router.register_callback("filtro_contenido:del", handle_del_filter)
        router.register_exact("filtro_contenido:list", handle_show_list)
        router.register_exact("filtro_contenido:words:show", handle_show_words)
        router.register_callback("filtro_contenido:words:del", handle_del_word)
        router.register_callback("filtro_contenido:words:add", handle_add_word)
        router.register_exact("filtro_contenido:sticker:show", handle_show_sticker)
        router.register_callback("filtro_contenido:sticker:add", handle_add_filter)
        router.register_exact("filtro_contenido:sticker:list", handle_show_sticker)


_filtro_contenido_feature: "FiltroContenidoFeature | None" = None


def get_filtro_contenido_feature() -> "FiltroContenidoFeature | None":
    """Get the filtro contenido feature instance."""
    return _filtro_contenido_feature


def init_filtro_contenido_feature(config_storage: ConfigStorage) -> "FiltroContenidoFeature":
    """Initialize the filtro contenido feature."""
    global _filtro_contenido_feature
    _filtro_contenido_feature = FiltroContenidoFeature(config_storage)
    return _filtro_contenido_feature

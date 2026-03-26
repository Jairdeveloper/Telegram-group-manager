"""Blocked Words feature module."""

from typing import TYPE_CHECKING, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot, Update
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class BlockedWordsFeature(FeatureModule):
    """Feature module for blocked words."""

    MENU_ID = "palabras_prohibidas"
    FEATURE_NAME = "Palabras Prohibidas"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for blocked words."""

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.palabras_prohibidas_menu import create_palabras_prohibidas_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_palabras_prohibidas_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.blocked_words_enabled = not cfg.blocked_words_enabled

            await self.update_config_and_refresh(
                callback, bot, "palabras_prohibidas", _apply
            )

        async def handle_action_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.palabras_prohibidas_menu import create_palabras_prohibidas_action_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_palabras_prohibidas_action_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_action_set(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Accion no especificada", show_alert=True)
                return

            action = parts[2]
            valid_actions = {"kick", "ban", "silenciar", "warn", "aviso", "off"}

            if action not in valid_actions:
                await callback.answer("Accion no valida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.blocked_words_action = action

            await self.update_config_and_refresh(
                callback, bot, "palabras_prohibidas:action", _apply
            )

        async def handle_delete_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.palabras_prohibidas_menu import create_palabras_prohibidas_delete_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_palabras_prohibidas_delete_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_delete_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Valor no especificado", show_alert=True)
                return

            value = parts[2]
            is_on = value == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.blocked_words_delete = is_on

            await self.update_config_and_refresh(
                callback, bot, "palabras_prohibidas:delete", _apply
            )

        async def handle_add(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia la palabra o frase que deseas prohibir.\n"
                "Usa /blockedwords add <palabra> para agregarla.",
                show_alert=True
            )

        async def handle_list(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.palabras_prohibidas_menu import create_palabras_prohibidas_list_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_palabras_prohibidas_list_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_del_word(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Palabra no especificada", show_alert=True)
                return

            word = parts[2]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                if word in cfg.blocked_words:
                    cfg.blocked_words.remove(word)

            await self.update_config_and_refresh(
                callback, bot, "palabras_prohibidas:list", _apply
            )

        async def handle_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.blocked_words = []

            await self.update_config_and_refresh(
                callback, bot, "palabras_prohibidas", _apply
            )

        router.register_exact("palabras_prohibidas:show", handle_show_menu)
        router.register_exact("palabras_prohibidas:toggle", handle_toggle)

        router.register_exact("palabras_prohibidas:action:show", handle_action_show)
        router.register_callback("palabras_prohibidas:action", handle_action_set)

        router.register_exact("palabras_prohibidas:delete:show", handle_delete_show)
        router.register_callback("palabras_prohibidas:delete", handle_delete_toggle)

        router.register_exact("palabras_prohibidas:add", handle_add)
        router.register_exact("palabras_prohibidas:list", handle_list)
        router.register_callback("palabras_prohibidas:del", handle_del_word)
        router.register_exact("palabras_prohibidas:clear", handle_clear)

    async def handle_callback(
        self, update: "Update", context, config: Optional[GroupConfig] = None
    ) -> Optional[str]:
        """Legacy callback handler for backward compatibility."""
        query = update.callback_query
        if not query:
            return None

        data = query.data
        if not data or not data.startswith("palabras_prohibidas:"):
            return None

        parts = data.split(":")
        if len(parts) < 2:
            return None

        return "palabras_prohibidas"


_blocked_words_feature: Optional[BlockedWordsFeature] = None


def get_blocked_words_feature() -> Optional[BlockedWordsFeature]:
    """Get the blocked words feature instance."""
    return _blocked_words_feature


def init_blocked_words_feature(config_storage: ConfigStorage) -> BlockedWordsFeature:
    """Initialize the blocked words feature."""
    global _blocked_words_feature
    _blocked_words_feature = BlockedWordsFeature(config_storage)
    return _blocked_words_feature

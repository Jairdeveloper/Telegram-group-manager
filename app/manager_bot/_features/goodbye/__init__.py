"""Goodbye feature module."""

from typing import TYPE_CHECKING, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot, Update
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class GoodbyeFeature(FeatureModule):
    """Feature module for goodbye messages."""

    MENU_ID = "despedida"
    FEATURE_NAME = "Despedida"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for goodbye."""

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            value = parts[2] if len(parts) >= 3 else None

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            is_enabled = value == "on"

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_enabled = is_enabled

            await self.update_config_and_refresh(
                callback, bot, "despedida", _apply
            )

        async def handle_text_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_text_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_text_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_text_set(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia el texto de despedida que deseas establecer.\n"
                "Usa /goodbye set <texto> o envia un mensaje.",
                show_alert=True
            )

        async def handle_text_ver(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            text = config.goodbye_text if config else ""

            if text:
                await callback.answer(f"Texto actual:\n{text}", show_alert=True)
            else:
                await callback.answer("No hay texto de despedida configurado", show_alert=True)

        async def handle_text_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_text = ""

            await self.update_config_and_refresh(
                callback, bot, "despedida:text", _apply
            )

        async def handle_media_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_media_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_media_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_media_set(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia la multimedia (foto, video, sticker) que deseas usar.",
                show_alert=True
            )

        async def handle_media_ver(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            media = config.goodbye_media if config else None

            if media:
                await callback.answer(f"Multimedia configurado:\n{media}", show_alert=True)
            else:
                await callback.answer("No hay multimedia configurado", show_alert=True)

        async def handle_media_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_media = None

            await self.update_config_and_refresh(
                callback, bot, "despedida:media", _apply
            )

        async def handle_customize_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_customize_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_customize_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_header_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_header_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_header_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_header_set(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia el texto para el encabezado de despedida.",
                show_alert=True
            )

        async def handle_header_ver(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            header = config.goodbye_header if config else ""

            if header:
                await callback.answer(f"Encabezado actual:\n{header}", show_alert=True)
            else:
                await callback.answer("No hay encabezado configurado", show_alert=True)

        async def handle_header_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_header = ""

            await self.update_config_and_refresh(
                callback, bot, "despedida:header", _apply
            )

        async def handle_footer_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_footer_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_footer_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_footer_set(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia el texto para el pie de pagina de despedida.",
                show_alert=True
            )

        async def handle_footer_ver(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            footer = config.goodbye_footer if config else ""

            if footer:
                await callback.answer(f"Pie de pagina actual:\n{footer}", show_alert=True)
            else:
                await callback.answer("No hay pie de pagina configurado", show_alert=True)

        async def handle_footer_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_footer = ""

            await self.update_config_and_refresh(
                callback, bot, "despedida:footer", _apply
            )

        async def handle_keyboard_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_keyboard_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_keyboard_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_keyboard_set(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envia los botones inline para la despedida.\n"
                "Formato: texto1 | url1\ntexto2 | url2",
                show_alert=True
            )

        async def handle_keyboard_ver(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            keyboard = config.goodbye_inline_keyboard if config else []

            if keyboard:
                buttons = "\n".join([f"• {btn}" for btn in keyboard])
                await callback.answer(f"Teclado actual:\n{buttons}", show_alert=True)
            else:
                await callback.answer("No hay teclado configurado", show_alert=True)

        async def handle_keyboard_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(cfg: GroupConfig) -> None:
                cfg.goodbye_inline_keyboard = []

            await self.update_config_and_refresh(
                callback, bot, "despedida:keyboard", _apply
            )

        async def handle_preview(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.despedida_menu import create_despedida_preview_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_despedida_preview_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_exact("despedida:show", handle_show_menu)
        router.register_callback("despedida:toggle", handle_toggle)
        router.register_exact("despedida:preview", handle_preview)

        router.register_exact("despedida:text:show", handle_text_show)
        router.register_exact("despedida:text:set", handle_text_set)
        router.register_exact("despedida:text:ver", handle_text_ver)
        router.register_exact("despedida:text:clear", handle_text_clear)

        router.register_exact("despedida:media:show", handle_media_show)
        router.register_exact("despedida:media:set", handle_media_set)
        router.register_exact("despedida:media:ver", handle_media_ver)
        router.register_exact("despedida:media:clear", handle_media_clear)

        router.register_exact("despedida:customize:show", handle_customize_show)

        router.register_exact("despedida:header:show", handle_header_show)
        router.register_exact("despedida:header:set", handle_header_set)
        router.register_exact("despedida:header:ver", handle_header_ver)
        router.register_exact("despedida:header:clear", handle_header_clear)

        router.register_exact("despedida:footer:show", handle_footer_show)
        router.register_exact("despedida:footer:set", handle_footer_set)
        router.register_exact("despedida:footer:ver", handle_footer_ver)
        router.register_exact("despedida:footer:clear", handle_footer_clear)

        router.register_exact("despedida:keyboard:show", handle_keyboard_show)
        router.register_exact("despedida:keyboard:set", handle_keyboard_set)
        router.register_exact("despedida:keyboard:ver", handle_keyboard_ver)
        router.register_exact("despedida:keyboard:clear", handle_keyboard_clear)

    async def handle_callback(
        self, update: "Update", context, config: Optional[GroupConfig] = None
    ) -> Optional[str]:
        """Legacy callback handler for backward compatibility."""
        query = update.callback_query
        if not query:
            return None

        data = query.data
        if not data or not data.startswith("despedida:"):
            return None

        parts = data.split(":")
        if len(parts) < 2:
            return None

        return "despedida"


_goodbye_feature: Optional[GoodbyeFeature] = None


def get_goodbye_feature() -> Optional[GoodbyeFeature]:
    """Get the goodbye feature instance."""
    return _goodbye_feature


def init_goodbye_feature(config_storage: ConfigStorage) -> GoodbyeFeature:
    """Initialize the goodbye feature."""
    global _goodbye_feature
    _goodbye_feature = GoodbyeFeature(config_storage)
    return _goodbye_feature

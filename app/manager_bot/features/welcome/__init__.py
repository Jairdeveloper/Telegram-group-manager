"""Welcome feature module."""

from typing import TYPE_CHECKING

from app.manager_bot.config.group_config import GroupConfig
from app.manager_bot.config.storage import ConfigStorage
from app.manager_bot.features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot.transport.telegram.callback_router import CallbackRouter


class WelcomeFeature(FeatureModule):
    """Feature module for welcome and goodbye messages."""

    MENU_ID = "welcome"
    FEATURE_NAME = "Welcome"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for welcome."""

        async def handle_welcome_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.welcome_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Bienvenida {'activada' if enabled else 'desactivada'}",
                show_alert=True
            )

        async def handle_goodbye_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.goodbye_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Despedida {'activada' if enabled else 'desactivada'}",
                show_alert=True
            )

        async def handle_edit_text(callback: "CallbackQuery", bot: "Bot", data: str):
            prefix = data.split(":")[0]
            await callback.answer(
                f"Usa /set{prefix} <texto> para configurar el mensaje",
                show_alert=True
            )

        async def handle_edit_media(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Envía una foto/video para configurar la bienvenida",
                show_alert=True
            )

        async def handle_show_welcome(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot.menus.welcome_menu import create_welcome_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_welcome_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_goodbye(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot.menus.welcome_menu import create_goodbye_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_goodbye_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_prefix("welcome:toggle", handle_welcome_toggle)
        router.register_prefix("goodbye:toggle", handle_goodbye_toggle)
        router.register_exact("welcome:edit:text", handle_edit_text)
        router.register_exact("welcome:edit:media", handle_edit_media)
        router.register_exact("goodbye:edit:text", handle_edit_text)
        router.register_exact("welcome:show", handle_show_welcome)
        router.register_exact("goodbye:show", handle_show_goodbye)

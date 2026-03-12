"""Antispam feature module."""

from typing import Any, Dict, Optional, TYPE_CHECKING

from app.manager_bot.config.group_config import GroupConfig
from app.manager_bot.config.storage import ConfigStorage
from app.manager_bot.features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot.transport.telegram.callback_router import CallbackRouter


class AntispamFeature(FeatureModule):
    """Feature module for antispam configuration."""

    MENU_ID = "antispam"
    FEATURE_NAME = "Antispam"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for antispam."""

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

            config.antispam_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Antispam {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_spamwatch_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.spamwatch_enabled = enabled
            config.antispam_enabled = True
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"SpamWatch {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_sibyl_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.sibyl_enabled = enabled
            config.antispam_enabled = True
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Sibyl {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_sensitivity(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            sensitivity = parts[-1]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Sensibilidad configurada: {sensitivity}",
                show_alert=True
            )

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot.menus.antispam_menu import create_antispam_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_antispam_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_prefix("antispam:toggle", handle_toggle)
        router.register_prefix("antispam:spamwatch:toggle", handle_spamwatch_toggle)
        router.register_prefix("antispam:sibyl:toggle", handle_sibyl_toggle)
        router.register_prefix("antispam:sensitivity:", handle_sensitivity)
        router.register_exact("antispam:show", handle_show_menu)

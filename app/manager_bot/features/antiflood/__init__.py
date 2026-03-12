"""AntiFlood feature module."""

from typing import TYPE_CHECKING

from app.manager_bot.config.group_config import GroupConfig
from app.manager_bot.config.storage import ConfigStorage
from app.manager_bot.features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot.transport.telegram.callback_router import CallbackRouter


class AntiFloodFeature(FeatureModule):
    """Feature module for anti-flood protection."""

    MENU_ID = "antiflood"
    FEATURE_NAME = "AntiFlood"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for anti-flood."""

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
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Anti-Flood {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

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
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Intervalo configurado: {interval} segundos",
                show_alert=True
            )

        router.register_prefix("mod:antiflood:toggle", handle_toggle)
        router.register_prefix("mod:antiflood:limit:", handle_limit)
        router.register_prefix("mod:antiflood:interval:", handle_interval)

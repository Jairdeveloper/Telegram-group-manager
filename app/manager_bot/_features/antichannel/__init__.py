"""AntiChannel feature module."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class AntiChannelFeature(FeatureModule):
    """Feature module for anti-channel protection."""

    MENU_ID = "antichannel"
    FEATURE_NAME = "AntiChannel"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for anti-channel."""

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

            config.antichannel_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Anti-Canal {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.moderation_menu import create_antichannel_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_antichannel_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("mod:antichannel:toggle", handle_toggle)
        router.register_exact("mod:antichannel:show", handle_show_menu)

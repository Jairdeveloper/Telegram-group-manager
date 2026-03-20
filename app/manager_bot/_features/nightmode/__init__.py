"""NightMode feature module."""

from typing import TYPE_CHECKING, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class NightModeFeature(FeatureModule):
    """Feature module for night mode."""

    MENU_ID = "nightmode"
    FEATURE_NAME = "NightMode"

    NIGHTMODE_ACTIONS = ["mute", "hide", "kick"]

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for night mode."""

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.nightmode_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "mod:nightmode", _apply)

        async def handle_time(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Usa /nightmode start/end <hora> para configurar el horario"
            )

        async def handle_action(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            action = parts[-1]

            if action not in self.NIGHTMODE_ACTIONS:
                await callback.answer("Accion invalida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.nightmode_enabled = True

            await self.update_config_and_refresh(callback, bot, "mod:nightmode", _apply)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_nightmode_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_nightmode_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("mod:nightmode:toggle", handle_toggle)
        router.register_callback("mod:nightmode:time", handle_time)
        router.register_callback("mod:nightmode:action", handle_action)
        router.register_exact("mod:nightmode:show", handle_show_menu)

    def is_active(self, config: GroupConfig) -> bool:
        """Check if night mode is currently active."""
        if not config.nightmode_enabled:
            return False
        
        from datetime import datetime
        
        try:
            current = datetime.now().time()
            start = datetime.strptime(config.nightmode_start, "%H:%M").time()
            end = datetime.strptime(config.nightmode_end, "%H:%M").time()
            
            if start <= end:
                return start <= current <= end
            else:
                return current >= start or current <= end
        except ValueError:
            return False

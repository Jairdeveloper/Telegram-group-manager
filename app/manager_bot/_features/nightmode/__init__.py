"""NightMode feature module."""

from typing import TYPE_CHECKING, Any, Optional

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

        async def handle_time(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_schedule_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_schedule_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_mode_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_mode_selection_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_mode_selection_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_action_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            action_type = parts[3]
            enabled = parts[4] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                if action_type == "delete_media":
                    config.nightmode_delete_media = enabled
                    if enabled:
                        config.nightmode_enabled = True
                elif action_type == "silence":
                    config.nightmode_silence = enabled
                    if enabled:
                        config.nightmode_enabled = True

            await self.update_config_and_refresh(callback, bot, "mod:nightmode_mode", _apply)
            
            config = await self.get_config(chat_id)
            from app.manager_bot._menus.nightmode_menu import create_mode_selection_menu
            menu = create_mode_selection_menu(config)
            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_toggle_main_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.nightmode_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "mod:nightmode", _apply)

            config = await self.get_config(chat_id)
            from app.manager_bot._menus.nightmode_menu import create_nightmode_menu
            menu = create_nightmode_menu(config)
            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_schedule_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_schedule_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_schedule_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_schedule_select_hour(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_schedule_matrix_menu, build_schedule_keyboard
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            hour_type = parts[3]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            
            selecting_start = hour_type == "start"
            current = config.nightmode_start if config else "23:00"
            if not selecting_start:
                current = config.nightmode_end if config else "07:00"
            
            current_hour = int(current.split(":")[0]) if current else 23
            
            hour_type_label = "INICIO" if selecting_start else "FIN"
            title = f"⏰ Seleccionar hora de {hour_type_label}\n\nClic en una hora para seleccionar"
            
            keyboard = build_schedule_keyboard(selecting_start, current_hour)

            try:
                await callback.edit_message_text(
                    text=title,
                    reply_markup=keyboard,
                )
            except Exception:
                pass

        async def handle_schedule_hour(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.nightmode_menu import create_schedule_menu
            
            parts = data.split(":")
            if len(parts) < 5:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            hour_type = parts[3]
            hour_value = parts[4]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)

            if hour_type == "start":
                new_time = f"{hour_value}:00"
                def _apply(config: GroupConfig) -> None:
                    config.nightmode_start = new_time
                await self.update_config_and_refresh(callback, bot, "mod:nightmode_schedule", _apply)
                config = await self.get_config(chat_id)
                menu = create_schedule_menu(config)
                try:
                    await callback.edit_message_text(
                        text=menu.title,
                        reply_markup=menu.to_keyboard(),
                    )
                except Exception:
                    pass
            elif hour_type == "end":
                new_time = f"{hour_value}:00"
                def _apply(config: GroupConfig) -> None:
                    config.nightmode_end = new_time
                await self.update_config_and_refresh(callback, bot, "mod:nightmode_schedule", _apply)
                config = await self.get_config(chat_id)
                menu = create_schedule_menu(config)
                try:
                    await callback.edit_message_text(
                        text=menu.title,
                        reply_markup=menu.to_keyboard(),
                    )
                except Exception:
                    pass
            else:
                await callback.answer("Tipo de hora inválido", show_alert=True)

        async def handle_announcements(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.nightmode_announcements = enabled

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

        router.register_callback("mod:nightmode:toggle", handle_toggle_main_menu)
        router.register_callback("mod:nightmode:time", handle_time)
        router.register_exact("mod:nightmode:show", handle_show_menu)
        router.register_exact("mod:nightmode:mode", handle_mode_show)
        router.register_callback("mod:nightmode:action:delete_media", handle_action_toggle)
        router.register_callback("mod:nightmode:action:silence", handle_action_toggle)
        router.register_exact("mod:nightmode:schedule", handle_schedule_show)
        router.register_exact("mod:nightmode:schedule:start", handle_schedule_select_hour)
        router.register_exact("mod:nightmode:schedule:end", handle_schedule_select_hour)
        router.register_callback("mod:nightmode:schedule:start", handle_schedule_hour)
        router.register_callback("mod:nightmode:schedule:end", handle_schedule_hour)
        router.register_callback("mod:nightmode:announcements", handle_announcements)

    def is_active(self, config: GroupConfig, *, ignore_schedule: bool = False) -> bool:
        """Check if night mode is currently active."""
        if not config.nightmode_enabled:
            return False
        
        if not config.nightmode_delete_media and not config.nightmode_silence:
            return False

        if ignore_schedule:
            return True
        
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

    def should_delete_media(self, config: GroupConfig) -> bool:
        """Check if media should be deleted during night mode."""
        return config.nightmode_enabled and config.nightmode_delete_media

    def should_silence(self, config: GroupConfig) -> bool:
        """Check if users should be silenced during night mode."""
        return config.nightmode_enabled and config.nightmode_silence

    def should_announce(self, config: GroupConfig) -> bool:
        """Check if announcements should be sent."""
        return getattr(config, "nightmode_announcements", True)

    async def send_activation_announcement(self, chat_id: int, bot: "Bot") -> None:
        """Send announcement when night mode activates."""
        config = await self.get_config(chat_id)
        if not config or not self.should_announce(config):
            return

        mode_text = []
        if config.nightmode_delete_media:
            mode_text.append("eliminación de multimedia")
        if config.nightmode_silence:
            mode_text.append("silencio global")

        mode_str = " y ".join(mode_text)
        message = f"🌙 *Modo Nocturno Activado*\n\n"
        message += f"Se ha activado el {mode_str}.\n"
        message += f"Horario: {config.nightmode_start} - {config.nightmode_end}"

        try:
            await bot.send_message(chat_id, message, parse_mode="Markdown")
        except Exception:
            pass

    async def send_deactivation_announcement(self, chat_id: int, bot: "Bot") -> None:
        """Send announcement when night mode deactivates."""
        config = await self.get_config(chat_id)
        if not config or not self.should_announce(config):
            return

        message = "🌙 *Modo Nocturno Desactivado*\n\n"
        message += "El modo nocturno ha terminado. Gracias por su paciencia."

        try:
            await bot.send_message(chat_id, message, parse_mode="Markdown")
        except Exception:
            pass

    def process_message(self, message: Any, config: GroupConfig) -> bool:
        """Process a message during night mode.
        
        Returns True if message should be deleted.
        """
        if not self.is_active(config, ignore_schedule=True):
            return False

        if self.should_delete_media(config):
            if message.content_type in ["photo", "video", "audio", "voice", "video_note", "document"]:
                return True

        return False

"""Media moderation feature module."""

from typing import TYPE_CHECKING, Dict, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class MediaFeature(FeatureModule):
    """Feature module for media moderation."""

    MENU_ID = "media"
    FEATURE_NAME = "Media"

    MEDIA_TYPES = ["photo", "video", "document", "sticker"]

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)
        self._media_restrictions: Dict[int, Dict[str, bool]] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for media moderation."""

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 3:
                media_type = parts[2]
                enabled = parts[-1] == "on"
            else:
                await callback.answer("Datos incompletos", show_alert=True)
                return

            if media_type not in self.MEDIA_TYPES:
                await callback.answer("Tipo de media inválido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            if chat_id not in self._media_restrictions:
                self._media_restrictions[chat_id] = {}

            self._media_restrictions[chat_id][media_type] = enabled

            await callback.answer(
                f"{media_type.capitalize()} {'bloqueado' if enabled else 'permitido'}",
                show_alert=True
            )

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.media_menu import create_media_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            restrictions = self._media_restrictions.get(chat_id, {})
            menu = create_media_menu(restrictions)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("mod:media:photo:toggle", handle_toggle)
        router.register_callback("mod:media:video:toggle", handle_toggle)
        router.register_callback("mod:media:document:toggle", handle_toggle)
        router.register_callback("mod:media:sticker:toggle", handle_toggle)
        router.register_exact("mod:media:show", handle_show_menu)

    def is_restricted(self, chat_id: int, media_type: str) -> bool:
        """Check if media type is restricted in a chat."""
        if chat_id not in self._media_restrictions:
            return False
        return self._media_restrictions[chat_id].get(media_type, False)

    def set_restriction(self, chat_id: int, media_type: str, restricted: bool) -> None:
        """Set media type restriction."""
        if chat_id not in self._media_restrictions:
            self._media_restrictions[chat_id] = {}
        self._media_restrictions[chat_id][media_type] = restricted

    def get_restrictions(self, chat_id: int) -> Dict[str, bool]:
        """Get all media restrictions for a chat."""
        return self._media_restrictions.get(chat_id, {})

"""Warnings feature module."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


@dataclass
class Warning:
    """Represents a user warning."""
    warning_id: str
    user_id: int
    chat_id: int
    reason: str
    issued_by: int
    created_at: datetime = field(default_factory=datetime.utcnow)


class WarningsFeature(FeatureModule):
    """Feature module for user warnings."""

    MENU_ID = "warnings"
    FEATURE_NAME = "Warnings"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)
        self._warnings: Dict[int, List[Warning]] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for warnings."""

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

            config.auto_ban_on_max = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Auto-ban al llegar al límite {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_max(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            max_warnings = int(parts[-1])

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.max_warnings = max_warnings
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Máximo de advertencias: {max_warnings}",
                show_alert=True
            )

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.warnings_menu import create_warnings_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_warnings_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("warnings:autoban", handle_toggle)
        router.register_callback("warnings:max", handle_max)
        router.register_exact("warnings:show", handle_show_menu)

    def add_warning(
        self, 
        chat_id: int, 
        user_id: int, 
        reason: str, 
        actor_id: int
    ) -> Warning:
        """Add a warning to a user."""
        key = (chat_id, user_id)
        
        warning = Warning(
            warning_id=str(uuid.uuid4()),
            user_id=user_id,
            chat_id=chat_id,
            reason=reason,
            issued_by=actor_id,
        )
        
        if key not in self._warnings:
            self._warnings[key] = []
        
        self._warnings[key].append(warning)
        return warning

    def remove_warning(self, chat_id: int, user_id: int, warning_id: str) -> bool:
        """Remove a specific warning."""
        key = (chat_id, user_id)
        if key not in self._warnings:
            return False
        
        self._warnings[key] = [
            w for w in self._warnings[key] 
            if w.warning_id != warning_id
        ]
        return True

    def get_warnings(self, chat_id: int, user_id: int) -> List[Warning]:
        """Get all warnings for a user."""
        key = (chat_id, user_id)
        return self._warnings.get(key, [])

    def get_warn_count(self, chat_id: int, user_id: int) -> int:
        """Get warning count for a user."""
        return len(self.get_warnings(chat_id, user_id))

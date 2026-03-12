"""AntiLink feature module."""

from typing import TYPE_CHECKING, List, Optional

from app.manager_bot.config.group_config import GroupConfig
from app.manager_bot.config.storage import ConfigStorage
from app.manager_bot.features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot.transport.telegram.callback_router import CallbackRouter


class AntiLinkFeature(FeatureModule):
    """Feature module for anti-link protection."""

    MENU_ID = "antilink"
    FEATURE_NAME = "AntiLink"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)
        self._whitelists: dict[int, List[str]] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for anti-link."""

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

            config.antilink_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Anti-Enlaces {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_whitelist_add(callback: "CallbackQuery", bot: "Bot", data: str):
            await callback.answer(
                "Usa /antilink whitelist add <dominio> para agregar un dominio",
                show_alert=True
            )

        async def handle_whitelist_remove(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 4:
                domain = parts[3]
            else:
                await callback.answer("Dominio no especificado", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            whitelist = self._whitelists.get(chat_id, [])
            if domain in whitelist:
                whitelist.remove(domain)
                self._whitelists[chat_id] = whitelist
                await callback.answer(f"Dominio '{domain}' eliminado de whitelist", show_alert=True)
            else:
                await callback.answer(f"Dominio '{domain}' no encontrado", show_alert=True)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot.menus.antilink_menu import create_antilink_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_antilink_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_prefix("mod:antilink:toggle", handle_toggle)
        router.register_prefix("mod:antilink:whitelist:add:", handle_whitelist_add)
        router.register_prefix("mod:antilink:whitelist:remove:", handle_whitelist_remove)
        router.register_exact("mod:antilink:show", handle_show_menu)

    def get_whitelist(self, chat_id: int) -> List[str]:
        """Get whitelist for a chat."""
        return self._whitelists.get(chat_id, [])

    def add_to_whitelist(self, chat_id: int, domain: str) -> None:
        """Add domain to whitelist."""
        if chat_id not in self._whitelists:
            self._whitelists[chat_id] = []
        if domain not in self._whitelists[chat_id]:
            self._whitelists[chat_id].append(domain)

    def remove_from_whitelist(self, chat_id: int, domain: str) -> bool:
        """Remove domain from whitelist."""
        if chat_id in self._whitelists and domain in self._whitelists[chat_id]:
            self._whitelists[chat_id].remove(domain)
            return True
        return False

    def is_whitelisted(self, chat_id: int, url: str) -> bool:
        """Check if URL is whitelisted."""
        whitelist = self.get_whitelist(chat_id)
        for domain in whitelist:
            if domain in url.lower():
                return True
        return False

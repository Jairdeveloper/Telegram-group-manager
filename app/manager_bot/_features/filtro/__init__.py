"""Filtro feature - Security filters for group management."""

import re
from typing import TYPE_CHECKING, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot, Update
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


FILTRO_OBLIGATION_MAP = {
    "username": "filtro_obligation_username_action",
    "photo": "filtro_obligation_photo_action",
    "channel": "filtro_obligation_channel_action",
    "add_users": "filtro_obligation_add_users_action",
}

FILTRO_BLOCK_MAP = {
    "arabic": "filtro_block_arabic_action",
    "chinese": "filtro_block_chinese_action",
    "russian": "filtro_block_russian_action",
    "spam": "filtro_block_spam_action",
}

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
RUSSIAN_PATTERN = re.compile(r'[\u0400-\u04FF]')


class FiltroSeguridadFeature(FeatureModule):
    """Feature module for security filters."""

    MENU_ID = "filtro_seguridad"
    FEATURE_NAME = "Filtros de Seguridad"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for filtro seguridad."""

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_filtro_seguridad_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_filtro_seguridad_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_obligation_action(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Accion no reconocida", show_alert=True)
                return

            action = parts[2]
            obligation_type = parts[3]

            if obligation_type not in FILTRO_OBLIGATION_MAP:
                await callback.answer("Tipo de obligacion no reconocido", show_alert=True)
                return

            valid_actions = {"kick", "ban", "silenciar", "off", "warn", "aviso"}
            if action not in valid_actions:
                await callback.answer("Accion no reconocida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config_field = FILTRO_OBLIGATION_MAP[obligation_type]

            def _apply(cfg: GroupConfig) -> None:
                setattr(cfg, config_field, action)

            await self.update_config_and_refresh(
                callback, bot, f"filtro_seguridad:obligation:{obligation_type}", _apply
            )

        async def handle_obligation_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_obligation_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_obligation_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_obligation_type_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_obligation_action_menu

            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Tipo no especificado", show_alert=True)
                return

            obligation_type = parts[2]

            if obligation_type not in FILTRO_OBLIGATION_MAP:
                await callback.answer("Tipo de obligacion no reconocido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_obligation_action_menu(obligation_type, config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_block_action(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Accion no reconocida", show_alert=True)
                return

            action = parts[2]
            block_type = parts[3]

            if block_type not in FILTRO_BLOCK_MAP:
                await callback.answer("Tipo de bloqueo no reconocido", show_alert=True)
                return

            valid_actions = {"kick", "ban", "silenciar", "off", "warn", "aviso"}
            if action not in valid_actions:
                await callback.answer("Accion no reconocida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config_field = FILTRO_BLOCK_MAP[block_type]

            def _apply(cfg: GroupConfig) -> None:
                setattr(cfg, config_field, action)

            await self.update_config_and_refresh(
                callback, bot, f"filtro_seguridad:block:{block_type}", _apply
            )

        async def handle_block_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_block_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_block_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_block_type_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_block_action_menu

            parts = data.split(":")
            if len(parts) < 3:
                await callback.answer("Tipo no especificado", show_alert=True)
                return

            block_type = parts[2]

            if block_type not in FILTRO_BLOCK_MAP:
                await callback.answer("Tipo de bloqueo no reconocido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_block_action_menu(block_type, config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_config_show(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.filtro_seguridad_menu import create_config_menu

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_config_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_config_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) < 4:
                await callback.answer("Configuracion no reconocida", show_alert=True)
                return

            config_key = parts[2]
            value = parts[3]

            if config_key not in ("on_entry", "delete"):
                await callback.answer("Clave de configuracion no reconocida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            is_on = value == "on"

            def _apply(cfg: GroupConfig) -> None:
                if config_key == "on_entry":
                    cfg.filtro_on_entry = is_on
                elif config_key == "delete":
                    cfg.filtro_delete_messages = is_on

            await self.update_config_and_refresh(callback, bot, "filtro_seguridad:config", _apply)

        router.register_exact("filtro_seguridad:show", handle_show_menu)

        router.register_exact("filtro_seguridad:obligation:show", handle_obligation_show)
        for obl_type in FILTRO_OBLIGATION_MAP.keys():
            router.register_exact(
                f"filtro_seguridad:obligation:{obl_type}:show", handle_obligation_type_show
            )
        router.register_callback("filtro_seguridad:obligation", handle_obligation_action)

        router.register_exact("filtro_seguridad:block:show", handle_block_show)
        for blk_type in FILTRO_BLOCK_MAP.keys():
            router.register_exact(
                f"filtro_seguridad:block:{blk_type}:show", handle_block_type_show
            )
        router.register_callback("filtro_seguridad:block", handle_block_action)

        router.register_exact("filtro_seguridad:config:show", handle_config_show)
        router.register_callback("filtro_seguridad:config", handle_config_toggle)

    def check_username_filter(
        self, config: GroupConfig, username: Optional[str]
    ) -> Optional[str]:
        """Check if username filter is triggered."""
        action = config.filtro_obligation_username_action
        if action == "off":
            return None
        if not username or username.startswith("@"):
            return None
        return action

    def check_photo_filter(
        self, config: GroupConfig, has_photo: bool
    ) -> Optional[str]:
        """Check if profile photo filter is triggered."""
        action = config.filtro_obligation_photo_action
        if action == "off":
            return None
        if has_photo:
            return None
        return action

    def check_channel_filter(
        self, config: GroupConfig, is_channel_member: bool
    ) -> Optional[str]:
        """Check if channel membership filter is triggered."""
        action = config.filtro_obligation_channel_action
        if action == "off":
            return None
        if is_channel_member:
            return None
        return action

    def check_add_users_filter(
        self, config: GroupConfig, can_add_users: bool
    ) -> Optional[str]:
        """Check if add users filter is triggered."""
        action = config.filtro_obligation_add_users_action
        if action == "off":
            return None
        if not can_add_users:
            return None
        return action

    def check_arabic_filter(
        self, config: GroupConfig, name: str
    ) -> Optional[str]:
        """Check if Arabic name filter is triggered."""
        action = config.filtro_block_arabic_action
        if action == "off":
            return None
        if ARABIC_PATTERN.search(name):
            return action
        return None

    def check_chinese_filter(
        self, config: GroupConfig, name: str
    ) -> Optional[str]:
        """Check if Chinese name filter is triggered."""
        action = config.filtro_block_chinese_action
        if action == "off":
            return None
        if CHINESE_PATTERN.search(name):
            return action
        return None

    def check_russian_filter(
        self, config: GroupConfig, name: str
    ) -> Optional[str]:
        """Check if Russian name filter is triggered."""
        action = config.filtro_block_russian_action
        if action == "off":
            return None
        if RUSSIAN_PATTERN.search(name):
            return action
        return None

    def check_spam_filter(
        self, config: GroupConfig, name: str
    ) -> Optional[str]:
        """Check if spam-like name filter is triggered."""
        action = config.filtro_block_spam_action
        if action == "off":
            return None

        spam_patterns = [
            r'(.)\1{4,}',
            r'^[a-zA-Z0-9]{20,}$',
            r'https?://',
            r'buy|sell|offer|discount',
        ]

        name_lower = name.lower()
        for pattern in spam_patterns:
            if re.search(pattern, name_lower):
                return action

        return None

    async def handle_callback(
        self, update: "Update", context, config: Optional[GroupConfig] = None
    ) -> Optional[str]:
        """Legacy callback handler for backward compatibility."""
        query = update.callback_query
        if not query:
            return None

        data = query.data
        if not data or not data.startswith("filtro_seguridad:"):
            return None

        parts = data.split(":")
        if len(parts) < 3:
            return None

        _, category, action = parts[0], parts[1], parts[2]

        if action == "show":
            if category == "obligation":
                return "filtro_seguridad:obligation"
            elif category.startswith("obligation:"):
                return f"filtro_seguridad:obligation:{category.split(':')[1]}"
            elif category == "block":
                return "filtro_seguridad:block"
            elif category.startswith("block:"):
                return f"filtro_seguridad:block:{category.split(':')[1]}"
            elif category == "config":
                return "filtro_seguridad:config"

        return None


_filtro_seguridad_feature: Optional[FiltroSeguridadFeature] = None


def get_filtro_seguridad_feature() -> Optional[FiltroSeguridadFeature]:
    """Get the filtro seguridad feature instance."""
    return _filtro_seguridad_feature


def init_filtro_seguridad_feature(config_storage: ConfigStorage) -> FiltroSeguridadFeature:
    """Initialize the filtro seguridad feature."""
    global _filtro_seguridad_feature
    _filtro_seguridad_feature = FiltroSeguridadFeature(config_storage)
    return _filtro_seguridad_feature

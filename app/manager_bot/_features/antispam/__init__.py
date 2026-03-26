"""Antispam feature module."""

from typing import Any, Dict, Optional, TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


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

            def _apply(config: GroupConfig) -> None:
                config.antispam_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "antispam", _apply)

        async def handle_spamwatch_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.spamwatch_enabled = enabled
                config.antispam_enabled = True

            await self.update_config_and_refresh(callback, bot, "antispam", _apply)

        async def handle_sibyl_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.sibyl_enabled = enabled
                config.antispam_enabled = True

            await self.update_config_and_refresh(callback, bot, "antispam", _apply)

        async def handle_sensitivity(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            _sensitivity = parts[-1]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                # Placeholder for future sensitivity persistence.
                pass

            await self.update_config_and_refresh(callback, bot, "antispam:sensitivity", _apply)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispam_menu
            
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

        router.register_callback("antispam:toggle", handle_toggle)
        router.register_callback("antispam:spamwatch:toggle", handle_spamwatch_toggle)
        router.register_callback("antispam:sibyl:toggle", handle_sibyl_toggle)
        router.register_prefix("antispam:sensitivity:", handle_sensitivity)
        router.register_exact("antispam:show", handle_show_menu)

        # ---- Antispan advanced menus (merged) ----

        async def _show_antispan_menu(callback: "CallbackQuery", bot: "Bot", menu_factory):
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = menu_factory(config) if menu_factory else None
            if not menu:
                await callback.answer("Menu no disponible", show_alert=True)
                return

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_antispan_show_main(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antispam_menu import create_antispan_menu
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                state = conversation.get_state(callback.from_user.id, chat_id)
                if state and state.get("state", "").startswith("waiting_antispan_"):
                    conversation.clear_state(callback.from_user.id, chat_id)
            await _show_antispan_menu(callback, bot, create_antispan_menu)

        async def handle_antispan_show_telegram(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_telegram_menu
            await _show_antispan_menu(callback, bot, create_antispan_telegram_menu)

        async def handle_antispan_show_forward(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_forward_menu
            await _show_antispan_menu(callback, bot, create_antispan_forward_menu)

        async def handle_antispan_show_quotes(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_quotes_menu
            await _show_antispan_menu(callback, bot, create_antispan_quotes_menu)

        async def handle_antispan_show_internet(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_internet_menu
            await _show_antispan_menu(callback, bot, create_antispan_internet_menu)

        async def handle_antispan_show_forward_target(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_forward_target_menu
            target = data.split(":")[2]
            await _show_antispan_menu(callback, bot, lambda config: create_antispan_forward_target_menu(target, config))

        async def handle_antispan_show_quotes_target(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import create_antispan_quotes_target_menu
            target = data.split(":")[2]
            await _show_antispan_menu(callback, bot, lambda config: create_antispan_quotes_target_menu(target, config))

        async def handle_antispan_show_exceptions(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.antispam_menu import (
                create_antispan_telegram_exceptions_menu,
                create_antispan_forward_exceptions_menu,
                create_antispan_quotes_exceptions_menu,
                create_antispan_internet_exceptions_menu,
            )
            scope = data.split(":")[1]
            menu_factory = {
                "telegram": lambda _c: create_antispan_telegram_exceptions_menu(),
                "forward": lambda _c: create_antispan_forward_exceptions_menu(),
                "quotes": lambda _c: create_antispan_quotes_exceptions_menu(),
                "internet": lambda _c: create_antispan_internet_exceptions_menu(),
            }.get(scope)
            if menu_factory:
                await _show_antispan_menu(callback, bot, menu_factory)

        async def handle_antispan_show_exception_input(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antispam_menu import (
                create_antispan_telegram_exception_input_menu,
                create_antispan_forward_exception_input_menu,
                create_antispan_quotes_exception_input_menu,
                create_antispan_internet_exception_input_menu,
            )
            parts = data.split(":")
            scope = parts[1]
            mode = parts[-1]
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    f"waiting_antispan_{scope}_exceptions_{mode}",
                )
            menu_factory = {
                "telegram": lambda _c: create_antispan_telegram_exception_input_menu(mode),
                "forward": lambda _c: create_antispan_forward_exception_input_menu(mode),
                "quotes": lambda _c: create_antispan_quotes_exception_input_menu(mode),
                "internet": lambda _c: create_antispan_internet_exception_input_menu(mode),
            }.get(scope)
            if menu_factory:
                await _show_antispan_menu(callback, bot, menu_factory)

        async def handle_antispan_show_duration(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menu_service import get_conversation_state
            from app.manager_bot._menus.antispam_menu import create_antispan_duration_menu
            parts = data.split(":")
            scope = parts[1]
            kind = parts[2]
            chat_id = callback.message.chat.id if callback.message else None
            if chat_id:
                conversation = get_conversation_state()
                conversation.set_state(
                    callback.from_user.id,
                    chat_id,
                    f"waiting_antispan_{scope}_{kind}_duration",
                )
            await _show_antispan_menu(callback, bot, lambda config: create_antispan_duration_menu(scope, kind, config))

        async def handle_antispan_action(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            scope = parts[1]
            target = None
            action = parts[-1]
            if scope in ("forward", "quotes") and len(parts) >= 5:
                target = parts[2]

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                if scope == "telegram":
                    config.antispan_telegram_action = action
                elif scope == "internet":
                    config.antispan_internet_action = action
                elif scope == "forward" and target:
                    if target == "channels":
                        config.antispan_forward_channels_action = action
                    elif target == "groups":
                        config.antispan_forward_groups_action = action
                    elif target == "users":
                        config.antispan_forward_users_action = action
                    elif target == "bots":
                        config.antispan_forward_bots_action = action
                elif scope == "quotes" and target:
                    if target == "channels":
                        config.antispan_quotes_channels_action = action
                    elif target == "groups":
                        config.antispan_quotes_groups_action = action
                    elif target == "users":
                        config.antispan_quotes_users_action = action
                    elif target == "bots":
                        config.antispan_quotes_bots_action = action

            menu_id = "antispan"
            if scope == "telegram":
                menu_id = "antispan:telegram"
            elif scope == "internet":
                menu_id = "antispan:internet"
            elif scope == "forward" and target:
                menu_id = f"antispan:forward:{target}"
            elif scope == "quotes" and target:
                menu_id = f"antispan:quotes:{target}"

            await self.update_config_and_refresh(callback, bot, menu_id, _apply)

        async def handle_antispan_delete_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            scope = parts[1]
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                if scope == "telegram":
                    config.antispan_telegram_delete_messages = enabled
                elif scope == "internet":
                    config.antispan_internet_delete_messages = enabled
                elif scope == "forward":
                    config.antispan_forward_delete_messages = enabled
                elif scope == "quotes":
                    config.antispan_quotes_delete_messages = enabled

            menu_id = "antispan"
            if scope == "telegram":
                menu_id = "antispan:telegram"
            elif scope == "internet":
                menu_id = "antispan:internet"
            elif scope == "forward":
                menu_id = "antispan:forward"
            elif scope == "quotes":
                menu_id = "antispan:quotes"

            await self.update_config_and_refresh(callback, bot, menu_id, _apply)

        async def handle_antispan_usernames_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            enabled = data.split(":")[-1] == "on"
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.antispan_telegram_usernames_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "antispan:telegram", _apply)

        async def handle_antispan_bots_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            enabled = data.split(":")[-1] == "on"
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.antispan_telegram_bots_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "antispan:telegram", _apply)

        async def handle_antispan_duration_clear(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            scope = parts[1]
            kind = parts[-1]
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                if scope == "telegram":
                    if kind == "mute":
                        config.antispan_telegram_mute_duration_sec = None
                    elif kind == "ban":
                        config.antispan_telegram_ban_duration_sec = None
                elif scope == "forward":
                    if kind == "mute":
                        config.antispan_forward_mute_duration_sec = None
                    elif kind == "ban":
                        config.antispan_forward_ban_duration_sec = None
                elif scope == "quotes":
                    if kind == "mute":
                        config.antispan_quotes_mute_duration_sec = None
                    elif kind == "ban":
                        config.antispan_quotes_ban_duration_sec = None
                elif scope == "internet":
                    if kind == "mute":
                        config.antispan_internet_mute_duration_sec = None
                    elif kind == "ban":
                        config.antispan_internet_ban_duration_sec = None

            menu_id = f"antispan:{scope}:{kind}:duration"
            await self.update_config_and_refresh(callback, bot, menu_id, _apply)


        router.register_exact("antispan:show", handle_antispan_show_main)
        router.register_exact("antispan:telegram:show", handle_antispan_show_telegram)
        router.register_exact("antispan:forward:show", handle_antispan_show_forward)
        router.register_exact("antispan:quotes:show", handle_antispan_show_quotes)
        router.register_exact("antispan:internet:show", handle_antispan_show_internet)

        router.register_exact("antispan:forward:channels:show", handle_antispan_show_forward_target)
        router.register_exact("antispan:forward:groups:show", handle_antispan_show_forward_target)
        router.register_exact("antispan:forward:users:show", handle_antispan_show_forward_target)
        router.register_exact("antispan:forward:bots:show", handle_antispan_show_forward_target)

        router.register_exact("antispan:quotes:channels:show", handle_antispan_show_quotes_target)
        router.register_exact("antispan:quotes:groups:show", handle_antispan_show_quotes_target)
        router.register_exact("antispan:quotes:users:show", handle_antispan_show_quotes_target)
        router.register_exact("antispan:quotes:bots:show", handle_antispan_show_quotes_target)

        router.register_exact("antispan:telegram:exceptions:show", handle_antispan_show_exceptions)
        router.register_exact("antispan:forward:exceptions:show", handle_antispan_show_exceptions)
        router.register_exact("antispan:quotes:exceptions:show", handle_antispan_show_exceptions)
        router.register_exact("antispan:internet:exceptions:show", handle_antispan_show_exceptions)

        router.register_exact("antispan:telegram:exceptions:add", handle_antispan_show_exception_input)
        router.register_exact("antispan:telegram:exceptions:remove", handle_antispan_show_exception_input)
        router.register_exact("antispan:forward:exceptions:add", handle_antispan_show_exception_input)
        router.register_exact("antispan:forward:exceptions:remove", handle_antispan_show_exception_input)
        router.register_exact("antispan:quotes:exceptions:add", handle_antispan_show_exception_input)
        router.register_exact("antispan:quotes:exceptions:remove", handle_antispan_show_exception_input)
        router.register_exact("antispan:internet:exceptions:add", handle_antispan_show_exception_input)
        router.register_exact("antispan:internet:exceptions:remove", handle_antispan_show_exception_input)

        router.register_exact("antispan:telegram:mute:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:telegram:ban:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:forward:mute:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:forward:ban:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:quotes:mute:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:quotes:ban:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:internet:mute:duration:show", handle_antispan_show_duration)
        router.register_exact("antispan:internet:ban:duration:show", handle_antispan_show_duration)

        router.register_callback("antispan:telegram:action", handle_antispan_action)
        router.register_callback("antispan:internet:action", handle_antispan_action)
        router.register_callback("antispan:forward:channels:action", handle_antispan_action)
        router.register_callback("antispan:forward:groups:action", handle_antispan_action)
        router.register_callback("antispan:forward:users:action", handle_antispan_action)
        router.register_callback("antispan:forward:bots:action", handle_antispan_action)
        router.register_callback("antispan:quotes:channels:action", handle_antispan_action)
        router.register_callback("antispan:quotes:groups:action", handle_antispan_action)
        router.register_callback("antispan:quotes:users:action", handle_antispan_action)
        router.register_callback("antispan:quotes:bots:action", handle_antispan_action)

        router.register_callback("antispan:telegram:delete:toggle", handle_antispan_delete_toggle)
        router.register_callback("antispan:internet:delete:toggle", handle_antispan_delete_toggle)
        router.register_callback("antispan:forward:delete:toggle", handle_antispan_delete_toggle)
        router.register_callback("antispan:quotes:delete:toggle", handle_antispan_delete_toggle)

        router.register_callback("antispan:telegram:usernames:toggle", handle_antispan_usernames_toggle)
        router.register_callback("antispan:telegram:bots:toggle", handle_antispan_bots_toggle)

        router.register_callback("antispan:telegram:duration:clear", handle_antispan_duration_clear)
        router.register_callback("antispan:forward:duration:clear", handle_antispan_duration_clear)
        router.register_callback("antispan:quotes:duration:clear", handle_antispan_duration_clear)
        router.register_callback("antispan:internet:duration:clear", handle_antispan_duration_clear)

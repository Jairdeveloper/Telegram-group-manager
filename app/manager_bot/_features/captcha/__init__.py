"""Captcha feature module."""

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


@dataclass
class CaptchaChallenge:
    """Represents a captcha challenge."""
    challenge_id: str
    user_id: int
    chat_id: int
    challenge_type: str
    question: str
    answer: str
    options: Optional[list[str]] = None


class CaptchaFeature(FeatureModule):
    """Feature module for captcha verification."""

    MENU_ID = "captcha"
    FEATURE_NAME = "Captcha"

    CAPTCHA_MODES = ["button", "presentation", "math", "rules", "quiz"]
    CAPTCHA_FAIL_ACTIONS = ["kick", "ban", "mute"]
    CAPTCHA_TIMEOUTS = [15, 30, 60, 120, 180, 300, 600, 900, 1200, 1800]

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)
        self._challenges: Dict[str, CaptchaChallenge] = {}

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for captcha."""

        async def handle_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.captcha_enabled = enabled

            await self.update_config_and_refresh(callback, bot, "captcha", _apply)

        async def handle_mode(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_mode_menu

            parts = data.split(":")
            mode = parts[-1] if len(parts) > 1 else ""

            if mode == "show":
                chat_id = callback.message.chat.id if callback.message else None
                if not chat_id:
                    await callback.answer("Chat no identificado", show_alert=True)
                    return
                config = await self.get_config(chat_id)
                menu = create_captcha_mode_menu(config)
                try:
                    await callback.edit_message_text(
                        text=menu.title,
                        reply_markup=menu.to_keyboard(),
                    )
                except Exception:
                    pass
                return

            if mode not in self.CAPTCHA_MODES:
                await callback.answer("Modo de captcha invalido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.captcha_mode = mode
                config.captcha_enabled = True

            await self.update_config_and_refresh(callback, bot, "captcha", _apply)

        async def handle_time(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_time_menu

            parts = data.split(":")
            time_part = parts[-1] if len(parts) > 1 else ""

            if time_part == "show":
                chat_id = callback.message.chat.id if callback.message else None
                if not chat_id:
                    await callback.answer("Chat no identificado", show_alert=True)
                    return
                config = await self.get_config(chat_id)
                menu = create_captcha_time_menu(config)
                try:
                    await callback.edit_message_text(
                        text=menu.title,
                        reply_markup=menu.to_keyboard(),
                    )
                except Exception:
                    pass
                return

            try:
                timeout = int(time_part)
            except ValueError:
                await callback.answer("Tiempo invalido", show_alert=True)
                return

            if timeout not in self.CAPTCHA_TIMEOUTS:
                await callback.answer("Tiempo no valido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.captcha_timeout = timeout
                config.captcha_enabled = True

            await self.update_config_and_refresh(callback, bot, "captcha", _apply)

        async def handle_fail_action(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_fail_action_menu

            parts = data.split(":")
            action_part = parts[-1] if len(parts) > 1 else ""

            if action_part == "show":
                chat_id = callback.message.chat.id if callback.message else None
                if not chat_id:
                    await callback.answer("Chat no identificado", show_alert=True)
                    return
                config = await self.get_config(chat_id)
                menu = create_captcha_fail_action_menu(config)
                try:
                    await callback.edit_message_text(
                        text=menu.title,
                        reply_markup=menu.to_keyboard(),
                    )
                except Exception:
                    pass
                return

            action = action_part

            if action not in self.CAPTCHA_FAIL_ACTIONS:
                await callback.answer("Accion invalida", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.captcha_fail_action = action
                config.captcha_enabled = True

            await self.update_config_and_refresh(callback, bot, "captcha", _apply)

        async def handle_delete_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            def _apply(config: GroupConfig) -> None:
                config.captcha_delete_service_message = enabled

            await self.update_config_and_refresh(callback, bot, "captcha", _apply)

        async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_captcha_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_mode_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_mode_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_captcha_mode_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_time_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_time_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_captcha_time_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_fail_action_menu(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.captcha_menu import create_captcha_fail_action_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_captcha_fail_action_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("captcha:toggle", handle_toggle)
        router.register_callback("captcha:mode", handle_mode)
        router.register_callback("captcha:time", handle_time)
        router.register_callback("captcha:fail_action", handle_fail_action)
        router.register_callback("captcha:delete:toggle", handle_delete_toggle)
        router.register_exact("captcha:show", handle_show_menu)
        router.register_exact("captcha:mode:show", handle_show_mode_menu)
        router.register_exact("captcha:time:show", handle_show_time_menu)
        router.register_exact("captcha:fail_action:show", handle_show_fail_action_menu)

    def generate_captcha(self, user_id: int, chat_id: int, captcha_mode: str = "button") -> CaptchaChallenge:
        """Generate a new captcha challenge."""
        challenge_id = f"{chat_id}:{user_id}:{random.randint(1000, 9999)}"
        
        if captcha_mode == "math":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} + {b} = ?"
            answer = str(a + b)
            options = None
        elif captcha_mode == "emoji":
            emojis = ["🍎", "🍊", "🍋", "🍇", "🍓"]
            correct = random.choice(emojis)
            options = emojis
            question = f"Selecciona: {correct}"
            answer = correct
        elif captcha_mode == "rules":
            question = "Acepto las reglas del grupo"
            answer = "accept"
            options = None
        else:
            question = "Haz clic en 'Verificar' para confirmar que eres humano"
            answer = "verified"
            options = None

        challenge = CaptchaChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            chat_id=chat_id,
            challenge_type=captcha_mode,
            question=question,
            answer=answer,
            options=options,
        )
        
        self._challenges[challenge_id] = challenge
        return challenge

    def verify_captcha(self, challenge_id: str, answer: str) -> bool:
        """Verify a captcha answer."""
        challenge = self._challenges.get(challenge_id)
        if not challenge:
            return False
        
        if challenge.answer.lower() == answer.lower():
            del self._challenges[challenge_id]
            return True
        return False

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

    CAPTCHA_TYPES = ["button", "math", "emoji"]

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

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.captcha_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Captcha {'activado' if enabled else 'desactivado'}",
                show_alert=True
            )

        async def handle_type(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            captcha_type = parts[-1]

            if captcha_type not in self.CAPTCHA_TYPES:
                await callback.answer("Tipo de captcha inválido", show_alert=True)
                return

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.captcha_type = captcha_type
            config.captcha_enabled = True
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Tipo de captcha: {captcha_type}",
                show_alert=True
            )

        async def handle_timeout(callback: "CallbackQuery", bot: "Bot", data: str):
            parts = data.split(":")
            timeout = int(parts[-1])

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.captcha_timeout = timeout
            config.captcha_enabled = True
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Timeout configurado: {timeout} segundos",
                show_alert=True
            )

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

        router.register_callback("captcha:toggle", handle_toggle)
        router.register_callback("captcha:type", handle_type)
        router.register_callback("captcha:timeout", handle_timeout)
        router.register_exact("captcha:show", handle_show_menu)

    def generate_captcha(self, user_id: int, chat_id: int, captcha_type: str = "button") -> CaptchaChallenge:
        """Generate a new captcha challenge."""
        challenge_id = f"{chat_id}:{user_id}:{random.randint(1000, 9999)}"
        
        if captcha_type == "math":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} + {b} = ?"
            answer = str(a + b)
            options = None
        elif captcha_type == "emoji":
            emojis = ["🍎", "🍊", "🍋", "🍇", "🍓"]
            correct = random.choice(emojis)
            options = emojis
            question = f"Selecciona: {correct}"
            answer = correct
        else:
            question = "Haz clic en 'Verificar' para confirmar que eres humano"
            answer = "verified"
            options = None

        challenge = CaptchaChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            chat_id=chat_id,
            challenge_type=captcha_type,
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

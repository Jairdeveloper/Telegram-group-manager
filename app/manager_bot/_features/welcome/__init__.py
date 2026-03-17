"""Welcome feature module."""

from typing import TYPE_CHECKING

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._features.base import FeatureModule

if TYPE_CHECKING:
    from telegram import Bot
    from telegram import CallbackQuery
    from app.manager_bot._transport.telegram.callback_router import CallbackRouter


class WelcomeFeature(FeatureModule):
    """Feature module for welcome and goodbye messages."""

    MENU_ID = "welcome"
    FEATURE_NAME = "Welcome"

    def __init__(self, config_storage: ConfigStorage):
        super().__init__(config_storage)

    def register_callbacks(self, router: "CallbackRouter") -> None:
        """Register all callback handlers for welcome."""

        async def handle_welcome_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.welcome_menu import create_welcome_menu
            
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.welcome_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Bienvenida {'activada' if enabled else 'desactivada'}",
                show_alert=True
            )

            menu = create_welcome_menu(config)
            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_goodbye_toggle(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.welcome_menu import create_goodbye_menu
            
            parts = data.split(":")
            enabled = parts[-1] == "on"

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            config.goodbye_enabled = enabled
            config.update_timestamp(callback.from_user.id)
            await self.update_config(config)

            await callback.answer(
                f"Despedida {'activada' if enabled else 'desactivada'}",
                show_alert=True
            )

            menu = create_goodbye_menu(config)
            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_edit_text(callback: "CallbackQuery", bot: "Bot", data: str):
            """Handle edit text for welcome/goodbye messages."""
            from app.manager_bot._menu_service import get_conversation_state
            
            parts = data.split(":")
            prefix = parts[0] if parts else "welcome"
            
            chat_id = callback.message.chat.id if callback.message else None
            user_id = callback.from_user.id
            
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return
            
            conversation = get_conversation_state()
            
            if prefix == "welcome":
                conversation.set_state(user_id, chat_id, "waiting_welcome_text")
                await callback.answer(
                    "📝 *Envía el mensaje de bienvenida*\n\n"
                    "Variables disponibles:\n"
                    "• {username} - Nombre del usuario\n"
                    "• {title} - Nombre del grupo\n"
                    "• {count} - Número de miembros",
                    show_alert=True
                )
            elif prefix == "goodbye":
                conversation.set_state(user_id, chat_id, "waiting_goodbye_text")
                await callback.answer(
                    "📝 *Envía el mensaje de despedida*\n\n"
                    "Variables disponibles:\n"
                    "• {username} - Nombre del usuario\n"
                    "• {title} - Nombre del grupo",
                    show_alert=True
                )

        async def handle_edit_media(callback: "CallbackQuery", bot: "Bot", data: str):
            """Handle edit media for welcome messages."""
            from app.manager_bot._menu_service import get_conversation_state
            
            chat_id = callback.message.chat.id if callback.message else None
            user_id = callback.from_user.id
            
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return
            
            conversation = get_conversation_state()
            conversation.set_state(user_id, chat_id, "waiting_welcome_media")
            
            await callback.answer(
                "🖼️ *Envía una foto o video para la bienvenida*\n\n"
                "El archivo debe ser una imagen o video válido.",
                show_alert=True
            )

        async def handle_show_welcome(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.welcome_menu import create_welcome_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_welcome_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_show_goodbye(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.welcome_menu import create_goodbye_menu
            
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            menu = create_goodbye_menu(config)

            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        async def handle_preview(callback: "CallbackQuery", bot: "Bot", data: str):
            """Handle preview of welcome/goodbye message."""
            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                return
            
            config = await self.get_config(chat_id)
            if not config:
                return
            
            prefix = data.split(":")[0]
            if prefix == "welcome":
                text = config.welcome_text or "No hay mensaje configurado"
            elif prefix == "goodbye":
                text = config.goodbye_text or "No hay mensaje configurado"
            else:
                text = "No hay mensaje configurado"
            
            user = callback.from_user
            try:
                text = text.format(
                    username=user.first_name or "Usuario",
                    title=callback.message.chat.title or "Grupo",
                    count="0"
                )
            except KeyError:
                pass
            
            await callback.answer(text, show_alert=True)

        async def handle_customize_open(callback: "CallbackQuery", bot: "Bot", data: str):
            from app.manager_bot._menus.welcome_menu import create_welcome_customize_menu
            from app.manager_bot._menu_service import get_menu_engine

            chat_id = callback.message.chat.id if callback.message else None
            if not chat_id:
                await callback.answer("Chat no identificado", show_alert=True)
                return

            config = await self.get_config(chat_id)
            if not config:
                config = GroupConfig.create_default(chat_id, "default")

            menu_engine = get_menu_engine()
            if menu_engine:
                await menu_engine.show_menu_by_callback(callback, bot, "welcome_customize")
                return

            menu = create_welcome_customize_menu(config)
            try:
                await callback.edit_message_text(
                    text=menu.title,
                    reply_markup=menu.to_keyboard(),
                )
            except Exception:
                pass

        router.register_callback("welcome:toggle", handle_welcome_toggle)
        router.register_callback("goodbye:toggle", handle_goodbye_toggle)
        router.register_exact("welcome:edit:text", handle_edit_text)
        router.register_exact("welcome:text:edit", handle_edit_text)
        router.register_exact("welcome:edit:media", handle_edit_media)
        router.register_exact("welcome:media:edit", handle_edit_media)
        router.register_exact("goodbye:edit:text", handle_edit_text)
        router.register_exact("welcome:customize:open", handle_customize_open)
        router.register_exact("welcome:show", handle_show_welcome)
        router.register_exact("goodbye:show", handle_show_goodbye)
        router.register_callback("welcome:preview", handle_preview)
        router.register_callback("goodbye:preview", handle_preview)

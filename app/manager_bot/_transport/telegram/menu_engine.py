"""Menu engine for rendering and managing interactive menus."""

import logging
from typing import Any, Optional, TYPE_CHECKING

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.manager_bot._config.storage import ConfigStorage
from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._menus.navigation import NavigationManager
from app.manager_bot._menus.registry import MenuRegistry
from app.manager_bot._transport.telegram.callback_router import CallbackRouter

if TYPE_CHECKING:
    from telegram import Bot

logger = logging.getLogger(__name__)


class MenuEngine:
    """
    Engine for rendering and managing interactive menus.
    
    Handles:
    - Menu rendering with dynamic context
    - Callback query processing
    - Navigation between menus
    - Permission checks
    """

    def __init__(
        self,
        menu_registry: MenuRegistry,
        callback_router: CallbackRouter,
        navigation_manager: NavigationManager,
        config_storage: ConfigStorage,
    ):
        self.registry = menu_registry
        self.callback_router = callback_router
        self.navigation = navigation_manager
        self.config_storage = config_storage
        
        self._setup_navigation_callbacks()

    def _setup_navigation_callbacks(self) -> None:
        """Setup default navigation callbacks."""
        
        async def handle_back(callback, bot: "Bot", data: str):
            parts = data.split(":")
            if len(parts) >= 3:
                target_menu = parts[2]
            else:
                target_menu = "main"
            
            user_id = callback.from_user.id
            self.navigation.pop_menu(user_id)
            
            await self.show_menu_by_callback(callback, bot, target_menu)

        async def handle_home(callback, bot: "Bot", data: str):
            user_id = callback.from_user.id
            self.navigation.go_home(user_id)
            
            await self.show_menu_by_callback(callback, bot, "main")

        async def handle_noop(callback, bot: "Bot", data: str):
            """No-op handler for info buttons."""
            await callback.answer()

        async def handle_menu_show(callback, bot: "Bot", data: str):
            """Handle menu show callbacks like info:show, mod:show, etc."""
            logger.info(f"handle_menu_show called with data={data}")
            parts = data.split(":")
            if len(parts) >= 2:
                menu_id = parts[0]
                logger.debug(f"Attempting to show menu: {menu_id}")
                try:
                    await self.show_menu_by_callback(callback, bot, menu_id)
                    logger.info(f"Menu {menu_id} displayed successfully")
                except Exception as e:
                    logger.error(f"Error showing menu {menu_id}: {e}", exc_info=True)
                    await callback.answer(f"⚠️ Error al mostrar menú: {str(e)[:50]}", show_alert=True)
            else:
                logger.warning(f"Invalid menu callback data: {data}")
                await callback.answer("Menú no encontrado", show_alert=True)

        self.callback_router.register_exact("nav:back:main", handle_back, "Back to main")
        self.callback_router.register_exact("nav:home", handle_home, "Go to home")
        self.callback_router.register_exact("nav:noop", handle_noop, "No-op")
        self.callback_router.register_prefix("nav:back:", handle_back, "Back navigation")

        self.callback_router.register_exact("info:show", handle_menu_show, "Info menu")
        self.callback_router.register_exact("mod:show", handle_menu_show, "Moderation menu")
        self.callback_router.register_exact("antispam:show", handle_menu_show, "Antispam menu")
        self.callback_router.register_exact("filters:show", handle_menu_show, "Filters menu")
        self.callback_router.register_exact("welcome:show", handle_menu_show, "Welcome menu")
        self.callback_router.register_exact("captcha:show", handle_menu_show, "Captcha menu")
        self.callback_router.register_exact("reports:show", handle_menu_show, "Reports menu")
        self.callback_router.register_exact("goodbye:show", handle_menu_show, "Goodbye menu")
        self.callback_router.register_exact("nightmode:show", handle_menu_show, "Nightmode menu")
        self.callback_router.register_exact("antilink:show", handle_menu_show, "Antilink menu")
        self.callback_router.register_exact("antiflood:show", handle_menu_show, "Antiflood menu")
        self.callback_router.register_exact("antichannel:show", handle_menu_show, "Antichannel menu")
        self.callback_router.register_exact("media:show", handle_menu_show, "Media menu")
        self.callback_router.register_exact("warnings:show", handle_menu_show, "Warnings menu")

        self.callback_router.register_prefix("nav", handle_noop, "General nav")

    async def show_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        menu_id: str,
        edit: bool = True,
        text: Optional[str] = None,
    ) -> Optional[Any]:
        """Show a menu to the user."""
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return None

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        config = await self.config_storage.get(chat_id)
        keyboard = menu.to_keyboard(context={"config": config})

        menu_text = text or menu.title

        try:
            if edit and update.callback_query:
                await update.callback_query.edit_message_text(
                    text=menu_text,
                    reply_markup=keyboard,
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=menu_text,
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error(f"Error showing menu {menu_id}: {e}")
            return None

        self.navigation.push_menu(user_id, menu_id, chat_id)
        return menu

    async def show_menu_by_callback(
        self,
        callback,
        bot: "Bot",
        menu_id: str,
        text: Optional[str] = None,
    ) -> Optional[Any]:
        """Show a menu from a callback query."""
        logger.debug(f"show_menu_by_callback: menu_id={menu_id}")
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return None

        chat_id = callback.message.chat.id if callback.message else None
        user_id = callback.from_user.id

        logger.debug(f"show_menu_by_callback: chat_id={chat_id}, user_id={user_id}")

        if not chat_id:
            await callback.answer("Chat no identificado", show_alert=True)
            return None

        config = await self.config_storage.get(chat_id)
        keyboard = menu.to_keyboard(context={"config": config})

        menu_text = text or menu.title

        try:
            logger.debug(f"Attempting edit_message_text for menu {menu_id}")
            await callback.edit_message_text(
                text=menu_text,
                reply_markup=keyboard,
            )
            logger.info(f"Menu {menu_id} displayed successfully via edit_message_text")
        except Exception as e:
            logger.warning(f"edit_message_text failed for menu {menu_id}: {e}, trying reply_text")
            try:
                await callback.message.reply_text(
                    text=menu_text,
                    reply_markup=keyboard,
                )
                logger.info(f"Menu {menu_id} displayed via reply_text fallback")
            except Exception as e2:
                logger.error(f"Failed to display menu {menu_id}: {e2}", exc_info=True)
                return None

        self.navigation.push_menu(user_id, menu_id, chat_id)
        return menu

    async def handle_callback_query_raw(
        self,
        callback_data: str,
        callback_query_id: Optional[str],
        chat_id: int,
        message_id: Optional[int],
        user_id: int,
    ) -> Any:
        """Handle a raw callback query from webhook (without Update object)."""
        from app.webhook.infrastructure import get_telegram_client
        from app.config.settings import load_webhook_settings
        
        settings = load_webhook_settings()
        telegram_client = get_telegram_client(settings.telegram_bot_token)
        
        class FakeCallbackQuery:
            def __init__(self, data, callback_query_id, chat_id, message_id, user_id, client):
                self.data = data
                self.callback_query_id = callback_query_id
                self.from_user = type('User', (), {'id': user_id})()
                self.message = type('Message', (), {
                    'chat': type('Chat', (), {'id': chat_id})(),
                    'message_id': message_id
                })() if message_id else None
                self._client = client
                
            async def answer(self, text: str = None, show_alert: bool = False):
                logger.debug(f"FakeCallbackQuery.answer called: text={text}, callback_query_id={self.callback_query_id}")
                if self.callback_query_id:
                    self._client.answer_callback_query(
                        callback_query_id=self.callback_query_id,
                        text=text,
                        show_alert=show_alert
                    )
                
            async def edit_message_text(self, text: str, reply_markup: Any = None):
                if self.message:
                    keyboard = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
                    self._client.edit_message_text(
                        chat_id=self.message.chat.id,
                        message_id=self.message.message_id,
                        text=text,
                        reply_markup=keyboard
                    )
                    
            async def reply_text(self, text: str, reply_markup: Any = None):
                if self.message:
                    keyboard = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
                    self._client.send_message(
                        chat_id=self.message.chat.id,
                        text=text,
                        reply_markup=keyboard
                    )
        
        class FakeBot:
            def __init__(self, telegram_client):
                self._client = telegram_client
                
            async def send_message(self, chat_id: int, text: str, reply_markup: Any = None):
                keyboard = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
                self._client.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
                
            async def edit_message_text(self, chat_id: int, message_id: int, text: str, reply_markup: Any = None):
                keyboard = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
                self._client.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=keyboard
                )
        
        fake_callback = FakeCallbackQuery(callback_data, callback_query_id, chat_id, message_id, user_id, telegram_client)
        fake_bot = FakeBot(telegram_client)
        logger.info(f"Handling callback: data={callback_data}, callback_query_id={callback_query_id}, chat_id={chat_id}, user_id={user_id}")
        return await self.callback_router.handle(fake_callback, fake_bot)

    async def handle_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> Any:
        """Handle a callback query."""
        callback = update.callback_query
        if not callback:
            return None

        await callback.answer()

        return await self.callback_router.handle(
            callback, 
            context.bot
        )

    async def send_menu_message(
        self,
        chat_id: int,
        bot: Any,
        menu_id: str,
        text: Optional[str] = None,
    ) -> Optional[Any]:
        """Send a menu message without an update context.
        
        Args:
            chat_id: The chat ID to send the menu to
            bot: Either a telegram Bot object or a telegram_client (RequestsTelegramClient)
            menu_id: The menu to display
            text: Optional custom text
        """
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return None

        config = await self.config_storage.get(chat_id)
        keyboard = menu.to_keyboard(context={"config": config})

        menu_text = text or menu.title

        try:
            # Check if it's a telegram_client (webhook) or Bot (python-telegram-bot)
            # telegram_client has _bot_token, Bot has no such attribute
            if hasattr(bot, '_bot_token'):  # It's a telegram_client
                return bot.send_message(
                    chat_id=chat_id,
                    text=menu_text,
                    reply_markup=keyboard.to_dict() if hasattr(keyboard, 'to_dict') else keyboard,
                )
            elif hasattr(bot, 'send_message'):  # It's a Bot
                return await bot.send_message(
                    chat_id=chat_id,
                    text=menu_text,
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error(f"Error sending menu {menu_id} to {chat_id}: {e}")
            return None

    def get_current_menu(self, user_id: int) -> Optional[str]:
        """Get the current menu for a user."""
        return self.navigation.get_current(user_id)


_menu_engine: Optional[MenuEngine] = None


def get_menu_engine() -> Optional[MenuEngine]:
    """Get the global menu engine instance."""
    return _menu_engine


def set_menu_engine(engine: MenuEngine) -> None:
    """Set the global menu engine instance."""
    global _menu_engine
    _menu_engine = engine

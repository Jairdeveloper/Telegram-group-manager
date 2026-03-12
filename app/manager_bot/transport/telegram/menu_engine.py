"""Menu engine for rendering and managing interactive menus."""

import logging
from typing import Any, Optional, TYPE_CHECKING

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.manager_bot.config.storage import ConfigStorage
from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.menus.navigation import NavigationManager
from app.manager_bot.menus.registry import MenuRegistry
from app.manager_bot.transport.telegram.callback_router import CallbackRouter

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

        self.callback_router.register_exact("nav:back:main", handle_back, "Back to main")
        self.callback_router.register_exact("nav:home", handle_home, "Go to home")
        self.callback_router.register_exact("nav:noop", handle_noop, "No-op")
        self.callback_router.register_prefix("nav:back:", handle_back, "Back navigation")
        self.callback_router.register_prefix("nav:", handle_noop, "General nav")

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
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return None

        chat_id = callback.message.chat.id if callback.message else None
        user_id = callback.from_user.id

        if not chat_id:
            await callback.answer("Chat no identificado", show_alert=True)
            return None

        config = await self.config_storage.get(chat_id)
        keyboard = menu.to_keyboard(context={"config": config})

        menu_text = text or menu.title

        try:
            await callback.edit_message_text(
                text=menu_text,
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error(f"Error editing menu {menu_id}: {e}")
            try:
                await callback.message.reply_text(
                    text=menu_text,
                    reply_markup=keyboard,
                )
            except Exception as e2:
                logger.error(f"Error sending new message: {e2}")
                return None

        self.navigation.push_menu(user_id, menu_id, chat_id)
        return menu

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
        bot: "Bot",
        menu_id: str,
        text: Optional[str] = None,
    ) -> Optional[Any]:
        """Send a menu message without an update context."""
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return None

        config = await self.config_storage.get(chat_id)
        keyboard = menu.to_keyboard(context={"config": config})

        menu_text = text or menu.title

        try:
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

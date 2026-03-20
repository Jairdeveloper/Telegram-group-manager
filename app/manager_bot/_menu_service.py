"""Menu service factory for ManagerBot."""

import logging
import os
from typing import Optional, Tuple

from app.manager_bot._config.storage import InMemoryConfigStorage, get_config_storage
from app.manager_bot._config.rate_limiter import RateLimiter
from app.manager_bot._menus import MenuRegistry, NavigationManager, register_all_menus
from app.manager_bot._transport.telegram.callback_router import CallbackRouter
from app.manager_bot._transport.telegram.menu_engine import MenuEngine, set_menu_engine

logger = logging.getLogger(__name__)

_menu_engine: Optional[MenuEngine] = None
_rate_limiter: Optional[RateLimiter] = None
_conversation_state: Optional["ConversationState"] = None


class ConversationState:
    """Manage conversation states for text input flows."""
    
    CONVERSATION_STATES = {
        "waiting_welcome_text": "Bienvenida",
        "waiting_goodbye_text": "Despedida", 
        "waiting_filter_pattern": "Filtro",
        "waiting_blocked_word": "Palabra bloqueada",
        "waiting_whitelist_domain": "Dominio whitelist",
        "waiting_rules_text": "Reglas",
        "waiting_captcha_answer": "Captcha",
        "waiting_welcome_media": "Media Bienvenida",
        "waiting_antiflood_warn_duration": "Duracion Warn",
        "waiting_antiflood_ban_duration": "Duracion Ban",
        "waiting_antiflood_mute_duration": "Duracion Silenciar",
        "waiting_antispan_telegram_mute_duration": "Antispan Telegram Silencio",
        "waiting_antispan_telegram_ban_duration": "Antispan Telegram Ban",
        "waiting_antispan_telegram_exceptions_add": "Antispan Telegram Excepciones Add",
        "waiting_antispan_telegram_exceptions_remove": "Antispan Telegram Excepciones Remove",
        "waiting_antispan_forward_mute_duration": "Antispan Reenvio Silencio",
        "waiting_antispan_forward_ban_duration": "Antispan Reenvio Ban",
        "waiting_antispan_forward_exceptions_add": "Antispan Reenvio Excepciones Add",
        "waiting_antispan_forward_exceptions_remove": "Antispan Reenvio Excepciones Remove",
        "waiting_antispan_quotes_mute_duration": "Antispan Citas Silencio",
        "waiting_antispan_quotes_ban_duration": "Antispan Citas Ban",
        "waiting_antispan_quotes_exceptions_add": "Antispan Citas Excepciones Add",
        "waiting_antispan_quotes_exceptions_remove": "Antispan Citas Excepciones Remove",
        "waiting_antispan_internet_mute_duration": "Antispan Internet Silencio",
        "waiting_antispan_internet_ban_duration": "Antispan Internet Ban",
        "waiting_antispan_internet_exceptions_add": "Antispan Internet Excepciones Add",
        "waiting_antispan_internet_exceptions_remove": "Antispan Internet Excepciones Remove",
        "waiting_multimedia_duration_mute": "Duracion Multimedia Silenciar",
        "waiting_multimedia_duration_ban": "Duracion Multimedia Ban",
    }
    
    def __init__(self):
        self._states: dict[tuple[int, int], dict] = {}
    
    def set_state(
        self, 
        user_id: int, 
        chat_id: int, 
        state: str, 
        context: dict = None
    ) -> None:
        """Set a conversation state for a user in a chat."""
        key = (user_id, chat_id)
        self._states[key] = {
            "state": state,
            "context": context or {},
        }
        logger.debug(f"Set conversation state: user={user_id}, chat={chat_id}, state={state}")
    
    def get_state(self, user_id: int, chat_id: int) -> Optional[dict]:
        """Get the conversation state for a user in a chat."""
        key = (user_id, chat_id)
        return self._states.get(key)
    
    def clear_state(self, user_id: int, chat_id: int) -> None:
        """Clear the conversation state for a user in a chat."""
        key = (user_id, chat_id)
        self._states.pop(key, None)
        logger.debug(f"Cleared conversation state: user={user_id}, chat={chat_id}")
    
    def is_waiting(self, user_id: int, chat_id: int, state: str) -> bool:
        """Check if user is waiting for a specific type of input."""
        conversation = self.get_state(user_id, chat_id)
        return conversation is not None and conversation.get("state") == state


def get_conversation_state() -> ConversationState:
    """Get the global conversation state instance."""
    global _conversation_state
    if _conversation_state is None:
        _conversation_state = ConversationState()
    return _conversation_state


def create_menu_engine(
    storage_type: str = None,
    database_url: str = None,
    redis_url: str = None,
) -> Tuple[MenuEngine, RateLimiter]:
    """
    Factory function to create and initialize the MenuEngine.
    
    Sets up:
    - Menu registry with all registered menus
    - Callback router for handling inline keyboard callbacks
    - Navigation manager for menu navigation
    - Config storage (memory, postgres, or redis)
    - Rate limiter for callback protection
    
    Args:
        storage_type: Type of storage ("memory", "postgres", "redis"). 
                      If None, reads from STORAGE_TYPE env var, defaults to "memory".
        database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL.
        redis_url: Redis connection URL. If None, reads from REDIS_URL.
    
    Returns:
        Tuple of (MenuEngine, RateLimiter)
    """
    if storage_type is None:
        storage_type = os.getenv("STORAGE_TYPE", "memory")
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL")
    
    global _menu_engine, _rate_limiter
    
    logger.info("Creating menu engine...")
    
    # Create registry and register all menus
    registry = MenuRegistry()
    register_all_menus(registry)
    logger.info(f"Registered {len(registry.list_menus())} menus")
    
    # Create callback router
    callback_router = CallbackRouter()
    
    # Create navigation manager
    navigation_manager = NavigationManager()
    
    # Create config storage based on type
    config_storage = get_config_storage(storage_type, database_url, redis_url)
    logger.info(f"Using config storage: {storage_type}")
    
    # Create rate limiter
    rate_limit_calls = int(os.getenv("RATE_LIMIT_CALLS", "30"))
    rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    rate_limiter = RateLimiter(max_calls=rate_limit_calls, window_seconds=rate_limit_window)
    logger.info(f"Rate limiter: {rate_limit_calls} calls per {rate_limit_window}s")
    
    # Create and configure menu engine
    menu_engine = MenuEngine(
        menu_registry=registry,
        callback_router=callback_router,
        navigation_manager=navigation_manager,
        config_storage=config_storage,
    )
    
    # Register all features
    _register_features(callback_router, config_storage)
    
    # Set as global instance
    set_menu_engine(menu_engine)
    _menu_engine = menu_engine
    _rate_limiter = rate_limiter
    
    logger.info("Menu engine initialized successfully")
    
    return menu_engine, rate_limiter


def _register_features(callback_router: CallbackRouter, config_storage) -> None:
    """Register all feature callbacks."""
    from app.manager_bot._features.antispam import AntispamFeature
    from app.manager_bot._features.filters import FiltersFeature
    from app.manager_bot._features.welcome import WelcomeFeature
    from app.manager_bot._features.antiflood import AntiFloodFeature
    from app.manager_bot._features.antichannel import AntiChannelFeature
    from app.manager_bot._features.captcha import CaptchaFeature
    from app.manager_bot._features.warnings import WarningsFeature
    from app.manager_bot._features.reports import ReportsFeature
    from app.manager_bot._features.nightmode import NightModeFeature
    from app.manager_bot._features.antilink import AntiLinkFeature
    from app.manager_bot._features.media import MediaFeature
    from app.manager_bot._features.multimedia import MultimediaFeature
    
    features = [
        AntispamFeature(config_storage),
        FiltersFeature(config_storage),
        WelcomeFeature(config_storage),
        AntiFloodFeature(config_storage),
        AntiChannelFeature(config_storage),
        CaptchaFeature(config_storage),
        WarningsFeature(config_storage),
        ReportsFeature(config_storage),
        NightModeFeature(config_storage),
        AntiLinkFeature(config_storage),
        MediaFeature(config_storage),
        MultimediaFeature(config_storage),
    ]
    
    for feature in features:
        feature.register_callbacks(callback_router)
    
    logger.info(f"Registered {len(features)} features")
    logger.info(f"Registered callbacks: {callback_router.list_handlers()}")


def get_menu_engine() -> Optional[MenuEngine]:
    """Get the global menu engine instance."""
    global _menu_engine
    if _menu_engine is None:
        from app.manager_bot._transport.telegram.menu_engine import get_menu_engine as _get
        return _get()
    return _menu_engine


def get_rate_limiter() -> Optional[RateLimiter]:
    """Get the global rate limiter instance."""
    global _rate_limiter
    return _rate_limiter


__all__ = [
    "create_menu_engine", 
    "get_menu_engine", 
    "get_rate_limiter",
    "ConversationState",
    "get_conversation_state",
]

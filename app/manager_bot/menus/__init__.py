"""Menus package for ManagerBot interactive menus."""

from .base import MenuAction, MenuRow, MenuDefinition
from .registry import MenuRegistry
from .navigation import NavigationManager, NavigationContext


def register_all_menus(registry: MenuRegistry) -> None:
    """Register all menu definitions with the registry."""
    from app.manager_bot.menus.main_menu import create_main_menu, create_info_menu
    from app.manager_bot.menus.moderation_menu import (
        create_moderation_menu,
        create_antichannel_menu,
        create_antilink_menu,
        create_media_moderation_menu,
        create_blocked_words_menu,
        create_nightmode_menu,
    )
    from app.manager_bot.menus.antispam_menu import (
        create_antispam_menu,
        create_sensitivity_menu,
    )
    from app.manager_bot.menus.filters_menu import (
        create_filters_menu,
        create_filters_list_menu,
        create_blocked_words_menu as create_filters_words_menu,
        create_sticker_blacklist_menu,
    )
    from app.manager_bot.menus.welcome_menu import (
        create_welcome_menu,
        create_goodbye_menu,
    )

    registry.register(create_main_menu())
    registry.register(create_info_menu())

    registry.register(create_moderation_menu())
    registry.register(create_antichannel_menu())
    registry.register(create_antilink_menu())
    registry.register(create_media_moderation_menu())
    registry.register(create_blocked_words_menu())
    registry.register(create_nightmode_menu())

    registry.register(create_antispam_menu())
    registry.register(create_sensitivity_menu())

    registry.register(create_filters_menu())
    registry.register(create_filters_list_menu())
    registry.register(create_filters_words_menu())
    registry.register(create_sticker_blacklist_menu())

    registry.register(create_welcome_menu())
    registry.register(create_goodbye_menu())


__all__ = [
    "MenuAction",
    "MenuRow", 
    "MenuDefinition",
    "MenuRegistry",
    "NavigationManager",
    "NavigationContext",
    "register_all_menus",
]

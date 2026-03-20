"""Menus package for ManagerBot interactive menus."""

from .base import MenuAction, MenuRow, MenuDefinition
from .registry import MenuRegistry
from .navigation import NavigationManager, NavigationContext


def register_all_menus(registry: MenuRegistry) -> None:
    """Register all menu definitions with the registry."""
    from app.manager_bot._menus.main_menu import create_main_menu, create_info_menu
    from app.manager_bot._menus.moderation_menu import (
        create_moderation_menu,
        create_antichannel_menu,
        create_blocked_words_menu,
    )
    from app.manager_bot._menus.antilink_menu import create_antilink_menu
    from app.manager_bot._menus.media_menu import create_media_menu
    from app.manager_bot._menus.nightmode_menu import create_nightmode_menu
    from app.manager_bot._menus.antispam_menu import (
        create_antispam_menu,
        create_sensitivity_menu,
        create_antispan_telegram_menu,
        create_antispan_telegram_exceptions_menu,
        create_antispan_telegram_exception_input_menu,
        create_antispan_forward_menu,
        create_antispan_forward_target_menu,
        create_antispan_forward_exceptions_menu,
        create_antispan_forward_exception_input_menu,
        create_antispan_quotes_menu,
        create_antispan_quotes_target_menu,
        create_antispan_quotes_exceptions_menu,
        create_antispan_quotes_exception_input_menu,
        create_antispan_internet_menu,
        create_antispan_internet_exceptions_menu,
        create_antispan_internet_exception_input_menu,
        create_antispan_duration_menu,
    )
    from app.manager_bot._menus.antiflood_menu import (
        create_antiflood_menu,
        create_antiflood_limit_menu,
        create_antiflood_interval_menu,
        create_antiflood_warn_duration_menu,
        create_antiflood_ban_duration_menu,
        create_antiflood_mute_duration_menu,
    )
    from app.manager_bot._menus.filters_menu import (
        create_filters_menu,
        create_filters_list_menu,
        create_blocked_words_menu as create_filters_words_menu,
        create_sticker_blacklist_menu,
    )
    from app.manager_bot._menus.welcome_menu import (
        create_welcome_menu,
        create_welcome_customize_menu,
        create_goodbye_menu,
    )
    from app.manager_bot._menus.multimedia_menu import (
        create_multimedia_menu,
        create_multimedia_page2_menu,
        create_multimedia_duration_menu,
        create_multimedia_mute_duration_menu,
        create_multimedia_ban_duration_menu,
    )

    registry.register(create_main_menu)
    registry.register(create_info_menu)

    registry.register(create_moderation_menu)
    registry.register(create_antichannel_menu)
    registry.register(create_antilink_menu)
    registry.register(create_media_menu)
    registry.register(create_blocked_words_menu)
    registry.register(create_nightmode_menu)

    registry.register(create_antispam_menu)
    registry.register(create_sensitivity_menu)

    registry.register(create_antiflood_menu)
    registry.register(create_antiflood_limit_menu)
    registry.register(create_antiflood_interval_menu)
    registry.register(create_antiflood_warn_duration_menu)
    registry.register(create_antiflood_ban_duration_menu)
    registry.register(create_antiflood_mute_duration_menu)

    registry.register(create_antispan_telegram_menu)
    registry.register(create_antispan_telegram_exceptions_menu)
    registry.register(lambda config: create_antispan_telegram_exception_input_menu("add"))
    registry.register(lambda config: create_antispan_telegram_exception_input_menu("remove"))

    registry.register(create_antispan_forward_menu)
    for target in ("channels", "groups", "users", "bots"):
        registry.register(lambda config, t=target: create_antispan_forward_target_menu(t, config))
    registry.register(create_antispan_forward_exceptions_menu)
    registry.register(lambda config: create_antispan_forward_exception_input_menu("add"))
    registry.register(lambda config: create_antispan_forward_exception_input_menu("remove"))

    registry.register(create_antispan_quotes_menu)
    for target in ("channels", "groups", "users", "bots"):
        registry.register(lambda config, t=target: create_antispan_quotes_target_menu(t, config))
    registry.register(create_antispan_quotes_exceptions_menu)
    registry.register(lambda config: create_antispan_quotes_exception_input_menu("add"))
    registry.register(lambda config: create_antispan_quotes_exception_input_menu("remove"))

    registry.register(create_antispan_internet_menu)
    registry.register(create_antispan_internet_exceptions_menu)
    registry.register(lambda config: create_antispan_internet_exception_input_menu("add"))
    registry.register(lambda config: create_antispan_internet_exception_input_menu("remove"))
    for scope in ("telegram", "forward", "quotes", "internet"):
        registry.register(lambda config, s=scope: create_antispan_duration_menu(s, "mute", config))
        registry.register(lambda config, s=scope: create_antispan_duration_menu(s, "ban", config))

    registry.register(create_filters_menu)
    registry.register(create_filters_list_menu)
    registry.register(create_filters_words_menu)
    registry.register(create_sticker_blacklist_menu)

    registry.register(create_welcome_menu)
    registry.register(create_welcome_customize_menu)
    registry.register(create_goodbye_menu)

    registry.register(create_multimedia_menu)
    registry.register(create_multimedia_page2_menu)
    registry.register(create_multimedia_duration_menu)
    registry.register(create_multimedia_mute_duration_menu)
    registry.register(create_multimedia_ban_duration_menu)


__all__ = [
    "MenuAction",
    "MenuRow", 
    "MenuDefinition",
    "MenuRegistry",
    "NavigationManager",
    "NavigationContext",
    "register_all_menus",
]

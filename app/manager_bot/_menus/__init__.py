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
    from app.manager_bot._menus.filtro_contenido_menu import (
        create_filtro_contenido_menu,
        create_filtro_contenido_list_menu,
        create_filtro_contenido_words_menu,
        create_filtro_contenido_sticker_menu,
    )
    from app.manager_bot._menus.welcome_menu import (
        create_welcome_menu,
        create_welcome_customize_menu,
    )
    from app.manager_bot._menus.despedida_menu import (
        create_despedida_menu,
        create_despedida_text_menu,
        create_despedida_media_menu,
        create_despedida_customize_menu,
        create_despedida_header_menu,
        create_despedida_footer_menu,
        create_despedida_keyboard_menu,
        create_despedida_preview_menu,
    )
    from app.manager_bot._menus.multimedia_menu import (
        create_multimedia_menu,
        create_multimedia_page2_menu,
        create_multimedia_duration_menu,
        create_multimedia_mute_duration_menu,
        create_multimedia_ban_duration_menu,
    )
    from app.manager_bot._menus.captcha_menu import (
        create_captcha_menu,
        create_captcha_mode_menu,
        create_captcha_time_menu,
        create_captcha_fail_action_menu,
    )
    from app.manager_bot._menus.filtro_seguridad_menu import (
        create_filtro_seguridad_menu,
        create_obligation_menu,
        create_obligation_action_menu,
        create_block_menu,
        create_block_action_menu,
        create_config_menu,
    )
    from app.manager_bot._menus.palabras_prohibidas_menu import (
        create_palabras_prohibidas_menu,
        create_palabras_prohibidas_action_menu,
        create_palabras_prohibidas_delete_menu,
        create_palabras_prohibidas_add_menu,
        create_palabras_prohibidas_list_menu,
    )
    from app.manager_bot._menus.reports_menu import (
        create_reports_menu,
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

    registry.register(create_filtro_contenido_menu)
    registry.register(create_filtro_contenido_list_menu)
    registry.register(create_filtro_contenido_words_menu)
    registry.register(create_filtro_contenido_sticker_menu)

    registry.register(create_welcome_menu)
    registry.register(create_welcome_customize_menu)

    registry.register(create_despedida_menu)
    registry.register(create_despedida_text_menu)
    registry.register(create_despedida_media_menu)
    registry.register(create_despedida_customize_menu)
    registry.register(create_despedida_header_menu)
    registry.register(create_despedida_footer_menu)
    registry.register(create_despedida_keyboard_menu)
    registry.register(create_despedida_preview_menu)

    registry.register(create_multimedia_menu)
    registry.register(create_multimedia_page2_menu)
    registry.register(create_multimedia_duration_menu)
    registry.register(create_multimedia_mute_duration_menu)
    registry.register(create_multimedia_ban_duration_menu)

    registry.register(create_captcha_menu)
    registry.register(create_captcha_mode_menu)
    registry.register(create_captcha_time_menu)
    registry.register(create_captcha_fail_action_menu)

    registry.register(create_filtro_seguridad_menu)
    registry.register(create_obligation_menu)
    for obligation in ("username", "photo", "channel", "add_users"):
        registry.register(lambda config, o=obligation: create_obligation_action_menu(o, config))

    registry.register(create_block_menu)
    for block in ("arabic", "chinese", "russian", "spam"):
        registry.register(lambda config, b=block: create_block_action_menu(b, config))

    registry.register(create_config_menu)

    registry.register(create_palabras_prohibidas_menu)
    registry.register(create_palabras_prohibidas_action_menu)
    registry.register(create_palabras_prohibidas_delete_menu)
    registry.register(create_palabras_prohibidas_add_menu)
    registry.register(create_palabras_prohibidas_list_menu)

    registry.register(create_reports_menu)


__all__ = [
    "MenuAction",
    "MenuRow", 
    "MenuDefinition",
    "MenuRegistry",
    "NavigationManager",
    "NavigationContext",
    "register_all_menus",
]

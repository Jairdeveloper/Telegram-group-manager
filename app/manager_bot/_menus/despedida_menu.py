"""Despedida menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_despedida_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Despedida menu."""
    enabled = config.goodbye_enabled if config else False
    status = "✅ Activo" if enabled else "❌ Apagado"

    has_text = bool(config.goodbye_text) if config else False
    has_media = bool(config.goodbye_media) if config else False

    title = f"👋🏻 Despedida\n\nEstado: {status}"

    menu = MenuDefinition(
        menu_id="despedida",
        title=title,
        parent_menu="main",
    )

    menu.add_row() \
        .add_action(f"despedida:toggle:{'off' if enabled else 'on'}", 
                    "Desactivar" if enabled else "Activar")

    menu.add_row() \
        .add_action("despedida:text:show", "Texto") \
        .add_action("despedida:text:ver", "Ver Texto")

    menu.add_row() \
        .add_action("despedida:media:show", "Multimedia") \
        .add_action("despedida:media:ver", "Ver Multimedia")

    menu.add_row() \
        .add_action("despedida:customize:show", "Personalizar Mensaje")

    menu.add_row() \
        .add_action("despedida:preview", "Vista Previa Completa")

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_despedida_text_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the text configuration submenu."""
    current_text = config.goodbye_text if config else ""
    has_text = bool(current_text)

    title = (
        "📝 Texto de Despedida\n\n"
        f"Texto actual:\n{current_text[:100]}{'...' if len(current_text) > 100 else ''}"
    )

    menu = MenuDefinition(
        menu_id="despedida:text",
        title=title,
        parent_menu="despedida",
    )

    menu.add_row() \
        .add_action("despedida:text:set", "Establecer Texto") \
        .add_action("despedida:text:ver", "Ver Texto")

    if has_text:
        menu.add_row().add_action("despedida:text:clear", "Borrar Texto")

    menu.add_row().add_action("despedida:show", "Volver")

    return menu


def create_despedida_media_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the media configuration submenu."""
    has_media = bool(config.goodbye_media) if config else False

    title = (
        "🖼 Multimedia de Despedida\n\n"
        f"Estado: {'✅ Configurado' if has_media else '❌ No configurado'}"
    )

    menu = MenuDefinition(
        menu_id="despedida:media",
        title=title,
        parent_menu="despedida",
    )

    menu.add_row() \
        .add_action("despedida:media:set", "Establecer Multimedia") \
        .add_action("despedida:media:ver", "Ver Multimedia")

    if has_media:
        menu.add_row().add_action("despedida:media:clear", "Borrar Multimedia")

    menu.add_row().add_action("despedida:show", "Volver")

    return menu


def create_despedida_customize_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the customization submenu."""
    has_header = bool(config.goodbye_header) if config else False
    has_footer = bool(config.goodbye_footer) if config else False
    has_keyboard = bool(config.goodbye_inline_keyboard) if config else False

    title = (
        "⚙️ Personalizar Mensaje\n\n"
        f"Encabezado: {'✅' if has_header else '❌'}\n"
        f"Pie de pagina: {'✅' if has_footer else '❌'}\n"
        f"Teclado Inline: {'✅' if has_keyboard else '❌'}"
    )

    menu = MenuDefinition(
        menu_id="despedida:customize",
        title=title,
        parent_menu="despedida",
    )

    menu.add_row() \
        .add_action("despedida:header:ver", "Ver Encabezado") \
        .add_action("despedida:header:set", "Editar Encabezado")

    menu.add_row() \
        .add_action("despedida:footer:ver", "Ver Pie de Pagina") \
        .add_action("despedida:footer:set", "Editar Pie de Pagina")

    menu.add_row() \
        .add_action("despedida:keyboard:ver", "Ver Teclado") \
        .add_action("despedida:keyboard:set", "Editar Teclado")

    menu.add_row().add_action("despedida:show", "Volver")

    return menu


def create_despedida_header_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the header configuration submenu."""
    current_header = config.goodbye_header if config else ""
    has_header = bool(current_header)

    title = (
        "📌 Encabezado\n\n"
        f"Actual:\n{current_header[:100]}{'...' if len(current_header) > 100 else ''}"
    )

    menu = MenuDefinition(
        menu_id="despedida:header",
        title=title,
        parent_menu="despedida:customize",
    )

    menu.add_row() \
        .add_action("despedida:header:set", "Establecer") \
        .add_action("despedida:header:ver", "Ver")

    if has_header:
        menu.add_row().add_action("despedida:header:clear", "Borrar Encabezado")

    menu.add_row().add_action("despedida:customize:show", "Volver")

    return menu


def create_despedida_footer_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the footer configuration submenu."""
    current_footer = config.goodbye_footer if config else ""
    has_footer = bool(current_footer)

    title = (
        "📝 Pie de Pagina\n\n"
        f"Actual:\n{current_footer[:100]}{'...' if len(current_footer) > 100 else ''}"
    )

    menu = MenuDefinition(
        menu_id="despedida:footer",
        title=title,
        parent_menu="despedida:customize",
    )

    menu.add_row() \
        .add_action("despedida:footer:set", "Establecer") \
        .add_action("despedida:footer:ver", "Ver")

    if has_footer:
        menu.add_row().add_action("despedida:footer:clear", "Borrar Pie de Pagina")

    menu.add_row().add_action("despedida:customize:show", "Volver")

    return menu


def create_despedida_keyboard_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the inline keyboard configuration submenu."""
    keyboard = config.goodbye_inline_keyboard if config else []
    has_keyboard = bool(keyboard)

    keyboard_info = "\n".join([f"• {row}" for row in keyboard]) if keyboard else "No configurado"

    title = (
        "🔘 Teclado Inline\n\n"
        f"Botones configurados:\n{keyboard_info}"
    )

    menu = MenuDefinition(
        menu_id="despedida:keyboard",
        title=title,
        parent_menu="despedida:customize",
    )

    menu.add_row() \
        .add_action("despedida:keyboard:set", "Establecer") \
        .add_action("despedida:keyboard:ver", "Ver")

    if has_keyboard:
        menu.add_row().add_action("despedida:keyboard:clear", "Borrar Teclado")

    menu.add_row().add_action("despedida:customize:show", "Volver")

    return menu


def create_despedida_preview_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the full preview menu."""
    header = config.goodbye_header if config else ""
    text = config.goodbye_text if config else ""
    media = config.goodbye_media if config else None
    footer = config.goodbye_footer if config else ""
    keyboard = config.goodbye_inline_keyboard if config else []

    title_parts = ["👋🏻 Vista Previa de Despedida\n\n"]

    if header:
        title_parts.append(f"📌 Encabezado:\n{header}\n\n")
    else:
        title_parts.append("📌 Encabezado: ❌ No configurado\n\n")

    if text:
        title_parts.append(f"📝 Texto:\n{text}\n\n")
    else:
        title_parts.append("📝 Texto: ❌ No configurado\n\n")

    if media:
        title_parts.append("🖼 Multimedia: ✅ Configurado\n\n")
    else:
        title_parts.append("🖼 Multimedia: ❌ No configurado\n\n")

    if keyboard:
        title_parts.append("🔘 Teclado Inline:\n")
        for row in keyboard:
            title_parts.append(f"  • {row}\n")
        title_parts.append("\n")
    else:
        title_parts.append("🔘 Teclado Inline: ❌ No configurado\n\n")

    if footer:
        title_parts.append(f"📝 Pie de Pagina:\n{footer}\n\n")
    else:
        title_parts.append("📝 Pie de Pagina: ❌ No configurado\n\n")

    title = "".join(title_parts)

    enabled = config.goodbye_enabled if config else False

    menu = MenuDefinition(
        menu_id="despedida:preview",
        title=title,
        parent_menu="despedida",
    )

    menu.add_row().add_action(f"despedida:toggle:{'off' if enabled else 'on'}",
                              "Desactivar" if enabled else "Activar")
    menu.add_row().add_action("despedida:show", "Volver")

    return menu

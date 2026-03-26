"""Media moderation menu definitions."""

from typing import Dict, Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._menus.rendering import build_title, build_section


def create_media_menu(restrictions: Optional[Dict[str, bool]] = None) -> MenuDefinition:
    """Create the media moderation settings menu."""
    restrictions = restrictions or {}
    blocked_count = sum(1 for v in restrictions.values() if v)
    title = build_title(
        "Moderacion de Multimedia",
        [build_section("Restricciones activas", str(blocked_count))],
    )

    menu = MenuDefinition(
        menu_id="mod:media",
        title=title,
        parent_menu="main",
    )

    def _label(name: str, blocked: bool) -> str:
        return f"{name}: {'Bloqueado' if blocked else 'Permitido'}"

    menu.add_row().add_action(
        f"mod:media:photo:toggle:{'off' if restrictions.get('photo') else 'on'}",
        _label("Fotos", restrictions.get('photo', False)),
    )
    menu.add_row().add_action(
        f"mod:media:video:toggle:{'off' if restrictions.get('video') else 'on'}",
        _label("Videos", restrictions.get('video', False)),
    )
    menu.add_row().add_action(
        f"mod:media:document:toggle:{'off' if restrictions.get('document') else 'on'}",
        _label("Documentos", restrictions.get('document', False)),
    )
    menu.add_row().add_action(
        f"mod:media:sticker:toggle:{'off' if restrictions.get('sticker') else 'on'}",
        _label("Stickers", restrictions.get('sticker', False)),
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu

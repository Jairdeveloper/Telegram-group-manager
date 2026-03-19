"""Media moderation menu definitions."""

from typing import Dict, Optional

from app.manager_bot._menus.base import MenuDefinition


def create_media_menu(restrictions: Optional[Dict[str, bool]] = None) -> MenuDefinition:
    """Create the media moderation settings menu."""
    menu = MenuDefinition(
        menu_id="mod:media",
        title="📸 Moderación de Multimedia",
        parent_menu="main",
    )

    restrictions = restrictions or {}

    photo_status = "🚫" if restrictions.get("photo", False) else "✅"
    menu.add_row().add_action(
        f"mod:media:photo:toggle:{'on' if restrictions.get('photo') else 'off'}",
        f"{photo_status} Fotos",
        "📷"
    )

    video_status = "🚫" if restrictions.get("video", False) else "✅"
    menu.add_row().add_action(
        f"mod:media:video:toggle:{'on' if restrictions.get('video') else 'off'}",
        f"{video_status} Videos",
        "🎬"
    )

    document_status = "🚫" if restrictions.get("document", False) else "✅"
    menu.add_row().add_action(
        f"mod:media:document:toggle:{'on' if restrictions.get('document') else 'off'}",
        f"{document_status} Documentos",
        "📄"
    )

    sticker_status = "🚫" if restrictions.get("sticker", False) else "✅"
    menu.add_row().add_action(
        f"mod:media:sticker:toggle:{'on' if restrictions.get('sticker') else 'off'}",
        f"{sticker_status} Stickers",
        "😀"
    )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu

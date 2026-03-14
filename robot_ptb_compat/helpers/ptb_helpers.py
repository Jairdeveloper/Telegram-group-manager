"""Re-export de helpers de PTB."""

from typing import Any, Optional

try:
    from telegram.helpers import (
        escape_markdown,
        mention_html,
        mention_markdown,
        effective_message_type,
        create_deep_linked_url,
    )

    __all__ = [
        "escape_markdown",
        "mention_html",
        "mention_markdown",
        "effective_message_type",
        "create_deep_linked_url",
    ]
except ImportError:
    def escape_markdown(
        text: str, 
        version: int = 1, 
        entity_type: Optional[str] = None
    ) -> str:
        import re
        if version == 1:
            escape_chars = r"_*`["
        elif version == 2:
            if entity_type in ["pre", "code"]:
                escape_chars = r"\`"
            elif entity_type in ["text_link", "custom_emoji"]:
                escape_chars = r"\)"
            else:
                escape_chars = r"\_*[]()~`>#+-=|{}.!"
        else:
            raise ValueError("Markdown version must be either 1 or 2!")
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    def mention_html(user_id: int, name: str) -> str:
        from html import escape
        return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'

    def mention_markdown(user_id: int, name: str, version: int = 1) -> str:
        tg_link = f"tg://user?id={user_id}"
        if version == 1:
            return f"[{name}]({tg_link})"
        return f"[{escape_markdown(name, version=version)}]({tg_link})"

    def effective_message_type(entity: Any) -> Optional[str]:
        return None

    def create_deep_linked_url(
        bot_username: str, 
        payload: Optional[str] = None, 
        group: bool = False
    ) -> str:
        if not bot_username or len(bot_username) <= 3:
            raise ValueError("Invalid bot_username")
        base_url = f"https://t.me/{bot_username}"
        if not payload:
            return base_url
        key = "startgroup" if group else "start"
        return f"{base_url}?{key}={payload}"

    __all__ = [
        "escape_markdown",
        "mention_html",
        "mention_markdown",
        "effective_message_type",
        "create_deep_linked_url",
    ]

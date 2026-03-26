"""Navigation management for menu system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class NavigationContext:
    """Navigation context for a user in a specific chat."""
    user_id: int
    chat_id: int
    current_menu: str
    menu_stack: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.utcnow)


class NavigationManager:
    """Manages navigation between menus."""

    def __init__(self):
        self._contexts: Dict[int, NavigationContext] = {}

    def push_menu(self, user_id: int, menu_id: str, chat_id: int) -> None:
        """Navigate to a new menu, pushing current to stack."""
        ctx = self._contexts.get(user_id)
        if ctx:
            ctx.menu_stack.append(ctx.current_menu)
            ctx.current_menu = menu_id
        else:
            ctx = NavigationContext(
                user_id=user_id,
                chat_id=chat_id,
                current_menu=menu_id,
            )
        ctx.last_update = datetime.utcnow()
        self._contexts[user_id] = ctx

    def pop_menu(self, user_id: int) -> Optional[str]:
        """Navigate back to previous menu."""
        ctx = self._contexts.get(user_id)
        if ctx and ctx.menu_stack:
            ctx.current_menu = ctx.menu_stack.pop()
            ctx.last_update = datetime.utcnow()
            return ctx.current_menu
        return None

    def go_home(self, user_id: int) -> str:
        """Navigate to main menu, clearing stack."""
        ctx = self._contexts.get(user_id)
        if ctx:
            ctx.menu_stack.clear()
            ctx.current_menu = "main"
            ctx.last_update = datetime.utcnow()
        return "main"

    def get_current(self, user_id: int) -> Optional[str]:
        """Get current menu for user."""
        ctx = self._contexts.get(user_id)
        return ctx.current_menu if ctx else None

    def get_context(self, user_id: int) -> Optional[NavigationContext]:
        """Get full navigation context for user."""
        return self._contexts.get(user_id)

    def set_metadata(self, user_id: int, key: str, value: Any) -> None:
        """Set metadata for current navigation session."""
        ctx = self._contexts.get(user_id)
        if ctx:
            ctx.metadata[key] = value

    def get_metadata(self, user_id: int, key: str) -> Optional[Any]:
        """Get metadata from current navigation session."""
        ctx = self._contexts.get(user_id)
        return ctx.metadata.get(key) if ctx else None

    def clear_context(self, user_id: int) -> None:
        """Clear navigation context for user."""
        if user_id in self._contexts:
            del self._contexts[user_id]

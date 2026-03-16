"""Keyboard builder for dynamic inline keyboards."""

from typing import Any, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardBuilder:
    """Fluent builder for creating inline keyboards."""

    def __init__(self):
        self._rows: List[List[InlineKeyboardButton]] = []

    @staticmethod
    def create() -> "KeyboardBuilder":
        """Create a new keyboard builder."""
        return KeyboardBuilder()

    def add_button(
        self,
        text: str,
        callback_data: str,
        emoji: Optional[str] = None
    ) -> "KeyboardBuilder":
        """Add a single button to a new row."""
        display_text = f"{emoji} {text}" if emoji else text
        self._rows.append(
            [InlineKeyboardButton(display_text, callback_data=callback_data)]
        )
        return self

    def add_toggle(
        self,
        label: str,
        current_value: bool,
        callback_prefix: str
    ) -> "KeyboardBuilder":
        """Add a toggle button that switches between on/off."""
        emoji = "✅" if current_value else "❌"
        value = "off" if current_value else "on"
        return self.add_button(
            f"{label}: {value}",
            f"{callback_prefix}:{value}",
            emoji
        )

    def add_row(self, *buttons: InlineKeyboardButton) -> "KeyboardBuilder":
        """Add a custom row of buttons."""
        if buttons:
            self._rows.append(list(buttons))
        return self

    def add_back(
        self,
        menu_id: str,
        label: str = "🔙 Volver"
    ) -> "KeyboardBuilder":
        """Add a back button."""
        return self.add_button(label, f"nav:back:{menu_id}")

    def add_home(self, label: str = "🏠 Menú Principal") -> "KeyboardBuilder":
        """Add a home button."""
        return self.add_button(label, "nav:home")

    def add_info_row(
        self,
        label: str,
        value: str,
        emoji: str = "ℹ️"
    ) -> "KeyboardBuilder":
        """Add an info row (label: value) as a button."""
        return self.add_button(f"{emoji} {label}: {value}", "nav:noop")

    def build(self) -> InlineKeyboardMarkup:
        """Build the keyboard markup."""
        return InlineKeyboardMarkup(self._rows)

    def build_pagination(
        self,
        items: List[dict],
        page: int,
        per_page: int,
        callback_prefix: str
    ) -> "KeyboardBuilder":
        """Build a keyboard with pagination."""
        total_pages = (len(items) + per_page - 1) // per_page
        start = page * per_page
        end = min(start + per_page, len(items))

        for item in items[start:end]:
            self.add_button(
                item.get("label", str(item)),
                f"{callback_prefix}:view:{item['id']}"
            )

        nav_buttons: List[InlineKeyboardButton] = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("◀️", callback_data=f"{callback_prefix}:page:{page - 1}")
            )
        
        nav_buttons.append(
            InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="nav:noop")
        )
        
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton("▶️", callback_data=f"{callback_prefix}:page:{page + 1}")
            )

        if nav_buttons:
            self.add_row(*nav_buttons)

        return self

    def build_selection_list(
        self,
        items: List[dict],
        callback_prefix: str,
        max_per_row: int = 2
    ) -> "KeyboardBuilder":
        """Build a selection list from items."""
        row: List[InlineKeyboardButton] = []
        for item in items:
            row.append(
                InlineKeyboardButton(
                    item.get("label", str(item)),
                    callback_data=f"{callback_prefix}:select:{item['id']}"
                )
            )
            if len(row) >= max_per_row:
                self._rows.append(row)
                row = []
        
        if row:
            self._rows.append(row)
        
        return self

    def clear(self) -> "KeyboardBuilder":
        """Clear all rows."""
        self._rows = []
        return self

    @property
    def rows(self) -> List[List[InlineKeyboardButton]]:
        """Get current rows."""
        return self._rows

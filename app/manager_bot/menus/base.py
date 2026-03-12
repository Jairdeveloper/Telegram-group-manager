"""Base classes for menu system."""

from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import InlineKeyboardMarkup


@dataclass
class MenuAction:
    """Represents an action within a menu."""
    callback_data: str
    label: str
    emoji: Optional[str] = None

    def __post_init__(self):
        if self.emoji:
            self.label = f"{self.emoji} {self.label}"


@dataclass
class MenuRow:
    """A row of buttons in a menu."""
    actions: list[MenuAction] = field(default_factory=list)

    def add_action(
        self, 
        callback_data: str, 
        label: str, 
        emoji: Optional[str] = None
    ) -> "MenuRow":
        """Add an action to this row."""
        self.actions.append(MenuAction(callback_data, label, emoji))
        return self


@dataclass
class MenuDefinition:
    """Defines a complete menu."""
    menu_id: str
    title: str
    rows: list[MenuRow] = field(default_factory=list)
    back_button: Optional[str] = None
    parent_menu: Optional[str] = None
    description: Optional[str] = None

    def add_row(self) -> MenuRow:
        """Add a new row to the menu."""
        row = MenuRow()
        self.rows.append(row)
        return row

    def to_keyboard(self, context: Optional[dict[str, Any]] = None) -> "InlineKeyboardMarkup":
        """Convert to InlineKeyboard format for python-telegram-bot."""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = []
        for row in self.rows:
            buttons = []
            for action in row.actions:
                text = action.label
                buttons.append(
                    InlineKeyboardButton(text, callback_data=action.callback_data)
                )
            if buttons:
                keyboard.append(buttons)
        
        return InlineKeyboardMarkup(keyboard)

    def with_back_button(self, target_menu: Optional[str] = None) -> "MenuDefinition":
        """Add a back button to the menu."""
        back_target = target_menu or self.parent_menu or "main"
        if self.rows:
            self.rows.append(
                MenuRow([MenuAction(f"nav:back:{back_target}", "🔙 Volver")])
            )
        return self

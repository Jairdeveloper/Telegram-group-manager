"""Group configuration model for ManagerBot."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class GroupConfig:
    """Complete configuration for a group."""
    chat_id: int
    tenant_id: str

    antiflood_enabled: bool = False
    antiflood_limit: int = 5
    antiflood_interval: int = 5

    antichannel_enabled: bool = False
    antilink_enabled: bool = False

    antispam_enabled: bool = False
    spamwatch_enabled: bool = False
    sibyl_enabled: bool = False

    captcha_enabled: bool = False
    captcha_timeout: int = 300
    captcha_type: str = "button"

    welcome_enabled: bool = False
    welcome_text: str = ""
    welcome_media: Optional[str] = None

    goodbye_enabled: bool = False
    goodbye_text: str = ""

    blocked_words: List[str] = field(default_factory=list)
    filters: List[Dict[str, str]] = field(default_factory=list)

    nightmode_enabled: bool = False
    nightmode_start: str = "23:00"
    nightmode_end: str = "07:00"

    max_warnings: int = 3
    auto_ban_on_max: bool = True

    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupConfig":
        """Create from dictionary."""
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if "blocked_words" in data and data["blocked_words"] is None:
            data["blocked_words"] = []
        if "filters" in data and data["filters"] is None:
            data["filters"] = []
        return cls(**data)

    @classmethod
    def create_default(cls, chat_id: int, tenant_id: str) -> "GroupConfig":
        """Create default configuration for a new group."""
        return cls(chat_id=chat_id, tenant_id=tenant_id)

    def update_timestamp(self, user_id: Optional[int] = None) -> None:
        """Update the timestamp and user."""
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id

    def get_filter_count(self) -> int:
        """Get number of active filters."""
        return len(self.filters)

    def is_filter_active(self, pattern: str) -> bool:
        """Check if a filter pattern exists."""
        return any(f.get("pattern") == pattern for f in self.filters)

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
    antiflood_action: str = "off"
    antiflood_delete_messages: bool = False
    antiflood_warn_duration_sec: Optional[int] = None
    antiflood_ban_duration_sec: Optional[int] = None
    antiflood_mute_duration_sec: Optional[int] = None

    antispan_telegram_action: str = "off"
    antispan_telegram_delete_messages: bool = False
    antispan_telegram_mute_duration_sec: Optional[int] = None
    antispan_telegram_ban_duration_sec: Optional[int] = None
    antispan_telegram_usernames_enabled: bool = False
    antispan_telegram_bots_enabled: bool = False
    antispan_telegram_exceptions: List[str] = field(default_factory=list)

    antispan_forward_channels_action: str = "off"
    antispan_forward_groups_action: str = "off"
    antispan_forward_users_action: str = "off"
    antispan_forward_bots_action: str = "off"
    antispan_forward_delete_messages: bool = False
    antispan_forward_mute_duration_sec: Optional[int] = None
    antispan_forward_ban_duration_sec: Optional[int] = None
    antispan_forward_exceptions: List[str] = field(default_factory=list)

    antispan_quotes_channels_action: str = "off"
    antispan_quotes_groups_action: str = "off"
    antispan_quotes_users_action: str = "off"
    antispan_quotes_bots_action: str = "off"
    antispan_quotes_delete_messages: bool = False
    antispan_quotes_mute_duration_sec: Optional[int] = None
    antispan_quotes_ban_duration_sec: Optional[int] = None
    antispan_quotes_exceptions: List[str] = field(default_factory=list)

    antispan_internet_action: str = "off"
    antispan_internet_delete_messages: bool = False
    antispan_internet_mute_duration_sec: Optional[int] = None
    antispan_internet_ban_duration_sec: Optional[int] = None
    antispan_internet_exceptions: List[str] = field(default_factory=list)

    multimedia_story_action: str = "warn"
    multimedia_photo_action: str = "warn"
    multimedia_video_action: str = "warn"
    multimedia_album_action: str = "off"
    multimedia_gif_action: str = "off"
    multimedia_voice_action: str = "off"
    multimedia_audio_action: str = "off"
    multimedia_sticker_action: str = "off"
    multimedia_animated_sticker_action: str = "off"
    multimedia_game_sticker_action: str = "off"
    multimedia_animated_emoji_action: str = "off"
    multimedia_custom_emoji_action: str = "off"
    multimedia_file_action: str = "off"
    multimedia_game_action: str = "off"
    multimedia_contact_action: str = "ban"
    multimedia_poll_action: str = "mute"
    multimedia_checklist_action: str = "off"
    multimedia_location_action: str = "warn"
    multimedia_caps_action: str = "ban"
    multimedia_payment_action: str = "off"
    multimedia_inline_bot_action: str = "kick"
    multimedia_spoiler_action: str = "warn"
    multimedia_spoiler_media_action: str = "kick"
    multimedia_video_note_action: str = "off"
    multimedia_giveaway_action: str = "off"
    multimedia_mute_duration_sec: Optional[int] = None
    multimedia_ban_duration_sec: Optional[int] = None

    antichannel_enabled: bool = False
    antilink_enabled: bool = False

    antispam_enabled: bool = False
    spamwatch_enabled: bool = False
    sibyl_enabled: bool = False

    captcha_enabled: bool = False
    captcha_mode: str = "math"
    captcha_timeout: int = 180
    captcha_fail_action: str = "kick"
    captcha_delete_service_message: bool = False

    filtro_on_entry: bool = True
    filtro_delete_messages: bool = False

    filtro_obligation_username_action: str = "off"
    filtro_obligation_photo_action: str = "off"
    filtro_obligation_channel_action: str = "off"
    filtro_obligation_add_users_action: str = "off"

    filtro_block_arabic_action: str = "off"
    filtro_block_chinese_action: str = "off"
    filtro_block_russian_action: str = "off"
    filtro_block_spam_action: str = "off"

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
        if "antispan_telegram_exceptions" in data and data["antispan_telegram_exceptions"] is None:
            data["antispan_telegram_exceptions"] = []
        if "antispan_forward_exceptions" in data and data["antispan_forward_exceptions"] is None:
            data["antispan_forward_exceptions"] = []
        if "antispan_quotes_exceptions" in data and data["antispan_quotes_exceptions"] is None:
            data["antispan_quotes_exceptions"] = []
        if "antispan_internet_exceptions" in data and data["antispan_internet_exceptions"] is None:
            data["antispan_internet_exceptions"] = []
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

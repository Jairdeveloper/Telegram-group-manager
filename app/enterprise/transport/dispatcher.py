"""Enterprise command dispatcher helpers."""

from __future__ import annotations

from typing import FrozenSet


ENTERPRISE_COMMANDS: FrozenSet[str] = frozenset(
    {
        "/adminhelp",
        "/antichannel",
        "/antispam",
        "/anilist",
        "/ban",
        "/blacklist",
        "/config",
        "/delnote",
        "/fun",
        "/gettime",
        "/unban",
        "/filter",
        "/note",
        "/notes",
        "/reactions",
        "/rules",
        "/setnote",
        "/setrules",
        "/setwelcome",
        "/stickerblacklist",
        "/user",
        "/users",
        "/welcome",
        "/wallpaper",
        "/whoami",
    }
)


def is_enterprise_command(command: str | None) -> bool:
    if not command:
        return False
    return command.lower() in ENTERPRISE_COMMANDS

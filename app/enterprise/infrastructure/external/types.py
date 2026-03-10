"""Shared types for external moderation providers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpamCheckResult:
    source: str
    banned: bool
    reason: str = ""

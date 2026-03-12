"""Sibyl integration (optional)."""

from __future__ import annotations

from typing import Optional

import requests

from .types import SpamCheckResult


class SibylClient:
    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        timeout: int = 3,
        requests_module=requests,
    ):
        self.base_url = (base_url or "").strip()
        self.token = (token or "").strip()
        self.timeout = timeout
        self._requests = requests_module

    def enabled(self) -> bool:
        return bool(self.base_url)

    def check_user(self, user_id: int) -> Optional[SpamCheckResult]:
        if not self.base_url:
            return None

        url = f"{self.base_url.rstrip('/')}/check/{user_id}"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = self._requests.get(url, headers=headers, timeout=self.timeout)
        except Exception:
            return None

        if response.status_code in (204, 404):
            return SpamCheckResult(source="sibyl", banned=False, reason="")
        if response.status_code >= 400:
            return None

        try:
            data = response.json() if response.content else {}
        except Exception:
            data = {}

        banned = bool(
            data.get("banned")
            or data.get("ban")
            or data.get("is_banned")
            or data.get("listed")
        )
        reason = str(data.get("reason") or data.get("comment") or data.get("message") or "")
        return SpamCheckResult(source="sibyl", banned=banned, reason=reason)

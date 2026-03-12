"""AniList integration (optional)."""

from __future__ import annotations

from typing import Optional

import requests


class AnilistClient:
    def __init__(
        self,
        *,
        base_url: str = "https://graphql.anilist.co",
        timeout: int = 5,
        requests_module=requests,
    ):
        self.base_url = (base_url or "").strip()
        self.timeout = timeout
        self._requests = requests_module

    def enabled(self) -> bool:
        return bool(self.base_url)

    def search(self, query: str) -> Optional[dict]:
        if not self.base_url:
            return None

        graphql = """
        query ($search: String) {
          Media(search: $search, type: ANIME) {
            title {
              romaji
              english
            }
            format
            status
            siteUrl
          }
        }
        """
        payload = {"query": graphql, "variables": {"search": query}}

        try:
            response = self._requests.post(self.base_url, json=payload, timeout=self.timeout)
        except Exception:
            return None

        if response.status_code >= 400:
            return None

        try:
            data = response.json()
        except Exception:
            return None

        media = (data or {}).get("data", {}).get("Media")
        if not media:
            return None

        title = media.get("title") or {}
        title_text = title.get("english") or title.get("romaji") or ""
        return {
            "title": title_text,
            "format": media.get("format"),
            "status": media.get("status"),
            "url": media.get("siteUrl"),
        }

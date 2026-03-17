"""Protocol for Telegram bot clients (sync or async)."""

from __future__ import annotations

from typing import Any, Awaitable, Optional, Protocol, Union


ReturnLike = Union[Any, Awaitable[Any]]


class BotClient(Protocol):
    """Bot client interface supporting sync or async implementations."""

    def send_message(
        self,
        *,
        chat_id: int,
        text: str,
        reply_markup: Optional[Any] = None,
    ) -> ReturnLike: ...

    def edit_message_text(
        self,
        *,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[Any] = None,
    ) -> ReturnLike: ...

    def answer_callback_query(
        self,
        *,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
    ) -> ReturnLike: ...


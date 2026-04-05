"""Infrastructure adapters for webhook ports."""

import warnings
from typing import Any, Callable, Dict, Optional

import requests
from requests import Session

from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient as PortTelegramClient

try:
    from robot_ptb_compat.transport import TelegramClient as PTBTelegramClient
    HAS_ROBOT_PTB_COMPAT = True
except ImportError:
    HAS_ROBOT_PTB_COMPAT = False
    PTBTelegramClient = None


_telegram_clients: Dict[str, Any] = {}


class _LegacyRequestsTelegramClient(PortTelegramClient):
    """Internal fallback - no deprecation warning."""
    
    def __init__(self, *, bot_token: str, requests_module=requests, timeout: int = 10):
        self._bot_token = bot_token
        self._requests = requests_module
        self._timeout = timeout

    def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}

    def edit_message_text(self, *, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}

    def answer_callback_query(self, *, callback_query_id: str, text: Optional[str] = None, show_alert: bool = False) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}


def get_telegram_client(bot_token: str) -> Any:
    """Get or create a singleton TelegramClient for the given token.
    
    Uses robot-ptb-compat TelegramClient if available, otherwise falls back
    to a legacy client.
    """
    if bot_token not in _telegram_clients:
        if HAS_ROBOT_PTB_COMPAT and PTBTelegramClient is not None:
            _telegram_clients[bot_token] = PTBTelegramClient(token=bot_token)
        else:
            _telegram_clients[bot_token] = _LegacyRequestsTelegramClient(bot_token=bot_token)
    return _telegram_clients[bot_token]


class RequestsChatApiClient(ChatApiClient):
    def __init__(self, *, chat_api_url: str, requests_module=requests, timeout: int = 15):
        self._chat_api_url = chat_api_url
        self._requests = requests_module
        self._timeout = timeout

    def ask(self, *, message: str, session_id: str) -> str:
        response = self._requests.post(
            self._chat_api_url,
            params={"message": message, "session_id": session_id},
            timeout=self._timeout,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "(no response)")
        return "(chat api error)"


class RequestsTelegramClient(PortTelegramClient):
    """DEPRECATED: Use get_telegram_client() instead for PTB-compatible client."""
    
    def __init__(self, *, bot_token: str, requests_module=requests, timeout: int = 10):
        warnings.warn(
            "RequestsTelegramClient is deprecated. Use get_telegram_client() "
            "to get a PTB-compatible TelegramClient.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._bot_token = bot_token
        self._requests = requests_module
        self._timeout = timeout

    def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}

    def edit_message_text(self, *, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}

    def answer_callback_query(self, *, callback_query_id: str, text: Optional[str] = None, show_alert: bool = False) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        response = self._requests.post(url, json=payload, timeout=self._timeout)
        
        # Validar que Telegram respondió exitosamente
        if response.status_code >= 400:
            error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
            raise Exception(error_msg)
        
        return {"status_code": response.status_code, "text": response.text}


class RedisDedupStore(DedupStore):
    def __init__(self, *, redis_client):
        self._redis = redis_client

    def mark_if_new(self, *, update_id: int, ttl_seconds: int) -> bool:
        key = f"tg:update:{update_id}"
        added = self._redis.setnx(key, "1")
        if added:
            self._redis.expire(key, ttl_seconds)
            return True
        return False


class InMemoryDedupStore(DedupStore):
    def __init__(self, *, memory_store: Optional[set] = None):
        self._seen = memory_store if memory_store is not None else set()

    @property
    def seen(self) -> set:
        return self._seen

    def mark_if_new(self, *, update_id: int, ttl_seconds: int) -> bool:
        # ttl_seconds is ignored for in-memory fallback.
        if update_id in self._seen:
            return False
        self._seen.add(update_id)
        return True


class RqTaskQueue(TaskQueue):
    def __init__(self, *, queue, process_update_callable: Callable[[Dict[str, Any]], None]):
        self._queue = queue
        self._process_update_callable = process_update_callable

    def enqueue_process_update(self, *, update: Dict[str, Any]) -> Optional[str]:
        job = self._queue.enqueue(self._process_update_callable, update)
        return getattr(job, "id", None)

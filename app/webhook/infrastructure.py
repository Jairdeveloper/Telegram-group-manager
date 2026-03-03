"""Infrastructure adapters for webhook ports."""

from typing import Any, Callable, Dict, Optional

import requests

from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient


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


class RequestsTelegramClient(TelegramClient):
    def __init__(self, *, bot_token: str, requests_module=requests, timeout: int = 10):
        self._bot_token = bot_token
        self._requests = requests_module
        self._timeout = timeout

    def send_message(self, *, chat_id: int, text: str) -> Dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = self._requests.post(url, json=payload, timeout=self._timeout)
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

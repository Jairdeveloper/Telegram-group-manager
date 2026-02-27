"""Tasks executed by workers (called from RQ)."""
import os
import requests
import logging

LOGGER = logging.getLogger("webhook_tasks")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_API = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8000/api/v1/chat")


def process_update(update: dict):
    """Process update: call Chat API and send response to Telegram."""
    chat = update.get("message") or update.get("edited_message")
    if not chat:
        LOGGER.info("No message to process")
        return

    chat_id = chat["chat"]["id"]
    text = chat.get("text", "")

    try:
        r = requests.post(CHAT_API, params={"message": text, "session_id": str(chat_id)}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            reply = data.get("response", "(no response)")
        else:
            reply = "(chat api error)"
    except Exception:
        LOGGER.exception("Chat API call failed")
        reply = "(internal error)"

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": reply}, timeout=10)
    except Exception:
        LOGGER.exception("Failed to send message to Telegram")

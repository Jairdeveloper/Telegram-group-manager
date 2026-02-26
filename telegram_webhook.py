"""Webhook adapter for Telegram using FastAPI.

Usage:
  - Expose this service over HTTPS (Ingress / Let's Encrypt).
  - Set the webhook to https://<your-domain>/webhook/<TELEGRAM_BOT_TOKEN>

This adapter forwards incoming messages to the local chat API and sends replies
back to Telegram using the Bot sendMessage API.
"""
import os
import logging
import requests
from fastapi import FastAPI, Request, HTTPException

logger = logging.getLogger("telegram_webhook")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_API = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8000/api/v1/chat")

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set. Exiting.")


@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    # Only handle message updates for now
    message = data.get("message") or data.get("edited_message")
    if not message:
        return {"ok": True, "note": "no message"}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text.strip():
        # ignore non-text
        return {"ok": True}

    # Forward to chat API
    try:
        resp = requests.post(CHAT_API, params={"message": text, "session_id": str(chat_id)})
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "(no response)")
        else:
            reply = "Error from chat API"
    except Exception as e:
        logger.exception("Error calling chat API")
        reply = "Internal error"

    # Send reply via Telegram
    try:
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})
    except Exception:
        logger.exception("Failed to send message to Telegram")

    return {"ok": True}

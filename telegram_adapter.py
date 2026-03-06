"""Legacy Telegram adapter scaffold.

Operational status:
- Legacy / non-canonical runtime.
- Do not run in parallel with `app.webhook.entrypoint:app` for the same
  `TELEGRAM_BOT_TOKEN`.
- Kept only as a temporary migration path while the webhook ingress is
  consolidated.

Behavior:
- Reads `TELEGRAM_BOT_TOKEN` from env.
- For every message, posts the text to local API `/api/v1/chat` and replies
  with the returned response.
- Uses long polling for dev only; webhook is the canonical ingress.
"""
import os
import logging
import asyncio
import httpx

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()  

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8000/api/v1/chat")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set. Export it and retry.")
    raise SystemExit(1)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("No input received.")
        return

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(API_URL, params={"message": text}, timeout=15.0)

        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "")
        else:
            logger.warning("API returned %s: %s", resp.status_code, resp.text)
            reply = "Lo siento, hubo un error en el servicio."
    except Exception:
        logger.exception("Error calling chatbot API")
        reply = "Error interno: no pude contactar al servidor de chat."

    await update.message.reply_text(reply)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram adapter (python-telegram-bot, long-polling)")
    app.run_polling()


if __name__ == "__main__":
    main()

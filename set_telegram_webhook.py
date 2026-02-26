"""Script to register Telegram webhook for a given public URL.

Usage:
  python set_telegram_webhook.py https://your-domain.com/webhook/<BOT_TOKEN>
"""
import os
import sys
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def set_webhook(url: str):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    resp = requests.post(api, json={"url": url})
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python set_telegram_webhook.py https://your-domain/.../webhook/<BOT_TOKEN>")
        sys.exit(1)

    set_webhook(sys.argv[1])

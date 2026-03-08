"""Register or remove webhook for production domain.

Usage:
  python set_webhook_prod.py set https://chat.example.com/webhook/<WEBHOOK_TOKEN>
  python set_webhook_prod.py remove
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")

def set_webhook(url: str):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    resp = requests.post(api, json={"url": url})
    print(resp.status_code, resp.text)

def remove_webhook():
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    resp = requests.post(api)
    print(resp.status_code, resp.text)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("Usage: set|remove [url]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "set":
        if len(sys.argv) < 3:
            print("Usage: set <webhook_url>")
            sys.exit(1)
        set_webhook(sys.argv[2])
    elif cmd == "remove":
        remove_webhook()
    else:
        print("Unknown command")

"""Webhook entrypoint wrapper.

This keeps compatibility with the current production module while exposing
`app/webhook` as the new modular location.
"""

from telegram_webhook_prod import app as _webhook_app


def create_webhook_app():
    return _webhook_app


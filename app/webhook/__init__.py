"""Webhook package."""


def create_webhook_app():
    # Lazy import avoids circular dependency when telegram_webhook_prod
    # imports app.webhook.handlers.
    from .entrypoint import create_webhook_app as _create_webhook_app

    return _create_webhook_app()

__all__ = ["create_webhook_app"]

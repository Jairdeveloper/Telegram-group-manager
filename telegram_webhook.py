"""Legacy compatibility wrapper for old webhook module path.

Canonical source now lives in `app.webhook.entrypoint`.
"""

from app.webhook.entrypoint import app, create_webhook_app  # noqa: F401

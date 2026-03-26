"""Canonical API entrypoint (composition root).

.. deprecated::
    Este entrypoint está deprecated desde 2026-03-13.
    Use `app.webhook.entrypoint:app` como único punto de entrada.
    La API ya está incluida en el webhook entrypoint en /manager/*.
"""

from app.api.factory import create_api_app as create_modular_api_app
from app.api.bootstrap import build_api_runtime


def create_app():
    runtime = build_api_runtime()
    return create_modular_api_app(
        app_name=runtime.app_name,
        app_version=runtime.app_version,
        app_description=runtime.app_description,
        agent=runtime.agent,
        storage=runtime.storage,
    )


app = create_app()

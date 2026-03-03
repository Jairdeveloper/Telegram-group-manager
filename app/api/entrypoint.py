"""Canonical API entrypoint.

This is a transitional modular entrypoint that still reuses legacy runtime
components from `chatbot_monolith.py` while deploys migrate to `app/api/*`.
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

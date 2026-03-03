"""Canonical API entrypoint.

This is a transitional modular entrypoint that still reuses legacy runtime
components from `chatbot_monolith.py` while deploys migrate to `app/api/*`.
"""

from app.api.factory import create_api_app as create_modular_api_app
from app.config.settings import load_api_settings
from chat_service.agent import Agent
from chatbot_monolith import SimpleConversationStorage, get_default_brain


def create_app():
    api_settings = load_api_settings()
    pattern_responses, default_responses = get_default_brain()
    agent = Agent(pattern_responses, default_responses)
    storage = SimpleConversationStorage()
    return create_modular_api_app(
        app_name=api_settings.app_name,
        app_version=api_settings.app_version,
        app_description="Modular API entrypoint (legacy runtime compatibility mode)",
        agent=agent,
        storage=storage,
    )


app = create_app()

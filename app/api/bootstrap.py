"""Dependency bootstrap for API runtime."""

from dataclasses import dataclass

from app.config.settings import load_api_settings
from chat_service.agent import Agent
from chat_service.brain import get_default_brain
from chat_service.storage import SimpleConversationStorage


@dataclass
class ApiRuntime:
    app_name: str
    app_version: str
    app_description: str
    agent: Agent
    storage: SimpleConversationStorage


def build_api_runtime() -> ApiRuntime:
    """Build runtime dependencies for modular API entrypoint."""
    api_settings = load_api_settings()
    pattern_responses, default_responses = get_default_brain()
    agent = Agent(pattern_responses, default_responses)
    storage = SimpleConversationStorage()
    return ApiRuntime(
        app_name=api_settings.app_name,
        app_version=api_settings.app_version,
        app_description="Modular API entrypoint (legacy runtime compatibility mode)",
        agent=agent,
        storage=storage,
    )

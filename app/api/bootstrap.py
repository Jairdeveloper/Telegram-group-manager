"""Dependency bootstrap for API runtime."""

from dataclasses import dataclass

from app.config.settings import load_api_settings
from chat_service.agent import Agent
from chat_service.brain import get_default_brain
from app.database.repositories import create_conversation_repository
from app.database.adapters import StorageAdapter


@dataclass
class ApiRuntime:
    app_name: str
    app_version: str
    app_description: str
    agent: Agent
    storage: StorageAdapter


def build_api_runtime() -> ApiRuntime:
    """Build runtime dependencies for modular API entrypoint."""
    api_settings = load_api_settings()
    pattern_responses, default_responses = get_default_brain()
    try:
        agent = Agent(
            pattern_responses,
            default_responses,
            llm_enabled=getattr(api_settings, "llm_enabled", False),
            llm_provider=getattr(api_settings, "llm_provider", None),
            llm_model=getattr(api_settings, "llm_model", None),
        )
    except TypeError:
        # Backward-compatible for Agent implementations that only accept two args (tests/mocks).
        agent = Agent(pattern_responses, default_responses)
    
    repository = create_conversation_repository()
    storage = StorageAdapter(repository)
    
    return ApiRuntime(
        app_name=api_settings.app_name,
        app_version=api_settings.app_version,
        app_description="Modular API entrypoint with PostgreSQL support",
        agent=agent,
        storage=storage,
    )

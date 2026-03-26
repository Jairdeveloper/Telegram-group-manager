from __future__ import annotations

from typing import Optional

from app.config.settings import load_api_settings

from .factory import LLMFactory, config_from_settings


def generate_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> str:
    settings = load_api_settings()
    config = config_from_settings(
        settings,
        provider=provider,
        model=model,
        temperature=temperature,
    )

    llm = LLMFactory.get_provider(config)
    return llm.generate(prompt, system_prompt=system_prompt)

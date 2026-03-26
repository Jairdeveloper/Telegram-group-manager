from __future__ import annotations

from typing import Dict, Optional, Tuple

from .base import BaseLLMProvider, DummyProvider, FallbackProvider, LLMConfig, LLMError
from .providers.ollama import OllamaProvider
from .providers.openai import OpenAIProvider


def _normalize_provider(name: Optional[str]) -> str:
    return (name or "ollama").strip().lower()


def config_from_settings(settings, **overrides) -> LLMConfig:
    return LLMConfig(
        provider=overrides.get("provider") or getattr(settings, "llm_provider", "ollama"),
        model=overrides.get("model") or getattr(settings, "llm_model", "llama3"),
        timeout=overrides.get("timeout") or getattr(settings, "llm_timeout", 30),
        openai_api_key=getattr(settings, "openai_api_key", None),
        openai_base_url=getattr(settings, "openai_base_url", None),
        ollama_base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
        ollama_model=getattr(settings, "ollama_model", "llama3"),
        temperature=overrides.get("temperature") or getattr(settings, "llm_temperature", 0.2),
    )


class LLMFactory:
    _cache: Dict[Tuple, BaseLLMProvider] = {}

    @classmethod
    def get_provider(cls, config: LLMConfig) -> BaseLLMProvider:
        provider = _normalize_provider(config.provider)
        cache_key = (
            provider,
            config.model,
            config.timeout,
            config.openai_base_url,
            config.ollama_base_url,
            config.temperature,
        )

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        if provider == "openai":
            provider_instance = cls._build_openai_with_fallback(config)
        elif provider == "ollama":
            provider_instance = cls._build_ollama(config)
        else:
            provider_instance = DummyProvider(f"Unsupported LLM provider '{provider}'")

        cls._cache[cache_key] = provider_instance
        return provider_instance

    @classmethod
    def _build_openai(cls, config: LLMConfig) -> BaseLLMProvider:
        try:
            return OpenAIProvider(config)
        except LLMError as exc:
            return DummyProvider(str(exc))

    @classmethod
    def _build_openai_with_fallback(cls, config: LLMConfig) -> BaseLLMProvider:
        primary = cls._build_openai(config)
        if isinstance(primary, DummyProvider):
            return primary

        fallback_config = LLMConfig(
            provider="ollama",
            model=config.ollama_model,
            timeout=config.timeout,
            openai_api_key=config.openai_api_key,
            openai_base_url=config.openai_base_url,
            ollama_base_url=config.ollama_base_url,
            ollama_model=config.ollama_model,
            temperature=config.temperature,
        )
        secondary = cls._build_ollama(fallback_config)
        if isinstance(secondary, DummyProvider):
            return primary

        return FallbackProvider(
            primary,
            secondary,
            fallback_model=config.ollama_model,
            fallback_on=[
                "insufficient_quota",
                "exceeded your current quota",
            ],
        )

    @classmethod
    def _build_ollama(cls, config: LLMConfig) -> BaseLLMProvider:
        try:
            return OllamaProvider(config)
        except LLMError as exc:
            return DummyProvider(str(exc))

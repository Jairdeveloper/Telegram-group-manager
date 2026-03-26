from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "ollama"
    model: str = "llama3"
    timeout: int = 30
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    temperature: float = 0.2


class BaseLLMProvider:
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError


class DummyProvider(BaseLLMProvider):
    def __init__(self, reason: str):
        super().__init__(LLMConfig(provider="dummy", model="none"))
        self.reason = reason

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        raise LLMError(self.reason)


class FallbackProvider(BaseLLMProvider):
    """Fallback to a secondary provider for specific error conditions."""

    def __init__(
        self,
        primary: BaseLLMProvider,
        secondary: BaseLLMProvider,
        *,
        fallback_model: Optional[str] = None,
        fallback_on: Optional[list[str]] = None,
    ):
        super().__init__(primary.config)
        self.primary = primary
        self.secondary = secondary
        self.fallback_model = fallback_model
        self.fallback_on = [token.lower() for token in (fallback_on or [])]

    def _should_fallback(self, message: str) -> bool:
        if not self.fallback_on:
            return False
        msg = message.lower()
        return any(token in msg for token in self.fallback_on)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        try:
            return self.primary.generate(prompt, system_prompt=system_prompt, **kwargs)
        except LLMError as exc:
            if not self._should_fallback(str(exc)):
                raise
            logger.warning(
                "llm.primary_failed_using_fallback",
                extra={"error": str(exc)},
            )
            fallback_kwargs = dict(kwargs)
            if self.fallback_model:
                fallback_kwargs["model"] = self.fallback_model
            try:
                return self.secondary.generate(prompt, system_prompt=system_prompt, **fallback_kwargs)
            except LLMError as fallback_exc:
                raise LLMError(
                    f"Primary failed ({exc}); fallback failed ({fallback_exc})"
                ) from fallback_exc

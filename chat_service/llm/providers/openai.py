from __future__ import annotations

from typing import Optional

from openai import OpenAI

from ..base import BaseLLMProvider, LLMConfig, LLMError


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        if not config.openai_api_key:
            raise LLMError("OPENAI_API_KEY is not configured")
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            timeout=config.timeout,
        )

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        model = kwargs.get("model") or self.config.model
        temperature = kwargs.get("temperature", self.config.temperature)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
        except Exception as exc:
            raise LLMError(str(exc)) from exc

        content = response.choices[0].message.content if response.choices else ""
        return content.strip() if content else ""

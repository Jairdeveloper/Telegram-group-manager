from __future__ import annotations

from typing import Optional

import httpx

from ..base import BaseLLMProvider, LLMConfig, LLMError


class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.ollama_base_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        model = kwargs.get("model") or self.config.model
        temperature = kwargs.get("temperature", self.config.temperature)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout,
            )
            if response.status_code == 404:
                return self._generate_legacy(prompt, system_prompt, model, temperature)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise LLMError(str(exc)) from exc

        message = data.get("message") or {}
        content = message.get("content", "")
        if not content:
            raise LLMError("Empty response from Ollama")
        return content.strip()

    def _generate_legacy(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
    ) -> str:
        try:
            merged_prompt = prompt
            if system_prompt:
                merged_prompt = f"{system_prompt}\n\nUsuario: {prompt}"

            payload = {
                "model": model,
                "prompt": merged_prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }

            response = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout,
            )
            if response.status_code == 404:
                return self._generate_openai_compat(
                    messages=[
                        {"role": "system", "content": system_prompt} if system_prompt else None,
                        {"role": "user", "content": prompt},
                    ],
                    model=model,
                    temperature=temperature,
                )
            response.raise_for_status()
            data = response.json()
            content = data.get("response", "")
            if not content:
                raise LLMError("Empty response from Ollama (legacy)")
            return content.strip()
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(str(exc)) from exc

    def _generate_openai_compat(self, messages, model: str, temperature: float) -> str:
        clean_messages = [m for m in messages if m]
        payload = {
            "model": model,
            "messages": clean_messages,
            "temperature": temperature,
            "stream": False,
        }
        try:
            response = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise LLMError(str(exc)) from exc

        choices = data.get("choices") or []
        if not choices:
            raise LLMError("Empty response from Ollama (openai compat)")
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if not content:
            raise LLMError("Empty response from Ollama (openai compat)")
        return content.strip()

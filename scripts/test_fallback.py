from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from app.config.settings import load_api_settings
    from chat_service.llm.base import LLMError
    from chat_service.llm.factory import LLMFactory, config_from_settings

    load_dotenv()
    settings = load_api_settings()

    # Force OpenAI as primary to validate fallback behavior.
    config = config_from_settings(settings, provider="openai")
    provider = LLMFactory.get_provider(config)

    print(f"Provider: {provider.__class__.__name__}")
    try:
        text = provider.generate("Responde solo con OK.")
        print(f"OK: {text}")
        return 0
    except LLMError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

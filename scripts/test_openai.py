from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def main() -> int:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY no esta configurada en el entorno o .env")
        return 2

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_TEST_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

    client = OpenAI(api_key=api_key, base_url=base_url)

    print(f"Base URL: {base_url}")
    print(f"Model: {model}")

    # 1) Probar credenciales (listado de modelos)
    try:
        models = client.models.list()
        print(f"OK: models.list() -> {len(models.data)} modelos")
    except Exception as exc:
        print(f"ERROR: models.list() fallo -> {exc}")
        return 1

    # 2) Probar llamada de chat simple
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responde solo con OK"}],
            max_tokens=5,
        )
        msg = resp.choices[0].message.content if resp.choices else ""
        print(f"OK: chat.completions.create -> {msg}")
    except Exception as exc:
        print(f"ERROR: chat.completions.create fallo -> {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

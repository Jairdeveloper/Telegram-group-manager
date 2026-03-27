from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Type

from pydantic import BaseModel


@dataclass(frozen=True)
class SlotResolution:
    missing_fields: List[str]
    prompt: str


class SlotResolver:
    def missing(self, schema: Type[BaseModel], payload: Dict[str, Any]) -> SlotResolution:
        missing = []
        for name, field in schema.model_fields.items():
            if name in payload and payload[name] not in (None, ""):
                continue
            if field.is_required():
                missing.append(name)
        if not missing:
            return SlotResolution([], "")
        prompt = "Faltan parametros: " + ", ".join(missing)
        return SlotResolution(missing, prompt)

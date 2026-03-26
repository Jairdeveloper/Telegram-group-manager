from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class TemplateContext:
    action_id: str
    status: str
    data: Dict[str, Any]


class ActionTemplateEngine:
    def __init__(self):
        self._templates = {
            "error": "Ocurrió un error al ejecutar la acción.",
            "denied": "No autorizado para ejecutar esta acción.",
            "confirm": "Confirmación requerida para ejecutar la acción.",
            "preview": "Previsualización de cambios.",
            "dry_run_unsupported": "Dry-run no soportado para esta acción.",
            "rollback_unsupported": "Rollback no soportado para esta acción.",
        }

    def render(self, context: TemplateContext) -> str:
        template = self._templates.get(context.status)
        if not template:
            return "Acción ejecutada."
        return template


_default_engine: ActionTemplateEngine | None = None


def get_default_template_engine() -> ActionTemplateEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = ActionTemplateEngine()
    return _default_engine

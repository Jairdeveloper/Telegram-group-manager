from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.config.settings import load_api_settings
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


class ReasoningAction(str, Enum):
    PLAN = "plan"
    RESPOND = "respond"


@dataclass
class ReasoningDecision:
    action: ReasoningAction
    thought: str = ""


_TOOL_HINTS = (
    "buscar",
    "busca",
    "search",
    "investiga",
    "calcula",
    "calculate",
    "convierte",
    "convert",
    "clima",
    "weather",
    "pronostico",
    "temperatura",
)


class ReActReasoner:
    def __init__(
        self,
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        settings = load_api_settings()
        self.llm_enabled = settings.llm_enabled if llm_enabled is None else llm_enabled
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )

    def decide(self, message: str) -> ReasoningDecision:
        lowered = (message or "").lower()
        should_plan = any(token in lowered for token in _TOOL_HINTS)
        if should_plan:
            return ReasoningDecision(action=ReasoningAction.PLAN, thought="tool_required")
        return ReasoningDecision(action=ReasoningAction.RESPOND, thought="direct_response")

    def think(self, message: str, context: str = "") -> str:
        if not self.llm_enabled:
            return "rule_based_thought"
        prompt = (
            "Genera un pensamiento breve (una linea) sobre como responder.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Mensaje: {message}\n\n"
            "Pensamiento:"
        )
        try:
            provider = LLMFactory.get_provider(self.llm_config)
            return provider.generate(prompt)
        except LLMError:
            return "llm_unavailable"

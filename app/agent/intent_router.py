from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.config.settings import load_api_settings
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


class IntentKind(str, Enum):
    CHAT = "chat"
    AGENT_TASK = "agent_task"


@dataclass(frozen=True)
class IntentDecision:
    kind: IntentKind
    reason: str = ""
    confidence: float = 0.5


_AGENT_KEYWORDS = (
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


class IntentRouter:
    def __init__(
        self,
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        settings = load_api_settings()
        self.llm_enabled = (
            settings.intent_router_llm_enabled if llm_enabled is None else llm_enabled
        )
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )

    def route(self, message: str) -> IntentDecision:
        message = (message or "").strip()
        if not message:
            return IntentDecision(IntentKind.CHAT, reason="empty_message", confidence=0.1)

        rule_based = self._rule_based(message)
        if rule_based is not None:
            return rule_based

        if self.llm_enabled:
            llm_decision = self._llm_classify(message)
            if llm_decision is not None:
                return llm_decision

        return IntentDecision(IntentKind.CHAT, reason="default", confidence=0.4)

    def _rule_based(self, message: str) -> Optional[IntentDecision]:
        lowered = message.lower()
        if any(keyword in lowered for keyword in _AGENT_KEYWORDS):
            return IntentDecision(IntentKind.AGENT_TASK, reason="keyword_match", confidence=0.6)
        return None

    def _llm_classify(self, message: str) -> Optional[IntentDecision]:
        prompt = (
            "Clasifica el siguiente mensaje en una de estas categorias: "
            "AGENT_TASK o CHAT. Responde solo con la categoria.\n\n"
            f"Mensaje: {message}"
        )
        try:
            provider = LLMFactory.get_provider(self.llm_config)
            result = provider.generate(prompt)
        except LLMError:
            return None

        normalized = (result or "").strip().upper()
        if "AGENT_TASK" in normalized:
            return IntentDecision(IntentKind.AGENT_TASK, reason="llm_classification", confidence=0.7)
        if "CHAT" in normalized:
            return IntentDecision(IntentKind.CHAT, reason="llm_classification", confidence=0.7)
        return None


_default_router: Optional[IntentRouter] = None


def get_default_intent_router() -> IntentRouter:
    global _default_router
    if _default_router is None:
        _default_router = IntentRouter()
    return _default_router

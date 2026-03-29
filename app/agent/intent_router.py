from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

from app.config.settings import load_api_settings
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError

logger = logging.getLogger(__name__)


class IntentKind(str, Enum):
    CHAT = "chat"
    AGENT_TASK = "agent_task"
    BOT_ACTION = "bot_action"
    HELP_REQUEST = "help_request"


@dataclass(frozen=True)
class IntentDecision:
    kind: IntentKind
    reason: str = ""
    confidence: float = 0.5
    nlp_intent: Optional[str] = None


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
        nlp_enabled: Optional[bool] = None,
    ):
        settings = load_api_settings()
        self.llm_enabled = (
            settings.intent_router_llm_enabled if llm_enabled is None else llm_enabled
        )
        self.nlp_enabled = (
            getattr(settings, 'nlp_enabled', True) if nlp_enabled is None else nlp_enabled
        )
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )
        self._nlp_classifier = None

    @property
    def nlp_classifier(self):
        if self._nlp_classifier is None:
            try:
                from app.nlp.intent_classifier import IntentClassifier
                self._nlp_classifier = IntentClassifier()
            except Exception as e:
                logger.warning(f"Failed to load NLP classifier: {e}")
                self._nlp_classifier = None
        return self._nlp_classifier

    def route(self, message: str) -> IntentDecision:
        message = (message or "").strip()
        if not message:
            return IntentDecision(IntentKind.CHAT, reason="empty_message", confidence=0.1)

        if self.nlp_enabled and self.nlp_classifier:
            nlp_decision = self._nlp_classify(message)
            if nlp_decision is not None:
                return nlp_decision

        rule_based = self._rule_based(message)
        if rule_based is not None:
            return rule_based

        if self.llm_enabled:
            llm_decision = self._llm_classify(message)
            if llm_decision is not None:
                return llm_decision

        return IntentDecision(IntentKind.CHAT, reason="default", confidence=0.4)

    def _nlp_classify(self, message: str) -> Optional[IntentDecision]:
        try:
            intent, confidence = self.nlp_classifier.classify(message)
            if intent and confidence >= 0.5:
                logger.info(f"NLP classified: {intent} ({confidence})")
                
                if intent in ("get_status", "get_settings", "list_actions"):
                    return IntentDecision(
                        kind=IntentKind.BOT_ACTION,
                        reason="nlp_classification",
                        confidence=confidence,
                        nlp_intent=intent
                    )
                elif intent == "help":
                    return IntentDecision(
                        kind=IntentKind.HELP_REQUEST,
                        reason="nlp_classification",
                        confidence=confidence,
                        nlp_intent=intent
                    )
                else:
                    return IntentDecision(
                        kind=IntentKind.BOT_ACTION,
                        reason="nlp_classification",
                        confidence=confidence,
                        nlp_intent=intent
                    )
        except Exception as e:
            logger.warning(f"NLP classification failed: {e}")
        return None

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

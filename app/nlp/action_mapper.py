import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActionParseResult:
    action_id: Optional[str]
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    reason: str = ""


@dataclass
class MappingResult:
    success: bool
    action_id: Optional[str] = None
    payload: Dict[str, Any] = None
    confidence: float = 0.0
    reason: str = ""
    fallback_needed: bool = False


class ActionMapper:
    ACTION_MAPPINGS = {
        "set_welcome": {
            "action_id": "welcome.set_text",
            "default_action_id": "welcome.toggle",
            "extract_text": True,
        },
        "toggle_feature": {
            "action_id_prefix": "",
            "default_action_id_suffix": "toggle",
        },
        "set_limit": {
            "action_id": "antiflood.set_limits",
            "default_action_id": "antiflood.toggle",
            "extract_limits": True,
        },
        "add_filter": {
            "action_id": "filter.add_word",
            "extract_word": True,
        },
        "remove_filter": {
            "action_id": "filter.remove_word",
            "extract_word": True,
        },
        "set_goodbye": {
            "action_id": "goodbye.set_text",
            "default_action_id": "goodbye.toggle",
            "extract_text": True,
        },
    }

    FEATURE_ACTIONS = {
        "welcome": ["welcome.toggle", "welcome.set_text"],
        "antiflood": ["antiflood.toggle", "antiflood.set_limits", "antiflood.set_action"],
        "antispam": ["antispam.toggle"],
        "goodbye": ["goodbye.toggle", "goodbye.set_text"],
        "filter": ["filter.add_word", "filter.remove_word"],
    }

    def __init__(self):
        self._classifier = None
        self._extractor = None

    @property
    def classifier(self):
        if self._classifier is None:
            from app.nlp.intent_classifier import IntentClassifier
            self._classifier = IntentClassifier()
        return self._classifier

    @property
    def extractor(self):
        if self._extractor is None:
            from app.nlp.ner import EntityExtractor
            self._extractor = EntityExtractor()
        return self._extractor

    def map(self, text: str, intent: Optional[str] = None) -> ActionParseResult:
        if not text:
            return ActionParseResult(None, {}, 0.0, "empty_message")

        logger.info(f"Mapping text: {text}")
        intent = intent or self.classifier.classify(text)[0]

        if not intent:
            logger.debug(f"No intent found for: {text}")
            return ActionParseResult(None, {}, 0.0, "no_intent")

        mapping = self.ACTION_MAPPINGS.get(intent)
        if not mapping:
            logger.warning(f"No mapping for intent: {intent}")
            return ActionParseResult(None, {}, 0.0, f"no_mapping_{intent}")

        return self._execute_mapping(intent, mapping, text)

    def _execute_mapping(self, intent: str, mapping: Dict, text: str) -> ActionParseResult:
        text_lower = text.lower()

        if intent == "set_welcome":
            return self._map_welcome(text, mapping, text_lower)
        elif intent == "toggle_feature":
            return self._map_toggle_feature(text, mapping, text_lower)
        elif intent == "set_limit":
            return self._map_set_limit(text, mapping, text_lower)
        elif intent == "add_filter":
            return self._map_add_filter(text, mapping, text_lower)
        elif intent == "remove_filter":
            return self._map_remove_filter(text, mapping, text_lower)
        elif intent == "set_goodbye":
            return self._map_goodbye(text, mapping, text_lower)

        return ActionParseResult(None, {}, 0.0, f"unhandled_intent_{intent}")

    def _map_welcome(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        welcome_text = self._extract_welcome_text(text)
        if welcome_text:
            return ActionParseResult(
                action_id="welcome.set_text",
                payload={"text": welcome_text},
                confidence=0.85,
                reason="welcome_set_text",
            )

        if self._is_toggle_on(text_lower):
            return ActionParseResult(
                action_id="welcome.toggle",
                payload={"enabled": True},
                confidence=0.8,
                reason="welcome_toggle_on",
            )

        if self._is_toggle_off(text_lower):
            return ActionParseResult(
                action_id="welcome.toggle",
                payload={"enabled": False},
                confidence=0.8,
                reason="welcome_toggle_off",
            )

        if self._has_set_intent(text_lower):
            return ActionParseResult(
                action_id="welcome.toggle",
                payload={"enabled": True},
                confidence=0.6,
                reason="welcome_intent_no_text",
            )

        return ActionParseResult(
            action_id="welcome.toggle",
            payload={},
            confidence=0.5,
            reason="welcome_default",
        )

    def _map_toggle_feature(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        feature = self.classifier.detect_feature(text_lower)

        if not feature:
            return ActionParseResult(None, {}, 0.0, "feature_not_detected")

        is_on = self._is_toggle_on(text_lower)
        is_off = self._is_toggle_off(text_lower)

        if feature == "welcome":
            if is_off:
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": False},
                    confidence=0.85,
                    reason="welcome_toggle_off",
                )
            if is_on:
                welcome_text = self._extract_welcome_text(text)
                if welcome_text:
                    return ActionParseResult(
                        action_id="welcome.set_text",
                        payload={"text": welcome_text},
                        confidence=0.85,
                        reason="welcome_set_text",
                    )
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="welcome_toggle_on",
                )

        elif feature == "antiflood":
            limits = self.extractor.extract_limits(text)
            if limits:
                return ActionParseResult(
                    action_id="antiflood.set_limits",
                    payload=limits,
                    confidence=0.85,
                    reason="antiflood_set_limits",
                )

            action_match = re.search(r'\b(warn|mute|ban|kick|silenciar|expulsar)\b', text_lower)
            if action_match:
                return ActionParseResult(
                    action_id="antiflood.set_action",
                    payload={"action": action_match.group(1)},
                    confidence=0.75,
                    reason="antiflood_set_action",
                )

            if is_off:
                return ActionParseResult(
                    action_id="antiflood.toggle",
                    payload={"enabled": False},
                    confidence=0.85,
                    reason="antiflood_toggle_off",
                )
            if is_on:
                return ActionParseResult(
                    action_id="antiflood.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="antiflood_toggle_on",
                )

        elif feature == "antispam":
            if is_off:
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": False},
                    confidence=0.85,
                    reason="antispam_toggle_off",
                )
            if is_on:
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="antispam_toggle_on",
                )

        elif feature == "goodbye":
            goodbye_text = self._extract_goodbye_text(text)
            if goodbye_text:
                return ActionParseResult(
                    action_id="goodbye.set_text",
                    payload={"text": goodbye_text},
                    confidence=0.85,
                    reason="goodbye_set_text",
                )
            if is_off:
                return ActionParseResult(
                    action_id="goodbye.toggle",
                    payload={"enabled": False},
                    confidence=0.85,
                    reason="goodbye_toggle_off",
                )
            if is_on:
                return ActionParseResult(
                    action_id="goodbye.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="goodbye_toggle_on",
                )

        return ActionParseResult(None, {}, 0.0, f"toggle_feature_{feature}_unhandled")

    def _map_set_limit(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        limits = self.extractor.extract_limits(text)
        if limits:
            return ActionParseResult(
                action_id="antiflood.set_limits",
                payload=limits,
                confidence=0.85,
                reason="antiflood_set_limits",
            )

        if self._is_toggle_on(text_lower):
            return ActionParseResult(
                action_id="antiflood.toggle",
                payload={"enabled": True},
                confidence=0.8,
                reason="antiflood_toggle_on",
            )

        return ActionParseResult(
            action_id="antiflood.toggle",
            payload={},
            confidence=0.5,
            reason="set_limit_no_limits",
        )

    def _map_add_filter(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        word = self.extractor.extract_filter_word(text)
        if word:
            return ActionParseResult(
                action_id="filter.add_word",
                payload={"word": word},
                confidence=0.85,
                reason="filter_add_word",
            )

        return ActionParseResult(None, {}, 0.0, "filter_word_not_extracted")

    def _map_remove_filter(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        word = self.extractor.extract_filter_word(text)
        if word:
            return ActionParseResult(
                action_id="filter.remove_word",
                payload={"word": word},
                confidence=0.85,
                reason="filter_remove_word",
            )

        return ActionParseResult(None, {}, 0.0, "filter_word_not_extracted")

    def _map_goodbye(self, text: str, mapping: Dict, text_lower: str) -> ActionParseResult:
        goodbye_text = self._extract_goodbye_text(text)
        if goodbye_text:
            return ActionParseResult(
                action_id="goodbye.set_text",
                payload={"text": goodbye_text},
                confidence=0.85,
                reason="goodbye_set_text",
            )

        if self._is_toggle_on(text_lower):
            return ActionParseResult(
                action_id="goodbye.toggle",
                payload={"enabled": True},
                confidence=0.8,
                reason="goodbye_toggle_on",
            )

        if self._is_toggle_off(text_lower):
            return ActionParseResult(
                action_id="goodbye.toggle",
                payload={"enabled": False},
                confidence=0.8,
                reason="goodbye_toggle_off",
            )

        return ActionParseResult(
            action_id="goodbye.toggle",
            payload={},
            confidence=0.5,
            reason="goodbye_default",
        )

    def _extract_welcome_text(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:welcome|bienvenida)\s*:\s*(.+)',
            r'(?:bienvenida|welcome)\s+(?:con|with|establecer|set|definir)\s+(.+)',
            r'(?:activa|activar|pon|ponle)\s+(?:bienvenida|welcome)\s+(?:con|with)\s+(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_goodbye_text(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:despedida|goodbye)\s*:\s*(.+)',
            r'(?:despedida|goodbye)\s+(?:con|with|establecer|set|definir)\s+(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _is_toggle_on(self, text_lower: str) -> bool:
        toggle_on_words = ["activar", "activa", "on", "enable", "encender", "pon", "ponle", "ponlo"]
        for word in toggle_on_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return True
        return False

    def _is_toggle_off(self, text_lower: str) -> bool:
        toggle_off_words = ["desactivar", "desactiva", "off", "disable", "apagar", "quita", "quitar"]
        for word in toggle_off_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return True
        return False

    def _has_set_intent(self, text_lower: str) -> bool:
        set_words = ["cambiar", "cambia", "configurar", "configura", "establecer", "establece",
                    "definir", "define", "nuevo", "nueva", "crear", "crea", "poner", "pon",
                    "actualizar", "actualiza", "modificar", "modifica", "set", "change"]
        return any(word in text_lower for word in set_words)


_mapper_instance: Optional[ActionMapper] = None

def get_mapper() -> ActionMapper:
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = ActionMapper()
    return _mapper_instance

def map_to_action(text: str, intent: Optional[str] = None) -> ActionParseResult:
    return get_mapper().map(text, intent)

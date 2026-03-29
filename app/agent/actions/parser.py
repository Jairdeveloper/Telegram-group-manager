from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Any, Dict, Optional

from app.config.settings import load_api_settings
from app.nlp.normalizer import TextNormalizer, normalize_text, normalize_text_keep_numbers
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActionParseResult:
    action_id: Optional[str]
    payload: Dict[str, Any]
    confidence: float
    reason: str


_TOGGLE_ON = ("activar", "activa", "on", "enable", "encender", "pon", "ponle", "ponlo")
_TOGGLE_OFF = ("desactivar", "desactiva", "off", "disable", "apagar", "quita", "quitar")


def _contains_word(text: str, words: tuple) -> bool:
    """Check if text contains any of the words as whole words."""
    for word in words:
        if re.search(r'\b' + re.escape(word) + r'\b', text):
            return True
    return False


class ActionParser:
    def __init__(
        self,
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        normalizer: Optional[TextNormalizer] = None,
    ):
        settings = load_api_settings()
        self.llm_enabled = (
            settings.action_parser_llm_enabled if llm_enabled is None else llm_enabled
        )
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )
        self.normalizer = normalizer or TextNormalizer()

    def parse(self, message: str) -> ActionParseResult:
        original_message = message
        message = (message or "").strip()
        if not message:
            return ActionParseResult(None, {}, 0.0, "empty_message")

        logger.info(f"Parsing message: {original_message}")

        # PRIORITY: Try LLM first when enabled for better intent recognition
        if self.llm_enabled:
            llm_result = self._llm_parse(message)
            if llm_result:
                return llm_result

        # Fall back to rule-based parsing
        rule_based = self._rule_based(message)
        if rule_based:
            return rule_based

        return ActionParseResult(None, {}, 0.0, "no_match")

    def _rule_based(self, message: str) -> Optional[ActionParseResult]:
        normalized = self.normalizer.normalize(message)
        logger.debug(f"Normalized message: {normalized}")
        lowered = normalized.lower()

        if "bienvenida" in lowered or "welcome" in lowered:
            # INTENT DETECTION: Words that indicate user wants to SET a message (not provide text)
            intent_words = ("cambiar", "cambia", "configurar", "configura", "establecer", 
                           "establece", "definir", "define", "nuevo", "nueva", "crear", 
                           "crea", "poner", "pon", "actualizar", "actualiza", "modificar", 
                           "modifica", "set", "change", "configure", "create", "update")
            
            has_intent = any(word in lowered for word in intent_words)
            
            # If user is asking to SET a message but no clear text is provided,
            # return toggle ON with default text - let the LLM handle the actual text
            if has_intent:
                # Check if there's explicit text after colon or "con"
                if re.search(r"(?:welcome|bienvenida)\s*:\s*(.+)", message, re.IGNORECASE):
                    pass  # Has explicit text, continue to parse
                elif re.search(r"(?:welcome|bienvenida)\s+(?:con|with)\s+(.+)", lowered):
                    pass  # Has "con texto", continue
                else:
                    # No explicit text - return toggle ON to enable welcome
                    # The user wants to set up welcome but didn't provide the text
                    return ActionParseResult(
                        action_id="welcome.toggle",
                        payload={"enabled": True},
                        confidence=0.6,
                        reason="welcome_intent_no_text",
                    )

            # PRIORITY: Check for set_text patterns FIRST (before toggle)
            # Pattern: "bienvenida: texto" or "welcome: texto"
            match = re.search(r"(?:welcome|bienvenida)\s*:\s*(.+)", message, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                return ActionParseResult(
                    action_id="welcome.set_text",
                    payload={"text": text} if text else {},
                    confidence=0.85,
                    reason="welcome_set_text_colon",
                )
            
            # Pattern: "bienvenida con texto" or "welcome with texto"
            match = re.search(r"(?:welcome|bienvenida)\s+(?:con|with|establecer|set|definir)\s+(.+)", lowered)
            if match:
                text = match.group(1).strip()
                if text:
                    return ActionParseResult(
                        action_id="welcome.set_text",
                        payload={"text": text},
                        confidence=0.85,
                        reason="welcome_set_text_with",
                    )
            
            # Pattern: "activa bienvenida con texto"
            if _contains_word(lowered, _TOGGLE_ON) and ("con " in lowered or " with " in lowered):
                match = re.search(r"(?:activa|activar|pon|ponle)\s+(?:bienvenida|welcome)\s+(?:con|with)\s+(.+)", lowered)
                if match:
                    text = match.group(1).strip()
                    if text:
                        return ActionParseResult(
                            action_id="welcome.set_text",
                            payload={"text": text},
                            confidence=0.85,
                            reason="welcome_set_text_activate_with",
                        )
            
            # Then check for toggle OFF
            if _contains_word(lowered, _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="welcome_toggle_off",
                )
            
            # Then check for toggle ON (without text)
            if _contains_word(lowered, _TOGGLE_ON):
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="welcome_toggle_on",
                )
            if _contains_word(lowered, _TOGGLE_ON):
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="welcome_toggle_on",
                )
            match = re.search(r"(?:welcome|bienvenida)\s*:\s*(.+)", message, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                return ActionParseResult(
                    action_id="welcome.set_text",
                    payload={"text": text} if text else {},
                    confidence=0.75,
                    reason="welcome_set_text_colon",
                )
            # This fallback was too greedy - removed to prevent false matches
            # The patterns above should be sufficient for explicit text after "bienvenida:"

        if "antispam" in lowered or "anti spam" in lowered:
            if _contains_word(lowered, _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="antispam_toggle_off",
                )
            if _contains_word(lowered, _TOGGLE_ON):
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="antispam_toggle_on",
                )
            return ActionParseResult(
                action_id="antispam.toggle",
                payload={},
                confidence=0.5,
                reason="antispam_incomplete",
            )

        if "antiflood" in lowered or "anti flood" in lowered or "flood" in lowered:
            match = re.search(r"(\d+)\s*mensajes?\s*(?:en|por)\s*(\d+)\s*(?:segundos?|s)", lowered)
            if match:
                limit = int(match.group(1))
                interval = int(match.group(2))
                return ActionParseResult(
                    action_id="antiflood.set_limits",
                    payload={"limit": limit, "interval": interval},
                    confidence=0.85,
                    reason="antiflood_set_limits",
                )
            if any(word in lowered for word in ("warn", "mute", "ban", "kick", "silenciar", "expulsar")):
                for action in ("warn", "mute", "ban", "kick"):
                    if action in lowered:
                        return ActionParseResult(
                            action_id="antiflood.set_action",
                            payload={"action": action},
                            confidence=0.75,
                            reason="antiflood_set_action",
                        )
            if _contains_word(lowered, _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="antiflood.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="antiflood_toggle_off",
                )
            if _contains_word(lowered, _TOGGLE_ON):
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
                reason="antiflood_incomplete",
            )

        if "despedida" in lowered or "goodbye" in lowered:
            if _contains_word(lowered, _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="goodbye.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="goodbye_toggle_off",
                )
            if _contains_word(lowered, _TOGGLE_ON):
                return ActionParseResult(
                    action_id="goodbye.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="goodbye_toggle_on",
                )
            match = re.search(r"(?:despedida|goodbye)\s*:\s*(.+)", message, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                return ActionParseResult(
                    action_id="goodbye.set_text",
                    payload={"text": text} if text else {},
                    confidence=0.75,
                    reason="goodbye_set_text_colon",
                )

        if "bloquear" in lowered or "bloquea" in lowered:
            match = re.search(r"bloquear?\s+(?:palabra\s+)?(.+)", lowered)
            if match:
                word = match.group(1).strip()
                return ActionParseResult(
                    action_id="filter.add_word",
                    payload={"word": word},
                    confidence=0.8,
                    reason="filter_add_word",
                )
            match = re.search(r"bloquear?\s+palabra\s*:\s*(.+)", message, re.IGNORECASE)
            if match:
                word = match.group(1).strip()
                return ActionParseResult(
                    action_id="filter.add_word",
                    payload={"word": word},
                    confidence=0.8,
                    reason="filter_add_word_colon",
                )
        if any(word in lowered for word in ("elimina", "quitar", "borrar", "desbloquear", "desbloquea", "remover")):
            match = re.search(r"(?:elimina|quitar|borrar|desbloquear|desbloquea|remover)\s+(?:palabra\s+)?(.+)", lowered)
            if match:
                word = match.group(1).strip()
                return ActionParseResult(
                    action_id="filter.remove_word",
                    payload={"word": word},
                    confidence=0.8,
                    reason="filter_remove_word",
                )

        return None

    def _llm_parse(self, message: str) -> Optional[ActionParseResult]:
        actions_list = """Acciones disponibles:
- welcome.toggle: {enabled: bool} - Activar/desactivar mensaje de bienvenida
- welcome.set_text: {text: string} - Establecer texto de bienvenida
- welcome.set_creative_text: {} - Generar un mensaje de bienvenida creativo automáticamente
- antispam.toggle: {enabled: bool}
- antiflood.toggle: {enabled: bool}
- antiflood.set_limits: {limit: int, interval: int}
- antiflood.set_action: {action: "warn"|"mute"|"ban"|"kick"}
- goodbye.toggle: {enabled: bool}
- goodbye.set_text: {text: string}
- filter.add_word: {word: string}
- filter.remove_word: {word: string}"""
        
        examples = """Ejemplos:
- "Activa bienvenida" -> {"action_id": "welcome.toggle", "payload": {"enabled": true}}
- "Desactiva bienvenida" -> {"action_id": "welcome.toggle", "payload": {"enabled": false}}
- "Bienvenida: Hola equipo" -> {"action_id": "welcome.set_text", "payload": {"text": "Hola equipo"}}
- "Bienvenida con Bienvenido a nuestro grupo" -> {"action_id": "welcome.set_text", "payload": {"text": "Bienvenido a nuestro grupo"}}
- "Quiero cambiar el mensaje de bienvenida" -> {"action_id": "welcome.set_creative_text", "payload": {}}
- "Cambia la bienvenida usa tu creatividad" -> {"action_id": "welcome.set_creative_text", "payload": {}}
- "Pon un mensaje de bienvenida creativo" -> {"action_id": "welcome.set_creative_text", "payload": {}}
- "Desactiva antiflood" -> {"action_id": "antiflood.toggle", "payload": {"enabled": false}}
- "Pon antiflood con 10 mensajes en 5 segundos" -> {"action_id": "antiflood.set_limits", "payload": {"limit": 10, "interval": 5}}
- "Antiflood con mute" -> {"action_id": "antiflood.set_action", "payload": {"action": "mute"}}
- "despedida: Hasta luego" -> {"action_id": "goodbye.set_text", "payload": {"text": "Hasta luego"}}
- "Bloquear palabra spam" -> {"action_id": "filter.add_word", "payload": {"word": "spam"}}"""
        
        prompt = (
            f"{actions_list}\n\n"
            f"{examples}\n\n"
            f"Analiza el mensaje del usuario y determina la acción apropiada.\n"
            f"Si el usuario quiere cambiar/configurar la bienvenida pero NO especifica el texto, usa welcome.set_creative_text para generar un mensaje automáticamente.\n"
            f"Mensaje: {message}\n"
            f"Responde SOLO con JSON, sin texto adicional."
        )
        try:
            provider = LLMFactory.get_provider(self.llm_config)
            result = provider.generate(prompt)
        except LLMError:
            return None

        # Attempt to parse JSON from response
        try:
            import json

            data = json.loads(result)
            action_id = data.get("action_id")
            payload = data.get("payload") or {}
            if action_id:
                return ActionParseResult(
                    action_id=action_id,
                    payload=payload,
                    confidence=0.6,
                    reason="llm_parse",
                )
        except Exception:
            return None
        return None

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, Optional

from app.config.settings import load_api_settings
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


@dataclass(frozen=True)
class ActionParseResult:
    action_id: Optional[str]
    payload: Dict[str, Any]
    confidence: float
    reason: str


_TOGGLE_ON = ("activar", "activa", "on", "enable", "encender")
_TOGGLE_OFF = ("desactivar", "desactiva", "off", "disable", "apagar")


class ActionParser:
    def __init__(
        self,
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
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

    def parse(self, message: str) -> ActionParseResult:
        message = (message or "").strip()
        if not message:
            return ActionParseResult(None, {}, 0.0, "empty_message")

        rule_based = self._rule_based(message)
        if rule_based:
            return rule_based

        if self.llm_enabled:
            llm_result = self._llm_parse(message)
            if llm_result:
                return llm_result

        return ActionParseResult(None, {}, 0.0, "no_match")

    def _rule_based(self, message: str) -> Optional[ActionParseResult]:
        lowered = message.lower()

        if "bienvenida" in lowered or "welcome" in lowered:
            if any(word in lowered for word in _TOGGLE_ON):
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="welcome_toggle_on",
                )
            if any(word in lowered for word in _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="welcome.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="welcome_toggle_off",
                )
            if any(word in lowered for word in ("mensaje", "texto", "set", "establece", "definir")):
                match = re.search(r"(?:welcome|bienvenida)[:\\s]+(.+)", message, re.IGNORECASE)
                text = match.group(1).strip() if match else ""
                return ActionParseResult(
                    action_id="welcome.set_text",
                    payload={"text": text} if text else {},
                    confidence=0.7,
                    reason="welcome_set_text",
                )

        if "antispam" in lowered or "anti spam" in lowered:
            if any(word in lowered for word in _TOGGLE_ON):
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": True},
                    confidence=0.8,
                    reason="antispam_toggle_on",
                )
            if any(word in lowered for word in _TOGGLE_OFF):
                return ActionParseResult(
                    action_id="antispam.toggle",
                    payload={"enabled": False},
                    confidence=0.8,
                    reason="antispam_toggle_off",
                )
            return ActionParseResult(
                action_id="antispam.toggle",
                payload={},
                confidence=0.5,
                reason="antispam_incomplete",
            )

        return None

    def _llm_parse(self, message: str) -> Optional[ActionParseResult]:
        prompt = (
            "Extrae una accion y parametros en JSON. "
            "Responde solo con JSON con keys: action_id, payload.\n\n"
            f"Mensaje: {message}"
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

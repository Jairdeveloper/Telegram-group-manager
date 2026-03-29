import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class IntentMatch:
    intent: str
    confidence: float
    matched_keywords: List[str]


class IntentClassifier:
    INTENTS = {
        "set_welcome": {
            "description": "Establecer mensaje de bienvenida",
            "keywords": ["bienvenida", "welcome", "mensaje de entrada"],
            "action_keywords": ["cambiar", "cambia", "configurar", "configura", "establecer", 
                              "establece", "definir", "define", "nuevo", "nueva", "crear", 
                              "crea", "poner", "pon", "actualizar", "actualiza", "modificar", 
                              "modifica", "set", "change", "configure", "create", "update"],
        },
        "toggle_feature": {
            "description": "Activar/desactivar funcion",
            "keywords": ["bienvenida", "welcome", "antiflood", "antispam", "anti flood", 
                        "anti spam", "despedida", "goodbye", "flood", "spam"],
            "action_keywords": ["activar", "activa", "on", "enable", "encender", "pon", 
                               "ponle", "ponlo", "desactivar", "desactiva", "off", "disable", 
                               "apagar", "quita", "quitar"],
        },
        "set_limit": {
            "description": "Configurar limites",
            "keywords": ["limite", "limitar", "mensajes", "segundos", "flood", "antiflood"],
            "action_keywords": ["pon", "ponle", "poner", "configurar", "ajustar", "set", "limite", "limitar"],
        },
        "add_filter": {
            "description": "Agregar filtro",
            "keywords": ["bloquear", "bloquea", "bloqueo", "filtrar", "filtro", "spam", "palabra"],
            "action_keywords": ["bloquear", "bloquea", "agregar", "aniadir", "anade", "add"],
        },
        "remove_filter": {
            "description": "Quitar filtro",
            "keywords": ["eliminar", "elimina", "quitar", "borrar", "desbloquear", "desbloquea", "remover", "spam", "palabra", "filtro"],
            "action_keywords": ["eliminar", "elimina", "quitar", "borrar", "desbloquear", "desbloquea", "remover"],
        },
        "set_goodbye": {
            "description": "Establecer mensaje de despedida",
            "keywords": ["despedida", "goodbye", "mensaje de salida"],
            "action_keywords": ["cambiar", "cambia", "configurar", "establecer", "definir", 
                               "nuevo", "crear", "poner", "actualizar", "modificar"],
        },
        "get_status": {
            "description": "Consultar estado de funciones",
            "keywords": ["como esta", "como estan", "estado", "status", "esta activo", 
                        "estan activos", "esta enabled", "como funciona", "como va"],
            "action_keywords": ["ver", "consultar", "preguntar", "saber", "verificar", "check"],
        },
        "get_settings": {
            "description": "Ver configuracion actual",
            "keywords": ["configuracion", "settings", "opciones", "preferencias", "cuales son", 
                        "que tienes", "que tienes configurado", "ver configuracion"],
            "action_keywords": ["ver", "mostrar", "listar", "display"],
        },
        "help": {
            "description": "Pedir ayuda",
            "keywords": ["ayuda", "help", "comandos", "como usar", "como hago", "instrucciones",
                        "guia", "guia", "manual", "que puedo hacer", "que comandos"],
            "action_keywords": ["ayudame", "ayudarme", "dime", "explicalo", "explicame"],
        },
        "list_actions": {
            "description": "Listar acciones disponibles",
            "keywords": ["acciones", "funciones", "que puedes hacer", "que sabes hacer",
                        "que puedo pedirte", "que acciones"],
            "action_keywords": ["listar", "mostrar", "ver", "cuales"],
        },
    }

    FEATURE_KEYWORDS = {
        "welcome": ["bienvenida", "welcome"],
        "antiflood": ["antiflood", "anti flood", "flood"],
        "antispam": ["antispam", "anti spam", "spam"],
        "goodbye": ["despedida", "goodbye"],
        "filter": ["filtro", "bloqueo", "bloquear", "palabra"],
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        self._intent_patterns = {}
        for intent_name, intent_data in self.INTENTS.items():
            keywords = intent_data["keywords"] + intent_data["action_keywords"]
            pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
            self._intent_patterns[intent_name] = re.compile(pattern, re.IGNORECASE)

    def classify(self, text: str, normalized: bool = False) -> Tuple[Optional[str], float]:
        if not text:
            return None, 0.0

        text_lower = text.lower() if not normalized else text
        matches = []

        for intent_name, pattern in self._intent_patterns.items():
            found = pattern.findall(text_lower)
            if found:
                confidence = min(0.9, 0.5 + (len(found) * 0.15))
                matches.append(IntentMatch(intent=intent_name, confidence=confidence, matched_keywords=found))
                logger.debug(f"Intent '{intent_name}' matched with confidence {confidence}: {found}")

        if not matches:
            logger.debug(f"No intent matched for: {text}")
            return None, 0.0

        best_match = max(matches, key=lambda m: m.confidence)
        logger.info(f"Classified intent: {best_match.intent} (confidence: {best_match.confidence})")
        
        return best_match.intent, best_match.confidence

    def classify_with_details(self, text: str, normalized: bool = False) -> List[IntentMatch]:
        if not text:
            return []

        text_lower = text.lower() if not normalized else text
        matches = []

        for intent_name, pattern in self._intent_patterns.items():
            found = pattern.findall(text_lower)
            if found:
                confidence = min(0.9, 0.5 + (len(found) * 0.15))
                matches.append(IntentMatch(intent=intent_name, confidence=confidence, matched_keywords=found))

        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches

    def detect_feature(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    logger.debug(f"Detected feature: {feature}")
                    return feature
        return None

    def is_toggle_on(self, text: str) -> bool:
        toggle_on_words = ["activar", "activa", "on", "enable", "encender", "pon", "ponle", "ponlo"]
        text_lower = text.lower()
        for word in toggle_on_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return True
        return False

    def is_toggle_off(self, text: str) -> bool:
        toggle_off_words = ["desactivar", "desactiva", "off", "disable", "apagar", "quita", "quitar"]
        text_lower = text.lower()
        for word in toggle_off_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return True
        return False

    def extract_action_verb(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for intent_name, intent_data in self.INTENTS.items():
            for keyword in intent_data["action_keywords"]:
                if keyword in text_lower:
                    return keyword
        return None


_classifier_instance: Optional[IntentClassifier] = None
_classify_cache: dict = {}


def get_classifier() -> IntentClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance


def classify_intent(text: str) -> Tuple[Optional[str], float]:
    cache_key = text.strip().lower()
    if cache_key in _classify_cache:
        return _classify_cache[cache_key]
    
    result = get_classifier().classify(text)
    
    if len(_classify_cache) < 1000:
        _classify_cache[cache_key] = result
    
    return result


def clear_classify_cache() -> None:
    global _classify_cache
    _classify_cache = {}

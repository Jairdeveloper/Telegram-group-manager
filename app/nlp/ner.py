import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    value: str
    label: str
    start: int
    end: int


class EntityExtractor:
    ENTITY_TYPES = {
        "ACTION_TYPE": ["bienvenida", "welcome", "antiflood", "anti flood", "antispam", "anti spam", 
                       "despedida", "goodbye", "flood", "spam", "filtro"],
        "SETTING_VALUE": ["on", "off", "enable", "disable", "activar", "desactivar"],
        "MODIFIER": ["cambiar", "activar", "desactivar", "encender", "apagar", "bloquear", 
                    "quitar", "eliminar", "pon", "configurar", "set", "change"],
        "NUMBER": [r'\d+'],
        "TIME_UNIT": ["segundo", "segundos", "minuto", "minutos", "hora", "horas"],
    }

    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy
        self._nlp = None
        if use_spacy:
            self._load_spacy()

    def _load_spacy(self) -> None:
        try:
            import spacy
            self._nlp = spacy.load("es_core_news_sm")
            logger.info("spaCy NER loaded")
        except (ImportError, OSError) as e:
            logger.warning(f"spaCy not available: {e}")
            self._nlp = None

    def extract(self, text: str) -> List[Entity]:
        if not text:
            return []

        entities = []
        
        if self._nlp is not None:
            entities.extend(self._extract_spacy(text))
        
        entities.extend(self._extract_custom_entities(text))
        
        entities = self._deduplicate_entities(entities)
        
        logger.debug(f"Extracted entities: {[e.value for e in entities]}")
        return entities

    def _extract_spacy(self, text: str) -> List[Entity]:
        entities = []
        doc = self._nlp(text)
        for ent in doc.ents:
            entities.append(Entity(
                value=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            ))
        return entities

    def _extract_custom_entities(self, text: str) -> List[Entity]:
        entities = []
        text_lower = text.lower()

        for entity_type, patterns in self.ENTITY_TYPES.items():
            for pattern in patterns:
                if pattern.startswith('r'):
                    matches = re.finditer(pattern[1:], text, re.IGNORECASE)
                    for match in matches:
                        entities.append(Entity(
                            value=match.group(),
                            label=entity_type,
                            start=match.start(),
                            end=match.end()
                        ))
                else:
                    pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                    matches = re.finditer(pattern_regex, text_lower)
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        if not any(e.start == start and e.end == end for e in entities):
                            entities.append(Entity(
                                value=text[start:end],
                                label=entity_type,
                                start=start,
                                end=end
                            ))

        return entities

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        seen = set()
        unique = []
        for e in entities:
            key = (e.value.lower(), e.label)
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique

    def extract_numbers(self, text: str) -> List[int]:
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]

    def extract_action_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        action_types = {
            "welcome": ["bienvenida", "welcome"],
            "antiflood": ["antiflood", "anti flood", "flood"],
            "antispam": ["antispam", "anti spam"],
            "goodbye": ["despedida", "goodbye"],
            "filter": ["bloquear", "filtro", "bloqueo"],
        }
        for action_type, keywords in action_types.items():
            if any(kw in text_lower for kw in keywords):
                return action_type
        return None

    def extract_filter_word(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        patterns = [
            r'bloquear?\s+(?:palabra\s+)?(.+)',
            r'bloquea\s+(?:palabra\s+)?(.+)',
            r'borrar\s+(?:palabra\s+)?(.+)',
            r'eliminar\s+(?:palabra\s+)?(.+)',
            r'desbloquear?\s+(?:palabra\s+)?(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(1).strip()
                stop_words = ['con', 'para', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']
                word = ' '.join(w for w in word.split() if w not in stop_words)
                return word
        return None

    def extract_limits(self, text: str) -> Optional[Dict[str, int]]:
        pattern = r'(\d+)\s*mensajes?\s*(?:en|por|cada)\s*(\d+)\s*(segundos?|s|minutos?|m|horas?|h)?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            limit = int(match.group(1))
            interval = int(match.group(2))
            unit = match.group(3) or 'segundos'
            if unit and unit.lower().startswith(('min', 'm')):
                interval *= 60
            elif unit and unit.lower().startswith(('h', 'hor')):
                interval *= 3600
            return {"limit": limit, "interval": interval}
        return None

    def extract_welcome_text(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:bienvenida|welcome)\s*:\s*(.+)',
            r'(?:bienvenida|welcome)\s+(?:con|with|establecer|set|definir)\s+(.+)',
            r'activa\s+(?:bienvenida|welcome)\s+(?:con|with)\s+(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                text_value = match.group(1).strip()
                if text_value:
                    return text_value
        return None


_extractor_instance: Optional[EntityExtractor] = None

def get_extractor(use_spacy: bool = True) -> EntityExtractor:
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = EntityExtractor(use_spacy)
    return _extractor_instance

def extract_entities(text: str) -> List[Entity]:
    return get_extractor().extract(text)

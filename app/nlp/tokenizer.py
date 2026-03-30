import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

_SPACY_MODELS_CACHE: Dict[str, Any] = {}
_CACHE_LOCK = threading.Lock()


@dataclass
class TokenizationResult:
    """Resultado completo del tokenization con análisis lingüístico"""
    tokens: List[str]
    pos_tags: List[Tuple[str, str]]
    lemmas: List[str]
    text: str
    deps: List[Tuple[str, str]] = field(default_factory=list)  # (token, dependency_label)
    intent_hint: Optional[str] = None  # Early intent detection
    
    def get_nouns(self) -> List[str]:
        """Retorna tokens que son sustantivos"""
        return [token for token, pos in self.pos_tags if pos == "NOUN"]
    
    def get_verbs(self) -> List[str]:
        """Retorna tokens que son verbos"""
        return [token for token, pos in self.pos_tags if pos == "VERB"]
    
    def get_adjectives(self) -> List[str]:
        """Retorna tokens que son adjetivos"""
        return [token for token, pos in self.pos_tags if pos == "ADJ"]
    
    def get_lemmas_for_nouns(self) -> List[str]:
        """Retorna lemmas solo de sustantivos (NEW in T1.2)"""
        noun_indices = [i for i, (_, pos) in enumerate(self.pos_tags) if pos == "NOUN"]
        return [self.lemmas[i] for i in noun_indices if i < len(self.lemmas)]
    
    def get_dependencies(self) -> List[str]:
        """Retorna lista de etiquetas de dependencias sintácticas (NEW in T1.2)"""
        return [dep for _, dep in self.deps]
    
    def has_word(self, word: str) -> bool:
        """Chequea si palabra está en tokens (case-insensitive)"""
        return word.lower() in [t.lower() for t in self.tokens]
    
    def has_lemma(self, lemma: str) -> bool:
        """Chequea si lemma está en lemmas (case-insensitive) (NEW in T1.2)"""
        return lemma.lower() in [l.lower() for l in self.lemmas]


class NLPTokenizer:
    def __init__(self, model_name: str = "es_core_news_sm", use_cache: bool = True):
        self.model_name = model_name
        self._nlp = None
        self.use_cache = use_cache
        self._ensure_model_loaded()
    
    def _ensure_model_loaded(self) -> None:
        if self._nlp is not None:
            return
        
        if self.use_cache:
            with _CACHE_LOCK:
                if self.model_name in _SPACY_MODELS_CACHE:
                    self._nlp = _SPACY_MODELS_CACHE[self.model_name]
                    logger.debug(f"Using cached spaCy model: {self.model_name}")
                    return
        
        self._load_model()
        
        if self.use_cache and self._nlp is not None:
            with _CACHE_LOCK:
                _SPACY_MODELS_CACHE[self.model_name] = self._nlp
                logger.info(f"Cached spaCy model: {self.model_name}")
    
    def _load_model(self) -> None:
        try:
            import spacy
            self._nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except ImportError:
            logger.warning("spaCy not installed, tokenization will use fallback")
            self._nlp = None
        except OSError:
            logger.warning(f"Model {self.model_name} not found, using fallback")
            self._nlp = None
    
    def tokenize(self, text: str) -> TokenizationResult:
        """Tokeniza texto con análisis lingüístico completo (T1.2 enhanced)"""
        if not text or not text.strip():
            return TokenizationResult(
                tokens=[],
                pos_tags=[],
                lemmas=[],
                deps=[],
                text=text,
                intent_hint=None
            )
        
        logger.debug(f"Tokenizing text: {text}")
        
        self._ensure_model_loaded()
        
        if self._nlp is not None:
            return self._tokenize_spacy(text)
        return self._tokenize_fallback(text)
    
    def _tokenize_spacy(self, text: str) -> TokenizationResult:
        """Tokenización con spaCy - incluye lemmas, POS, deps e intent hints (T1.2)"""
        doc = self._nlp(text)
        
        tokens = [token.text for token in doc]
        pos_tags = [(token.text, token.pos_) for token in doc]
        lemmas = [token.lemma_ for token in doc]
        
        # Extraer dependencias sintácticas (NEW in T1.2)
        deps = [(token.text, token.dep_) for token in doc]
        
        # Detectar intent hints tempranos basado en lemmas (NEW in T1.2)
        intent_hint = self._detect_intent_hint(lemmas)
        
        logger.debug(f"Tokens: {tokens}")
        logger.debug(f"POS tags: {pos_tags}")
        logger.debug(f"Lemmas: {lemmas}")
        logger.debug(f"Dependencies: {deps}")
        if intent_hint:
            logger.debug(f"Intent hint detected: {intent_hint}")
        
        return TokenizationResult(
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            deps=deps,
            text=text,
            intent_hint=intent_hint
        )
    
    def _tokenize_fallback(self, text: str) -> TokenizationResult:
        """Tokenización fallback cuando spaCy no está disponible (T1.2 compatible)"""
        tokens = text.split()
        pos_tags = [(token, "X") for token in tokens]
        lemmas = tokens  # Sin spaCy, lemmas = tokens
        deps = [(token, "UNK") for token in tokens]  # Dependencies unknown
        
        # Intentos hints con fallback
        intent_hint = self._detect_intent_hint(lemmas)
        
        logger.debug(f"Fallback tokens: {tokens}")
        logger.debug(f"Fallback deps: {deps}")
        
        return TokenizationResult(
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            deps=deps,
            text=text,
            intent_hint=intent_hint
        )
    
    def _detect_intent_hint(self, lemmas: List[str]) -> Optional[str]:
        """Detecta intent hints tempranos basado en lemmas (NEW in T1.2)"""
        hint_keywords = {
            "set_welcome": ["cambiar", "configurar", "establecer", "definir", "bienvenida", "welcome"],
            "set_goodbye": ["despedida", "adiós", "adios", "salida", "goodbye"],
            "toggle_feature": ["activar", "desactivar", "encender", "apagar", "on", "off", "enable", "disable"],
            "add_filter": ["bloquear", "filtrar", "agregar", "añadir", "add", "block"],
            "remove_filter": ["eliminar", "quitar", "desbloquear", "remover", "remove", "delete"],
            "get_status": ["estado", "cómo", "como", "status", "how", "check"],
            "get_settings": ["configuración", "settings", "opciones", "preferences"],
        }
        
        lemmas_lower = [l.lower() for l in lemmas]
        
        for intent, keywords in hint_keywords.items():
            if any(kw in lemmas_lower for kw in keywords):
                logger.debug(f"Intent hint '{intent}' detected from lemmas")
                return intent
        
        return None
    
    def analyze(self, text: str) -> Dict:
        """Análisis completo del texto (T1.2 enhanced)"""
        result = self.tokenize(text)
        return {
            "text": text,
            "tokens": result.tokens,
            "pos_tags": result.pos_tags,
            "lemmas": result.lemmas,
            "deps": result.deps,
            "intent_hint": result.intent_hint,
            "noun_count": len(result.get_nouns()),
            "verb_count": len(result.get_verbs()),
            "adj_count": len(result.get_adjectives()),
            "nouns": result.get_nouns(),
            "verbs": result.get_verbs(),
            "noun_lemmas": result.get_lemmas_for_nouns(),
            "dependencies": result.get_dependencies(),
        }


_tokenizer_instance: Optional[NLPTokenizer] = None

def get_tokenizer(model_name: str = "es_core_news_sm") -> NLPTokenizer:
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = NLPTokenizer(model_name)
    return _tokenizer_instance

def tokenize_text(text: str) -> TokenizationResult:
    return get_tokenizer().tokenize(text)

def clear_spacy_cache() -> None:
    """Limpia el cache de modelos spaCy"""
    global _SPACY_MODELS_CACHE
    with _CACHE_LOCK:
        _SPACY_MODELS_CACHE.clear()
    logger.info("spaCy models cache cleared")

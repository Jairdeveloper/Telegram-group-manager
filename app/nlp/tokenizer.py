import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TokenizationResult:
    tokens: List[str]
    pos_tags: List[Tuple[str, str]]
    lemmas: List[str]
    text: str
    
    def get_nouns(self) -> List[str]:
        return [token for token, pos in self.pos_tags if pos == "NOUN"]
    
    def get_verbs(self) -> List[str]:
        return [token for token, pos in self.pos_tags if pos == "VERB"]
    
    def get_adjectives(self) -> List[str]:
        return [token for token, pos in self.pos_tags if pos == "ADJ"]
    
    def has_word(self, word: str) -> bool:
        return word.lower() in [t.lower() for t in self.tokens]


class NLPTokenizer:
    def __init__(self, model_name: str = "es_core_news_sm"):
        self.model_name = model_name
        self._nlp = None
        self._load_model()
    
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
        if not text:
            return TokenizationResult(tokens=[], pos_tags=[], lemmas=[], text="")
        
        logger.debug(f"Tokenizing text: {text}")
        
        if self._nlp is not None:
            return self._tokenize_spacy(text)
        return self._tokenize_fallback(text)
    
    def _tokenize_spacy(self, text: str) -> TokenizationResult:
        doc = self._nlp(text)
        
        tokens = [token.text for token in doc]
        pos_tags = [(token.text, token.pos_) for token in doc]
        lemmas = [token.lemma_ for token in doc]
        
        logger.debug(f"Tokens: {tokens}")
        logger.debug(f"POS tags: {pos_tags}")
        logger.debug(f"Lemmas: {lemmas}")
        
        return TokenizationResult(
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            text=text
        )
    
    def _tokenize_fallback(self, text: str) -> TokenizationResult:
        tokens = text.split()
        pos_tags = [(token, "X") for token in tokens]
        lemmas = tokens
        
        logger.debug(f"Fallback tokens: {tokens}")
        
        return TokenizationResult(
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            text=text
        )
    
    def analyze(self, text: str) -> Dict:
        result = self.tokenize(text)
        return {
            "text": text,
            "tokens": result.tokens,
            "pos_tags": result.pos_tags,
            "lemmas": result.lemmas,
            "noun_count": len(result.get_nouns()),
            "verb_count": len(result.get_verbs()),
            "adj_count": len(result.get_adjectives()),
        }


_tokenizer_instance: Optional[NLPTokenizer] = None

def get_tokenizer(model_name: str = "es_core_news_sm") -> NLPTokenizer:
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = NLPTokenizer(model_name)
    return _tokenizer_instance

def tokenize_text(text: str) -> TokenizationResult:
    return get_tokenizer().tokenize(text)

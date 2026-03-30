import logging
import re
import unicodedata
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TextNormalizer:
    def __init__(self, lowercase: bool = True, remove_numbers: bool = True, remove_punctuation: bool = True):
        self.lowercase = lowercase
        self.remove_numbers = remove_numbers
        self.remove_punctuation = remove_punctuation
        
    def normalize(self, text: str) -> str:
        if not text:
            return ""
        
        original_text = text
        logger.debug(f"Normalizing text: {original_text}")
        
        if self.lowercase:
            text = text.lower()
            
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
            
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
            
        text = ' '.join(text.split())
        
        logger.debug(f"Normalized text: {text}")
        return text
    
    def normalize_keep_numbers(self, text: str) -> str:
        if not text:
            return ""
        
        original_text = text
        logger.debug(f"Normalizing text (keep numbers): {original_text}")
        
        if self.lowercase:
            text = text.lower()
            
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
            
        text = ' '.join(text.split())
        
        logger.debug(f"Normalized text: {text}")
        return text
    
    def normalize_preserve_case(self, text: str) -> str:
        if not text:
            return ""
        
        original_text = text
        logger.debug(f"Normalizing text (preserve case): {original_text}")
        
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
            
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
            
        text = ' '.join(text.split())
        
        logger.debug(f"Normalized text: {text}")
        return text


_normalizer_instance: Optional[TextNormalizer] = None

def get_normalizer() -> TextNormalizer:
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = TextNormalizer()
    return _normalizer_instance

def normalize_text(text: str) -> str:
    return get_normalizer().normalize(text)

def normalize_text_keep_numbers(text: str) -> str:
    return get_normalizer().normalize_keep_numbers(text)


class EnhancedTextNormalizer:
    """Normalización mejorada para texto español"""
    
    CONTRACTIONS: Dict[str, str] = {
        "p'al": "para el",
        "pal": "para el",
        "d'elas": "de elas",
        "n'est": "no est",
        "tá": "está",
        "q'el": "que el",
        "del": "de el",
        "al": "a el",
    }
    
    TYPOS: Dict[str, str] = {
        "porfa": "por favor",
        "porfis": "por favor",
        "pq": "porque",
        "xq": "porque",
        "ke": "que",
        "k": "que",
        "tb": "también",
        "tmb": "también",
        "vc": "vos",
        "uds": "ustedes",
        "u": "you",
        "q": "que",
    }
    
    WHITESPACE_PATTERN = re.compile(r'\s+')
    
    DIACRITICS_MAP: Dict[str, str] = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I',
        'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
    }
    
    def __init__(self, keep_diacritics: bool = True):
        """
        Args:
            keep_diacritics: Si False, remueve acentos (útil para búsqueda)
        """
        self.keep_diacritics = keep_diacritics
    
    def normalize(self, text: str) -> str:
        """Pipeline completo de normalización"""
        if not text:
            return text
        
        text = self._expand_contractions(text)
        text = self._fix_typos(text)
        
        if not self.keep_diacritics:
            text = self._remove_diacritics(text)
        
        text = self._normalize_whitespace(text)
        text = self._normalize_case(text)
        
        return text.strip()
    
    def _expand_contractions(self, text: str) -> str:
        """Expande contracciones españolas"""
        for contraction, expansion in self.CONTRACTIONS.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        return text
    
    def _fix_typos(self, text: str) -> str:
        """Corrige typos y variaciones comunes"""
        for typo, correct in self.TYPOS.items():
            pattern = r'\b' + re.escape(typo) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        return text
    
    def _remove_diacritics(self, text: str) -> str:
        """Remueve acentos y diacríticos"""
        result = []
        for char in text:
            if char in self.DIACRITICS_MAP:
                result.append(self.DIACRITICS_MAP[char])
            else:
                normalized = unicodedata.normalize('NFD', char)
                if len(normalized) == 1 or unicodedata.category(normalized[0]) != 'Mn':
                    result.append(char)
                else:
                    result.append(normalized[0] if len(normalized) > 0 else char)
        return ''.join(result)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espacios múltiples"""
        text = self.WHITESPACE_PATTERN.sub(' ', text)
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\t+', ' ', text)
        return text
    
    def _normalize_case(self, text: str) -> str:
        """Normaliza mayúsculas de forma inteligente"""
        words = text.split()
        result = []
        
        for word in words:
            if word.isupper() and len(word) > 2:
                result.append(word)
            else:
                result.append(word.lower())
        
        return ' '.join(result)


_enhanced_normalizer_instance: Optional[EnhancedTextNormalizer] = None

def get_enhanced_normalizer() -> EnhancedTextNormalizer:
    global _enhanced_normalizer_instance
    if _enhanced_normalizer_instance is None:
        _enhanced_normalizer_instance = EnhancedTextNormalizer()
    return _enhanced_normalizer_instance

def normalize_text_enhanced(text: str, keep_diacritics: bool = True) -> str:
    """Normalización mejorada para texto en español"""
    normalizer = EnhancedTextNormalizer(keep_diacritics=keep_diacritics)
    return normalizer.normalize(text)

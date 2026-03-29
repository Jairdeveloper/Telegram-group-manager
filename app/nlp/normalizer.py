import logging
import re
from typing import Optional

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

import pytest
from app.nlp.normalizer import EnhancedTextNormalizer, TextNormalizer


class TestEnhancedTextNormalizer:
    """Tests para EnhancedTextNormalizer - Tarea T1.1"""
    
    def test_expand_contractions(self):
        """Test expansión de contracciones españolas"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("p'al kitchen") == "para el kitchen"
        assert normalizer.normalize("Dame p'al sistema") == "dame para el sistema"
        assert normalizer.normalize("n'est aquí") == "no est aquí"
        assert normalizer.normalize("tá") == "está"
        assert normalizer.normalize("del libro") == "de el libro"
        assert normalizer.normalize("al usuario") == "a el usuario"
    
    def test_expand_contractions_case_insensitive(self):
        """Test expansión de contracciones con mayúsculas"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("P'AL") == "para el"
        assert normalizer.normalize("TÁ") == "está"
    
    def test_remove_diacritics(self):
        """Test eliminación de diacríticos"""
        normalizer = EnhancedTextNormalizer(keep_diacritics=False)
        
        assert normalizer.normalize("Hola, ¿cómo estás?") == "hola, ¿como estas?"
        assert normalizer.normalize("Niño") == "nino"
        assert normalizer.normalize("Árbol") == "arbol"
        assert normalizer.normalize("Éxito") == "exito"
        assert normalizer.normalize("¿Por qué?") == "¿por que?"
    
    def test_keep_diacritics(self):
        """Test preservación de diacríticos por defecto"""
        normalizer = EnhancedTextNormalizer(keep_diacritics=True)
        
        assert normalizer.normalize("Hola, ¿cómo estás?") == "hola, ¿cómo estás?"
        assert normalizer.normalize("Niño") == "niño"
    
    def test_normalize_whitespace(self):
        """Test normalización de espacios"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("Hola   mundo") == "hola mundo"
        assert normalizer.normalize("Hola\n\ntest") == "hola test"
        assert normalizer.normalize("Hola\ttest") == "hola test"
        assert normalizer.normalize("  Hola   mundo  ") == "hola mundo"
    
    def test_typo_correction(self):
        """Test corrección de typos comunes"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("porfa ayuda") == "por favor ayuda"
        assert normalizer.normalize("porfis") == "por favor"
        assert normalizer.normalize("pq") == "porque"
        assert normalizer.normalize("xq") == "porque"
        assert normalizer.normalize("ke") == "que"
        assert normalizer.normalize("tb") == "también"
        assert normalizer.normalize("tmb") == "también"
    
    def test_typo_correction_case_insensitive(self):
        """Test corrección de typos con mayúsculas"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("PORFA") == "por favor"
        assert normalizer.normalize("PQ") == "porque"
    
    def test_normalize_case(self):
        """Test normalización de mayúsculas"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("Hola Mundo") == "hola mundo"
        assert normalizer.normalize("DNI") == "DNI"
        assert normalizer.normalize("mi palabra API") == "mi palabra API"
    
    def test_full_pipeline(self):
        """Test pipeline completo de normalización"""
        normalizer = EnhancedTextNormalizer(keep_diacritics=False)
        
        result = normalizer.normalize("P'al niño,\n\n¿cómo tá? porfa")
        assert result == "para el nino, ¿como esta? por favor"
    
    def test_empty_text(self):
        """Test con texto vacío"""
        normalizer = EnhancedTextNormalizer()
        
        assert normalizer.normalize("") == ""
        assert normalizer.normalize("   ") == ""
    
    def test_get_enhanced_normalizer_singleton(self):
        """Test singleton pattern"""
        from app.nlp.normalizer import get_enhanced_normalizer
        
        norm1 = get_enhanced_normalizer()
        norm2 = get_enhanced_normalizer()
        
        assert norm1 is norm2
    
    def test_normalize_text_enhanced_function(self):
        """Test función de conveniencia"""
        from app.nlp.normalizer import normalize_text_enhanced
        
        result = normalize_text_enhanced("Hola mundo")
        assert result == "hola mundo"
        
        result = normalize_text_enhanced("Niño", keep_diacritics=False)
        assert result == "nino"


class TestTextNormalizer:
    """Tests para TextNormalizer (backward compatibility)"""
    
    def test_basic_normalization(self):
        """Test normalización básica"""
        normalizer = TextNormalizer()
        
        assert normalizer.normalize("Hola MUNDO") == "hola mundo"
        assert normalizer.normalize("Hola  Mundo") == "hola mundo"
    
    def test_remove_numbers(self):
        """Test eliminación de números"""
        normalizer = TextNormalizer()
        
        assert normalizer.normalize("Tengo 2 gatos") == "tengo gatos"
    
    def test_remove_punctuation(self):
        """Test eliminación de puntuación"""
        normalizer = TextNormalizer()
        
        assert normalizer.normalize("¡Hola! ¿Cómo estás?") == "hola cómo estás"
    
    def test_preserve_numbers(self):
        """Test preservación de números"""
        normalizer = TextNormalizer()
        
        assert normalizer.normalize_keep_numbers("Tengo 2 gatos") == "tengo 2 gatos"
    
    def test_preserve_case(self):
        """Test preservación de mayúsculas"""
        normalizer = TextNormalizer()
        
        assert normalizer.normalize_preserve_case("Hola MUNDO") == "Hola MUNDO"
    
    def test_get_normalizer_singleton(self):
        """Test singleton"""
        from app.nlp.normalizer import get_normalizer
        
        norm1 = get_normalizer()
        norm2 = get_normalizer()
        
        assert norm1 is norm2

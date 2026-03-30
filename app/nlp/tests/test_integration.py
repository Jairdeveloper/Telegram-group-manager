"""Tests de integración para NLP Pipeline - Tarea T1.6"""

import pytest
from app.nlp.normalizer import EnhancedTextNormalizer
from app.nlp.tokenizer import NLPTokenizer, tokenize_text


class TestNormalizationIntegration:
    """Tests de integración para normalización"""
    
    def test_normalize_then_tokenize(self):
        """Test pipeline completo: normalizar luego tokenizar"""
        normalizer = EnhancedTextNormalizer()
        tokenizer = NLPTokenizer(use_cache=False)
        
        text = "P'al sistema, porfa cambia el mensaje"
        normalized = normalizer.normalize(text)
        result = tokenizer.tokenize(normalized)
        
        assert result.tokens
        assert result.pos_tags
        assert result.lemmas
    
    def test_normalize_keep_diacritics(self):
        """Test normalización preservando diacríticos"""
        normalizer = EnhancedTextNormalizer(keep_diacritics=True)
        tokenizer = NLPTokenizer(use_cache=False)
        
        text = "¿Cómo estás?"
        normalized = normalizer.normalize(text)
        result = tokenizer.tokenize(normalized)
        
        assert "cómo" in [t.lower() for t in result.tokens]
    
    def test_normalize_remove_diacritics(self):
        """Test normalización removiendo diacríticos"""
        normalizer = EnhancedTextNormalizer(keep_diacritics=False)
        tokenizer = NLPTokenizer(use_cache=False)
        
        text = "¿Cómo estás?"
        normalized = normalizer.normalize(text)
        result = tokenizer.tokenize(normalized)
        
        assert "como" in [t.lower() for t in result.tokens]
    
    def test_contractions_pipeline(self):
        """Test expansión de contracciones en pipeline"""
        normalizer = EnhancedTextNormalizer()
        tokenizer = NLPTokenizer(use_cache=False)
        
        text = "p'al kitchen"
        normalized = normalizer.normalize(text)
        result = tokenizer.tokenize(normalized)
        
        assert "para" in [t.lower() for t in result.tokens]
        assert "el" in [t.lower() for t in result.tokens]


class TestTokenizationIntegration:
    """Tests de integración para tokenización"""
    
    def test_full_pipeline(self):
        """Test pipeline completo de NLP"""
        result = tokenize_text("Cambiar mensaje de bienvenida")
        
        assert result.tokens
        assert result.pos_tags
        assert result.lemmas
        assert result.deps
        assert result.intent_hint is not None
    
    def test_intent_classification_pipeline(self):
        """Test detección de intents"""
        test_cases = [
            ("Cambiar bienvenida", "set_welcome"),
            ("Bloquear palabra", "add_filter"),
            ("Eliminar filtro", "remove_filter"),
            ("Activar antiflood", "toggle_feature"),
            ("Estado del sistema", "get_status"),
        ]
        
        for text, expected_intent in test_cases:
            result = tokenize_text(text)
            assert result.intent_hint == expected_intent, f"Failed for: {text}"
    
    def test_entity_extraction_pipeline(self):
        """Test extracción de entidades (nouns)"""
        result = tokenize_text("Cambiar mensaje de bienvenida")
        
        nouns = result.get_nouns()
        assert len(nouns) >= 2
        assert "mensaje" in [n.lower() for n in nouns]
    
    def test_lemma_based_matching(self):
        """Test matching basado en lemmas"""
        result = tokenize_text("Los niños están corriendo")
        
        assert result.has_lemma("niño")
        assert result.has_lemma("correr")
        assert result.has_lemma("estar")
    
    def test_dependency_based_understanding(self):
        """Test comprensión basada en dependencias"""
        result = tokenize_text("Cambiar mensaje")
        
        deps = result.get_dependencies()
        assert len(deps) > 0


class TestEndToEndScenarios:
    """Tests de escenarios end-to-end"""
    
    def test_welcome_message_flow(self):
        """Test flujo para cambiar mensaje de bienvenida"""
        text = "Cambiar mensaje de bienvenida"
        
        result = tokenize_text(text)
        
        assert result.intent_hint == "set_welcome"
        assert result.has_lemma("bienvenida")
        assert result.has_lemma("cambiar")
    
    def test_filter_management_flow(self):
        """Test flujo para gestionar filtros"""
        texts = [
            "Bloquear palabra grosera",
            "Agregar filtro de spam",
            "Eliminar palabra bloqueada",
        ]
        
        intents = ["add_filter", "add_filter", "remove_filter"]
        
        for text, expected in zip(texts, intents):
            result = tokenize_text(text)
            assert result.intent_hint == expected
    
    def test_status_check_flow(self):
        """Test flujo para consultar estado"""
        texts = [
            "¿Cuál es el estado?",
            "Cómo estás el sistema",
            "Dime el status del antiflood",
        ]
        
        for text in texts:
            result = tokenize_text(text)
            assert result.intent_hint == "get_status"
    
    def test_toggle_feature_flow(self):
        """Test flujo para activar/desactivar features"""
        texts = [
            "Activar antiflood",
            "Desactivar logs",
            "Apagar modo debug",
        ]
        
        for text in texts:
            result = tokenize_text(text)
            assert result.intent_hint == "toggle_feature"
    
    def test_empty_and_edge_cases(self):
        """Test casos extremos"""
        tokenizer = NLPTokenizer(use_cache=False)
        
        assert tokenizer.tokenize("").tokens == []
        assert tokenizer.tokenize("   ").tokens == []
        
        result = tokenizer.tokenize("!")
        assert len(result.tokens) >= 0
    
    def test_spanish_accented_text(self):
        """Test texto con acentos"""
        result = tokenize_text("¿Qué mensaje quieres cambiar?")
        
        assert result.tokens
        assert "qué" in [t.lower() for t in result.tokens]
    
    def test_mixed_case_text(self):
        """Test texto con caso mixto"""
        result = tokenize_text("CAMBIAR el MENSAJE de BIENVENIDA")
        
        assert result.tokens
        assert result.has_lemma("cambiar")
        assert result.has_lemma("mensaje")


class TestBackwardCompatibilityIntegration:
    """Tests de backward compatibility"""
    
    def test_old_api_still_works(self):
        """Verifica que API antigua siga funcionando"""
        from app.nlp.normalizer import get_normalizer, normalize_text
        from app.nlp.tokenizer import get_tokenizer
        
        normalizer = get_normalizer()
        result = normalizer.normalize("Hola MUNDO")
        assert result == "hola mundo"
        
        text_result = normalize_text("Test")
        assert text_result
        
        tokenizer = get_tokenizer()
        tok_result = tokenizer.tokenize("Hola")
        assert tok_result.tokens
    
    def test_tokenization_result_compatibility(self):
        """Test que TokenizationResult sea compatible"""
        result = tokenize_text("Test")
        
        assert hasattr(result, 'tokens')
        assert hasattr(result, 'text')
        assert hasattr(result, 'pos_tags')
        assert hasattr(result, 'lemmas')
        assert hasattr(result, 'deps')
        assert hasattr(result, 'intent_hint')
        
        assert result.tokens
        assert result.text == "Test"

import pytest
from app.nlp.tokenizer import NLPTokenizer, TokenizationResult, _SPACY_MODELS_CACHE


class TestPOSTagging:
    """Tests para POS Tagging - Tarea T1.3"""
    
    @pytest.fixture
    def tokenizer(self):
        return NLPTokenizer(use_cache=False)
    
    def test_pos_tagging_basic(self, tokenizer):
        """Test básico de POS tagging"""
        result = tokenizer.tokenize("El gato duerme")
        
        pos_dict = dict(result.pos_tags)
        assert pos_dict["El"] == "DET"
        assert pos_dict["gato"] == "NOUN"
        assert pos_dict["duerme"] == "VERB"
    
    def test_pos_tagging_verbs(self, tokenizer):
        """Test identificación de verbos"""
        result = tokenizer.tokenize("Cambiar mensaje de bienvenida")
        
        pos_dict = dict(result.pos_tags)
        assert pos_dict["Cambiar"] == "VERB"
    
    def test_pos_tagging_nouns(self, tokenizer):
        """Test identificación de sustantivos"""
        result = tokenizer.tokenize("Mensaje de bienvenida")
        
        nouns = result.get_nouns()
        assert "Mensaje" in nouns or "bienvenida" in nouns
    
    def test_pos_tagging_adjectives(self, tokenizer):
        """Test identificación de adjetivos"""
        result = tokenizer.tokenize("El mensaje es importante")
        
        adjectives = result.get_adjectives()
        assert "importante" in adjectives
    
    def test_pos_tagging_preposition(self, tokenizer):
        """Test preposiciones"""
        result = tokenizer.tokenize("Mensaje de bienvenida")
        
        pos_dict = dict(result.pos_tags)
        assert pos_dict["de"] == "ADP"
    
    def test_get_verbs_method(self, tokenizer):
        """Test método get_verbs()"""
        result = tokenizer.tokenize("El gato duerme y juega")
        
        verbs = result.get_verbs()
        assert "duerme" in verbs
        assert "juega" in verbs
    
    def test_get_nouns_method(self, tokenizer):
        """Test método get_nouns()"""
        result = tokenizer.tokenize("El gato y el perro")
        
        nouns = result.get_nouns()
        assert "gato" in nouns
    
    def test_get_adjectives_method(self, tokenizer):
        """Test método get_adjectives()"""
        result = tokenizer.tokenize("Palabra muy mala")
        
        adjectives = result.get_adjectives()
        assert "mala" in adjectives
    
    def test_pos_tagging_empty_text(self, tokenizer):
        """Test POS tagging con texto vacío"""
        result = tokenizer.tokenize("")
        
        assert result.pos_tags == []
        assert result.get_nouns() == []
        assert result.get_verbs() == []
    
    def test_pos_tagging_returns_list(self, tokenizer):
        """Test que POS tagging retorna lista"""
        result = tokenizer.tokenize("Hola mundo")
        
        assert isinstance(result.pos_tags, list)
        assert len(result.pos_tags) == 2


class TestLemmatization:
    """Tests para Lemmatización - Tarea T1.2"""
    
    @pytest.fixture
    def tokenizer(self):
        return NLPTokenizer(use_cache=False)
    
    def test_lemmatization_basic(self, tokenizer):
        """Test lemmatización básica"""
        result = tokenizer.tokenize("corriendo")
        
        assert "correr" in result.lemmas
    
    def test_lemmatization_nouns(self, tokenizer):
        """Test lemmatización de sustantivos"""
        result = tokenizer.tokenize("Los niños")
        
        lemmas = result.get_lemmas_for_nouns()
        assert "niño" in lemmas or "los" in lemmas
    
    def test_get_lemmas_for_nouns(self, tokenizer):
        """Test método get_lemmas_for_nouns()"""
        result = tokenizer.tokenize("Los perros corren")
        
        lemmas = result.get_lemmas_for_nouns()
        assert "perro" in lemmas
    
    def test_has_lemma(self, tokenizer):
        """Test método has_lemma()"""
        result = tokenizer.tokenize("Cambiar mensaje")
        
        assert result.has_lemma("cambiar")
        assert result.has_lemma("mensaje")
    
    def test_lemmatization_fallback(self):
        """Test fallback lemmatization"""
        tokenizer = NLPTokenizer(use_cache=False)
        tokenizer._nlp = None
        
        result = tokenizer.tokenize("palabra palabras")
        
        assert result.lemmas == ["palabra", "palabras"]


class TestIntentHint:
    """Tests para Intent Hint Detection - Tarea T1.2"""
    
    @pytest.fixture
    def tokenizer(self):
        return NLPTokenizer(use_cache=False)
    
    def test_intent_hint_set_welcome(self, tokenizer):
        """Test detección intent set_welcome"""
        result = tokenizer.tokenize("Cambiar mensaje de bienvenida")
        
        assert result.intent_hint == "set_welcome"
    
    def test_intent_hint_add_filter(self, tokenizer):
        """Test detección intent add_filter"""
        result = tokenizer.tokenize("Bloquear palabra malas")
        
        assert result.intent_hint == "add_filter"
    
    def test_intent_hint_remove_filter(self, tokenizer):
        """Test detección intent remove_filter"""
        result = tokenizer.tokenize("Eliminar filtro de palabras")
        
        assert result.intent_hint == "remove_filter"
    
    def test_intent_hint_toggle_feature(self, tokenizer):
        """Test detección intent toggle_feature"""
        result = tokenizer.tokenize("Activar antiflood")
        
        assert result.intent_hint == "toggle_feature"
    
    def test_intent_hint_get_status(self, tokenizer):
        """Test detección intent get_status"""
        result = tokenizer.tokenize("Cuál es el estado del sistema")
        
        assert result.intent_hint == "get_status"
    
    def test_intent_hint_no_match(self, tokenizer):
        """Test sin coincidencia de intent"""
        result = tokenizer.tokenize("Hola buenas tardes")
        
        assert result.intent_hint is None


class TestDependencyParsing:
    """Tests para Dependency Parsing - Tarea T1.4"""
    
    @pytest.fixture
    def tokenizer(self):
        return NLPTokenizer(use_cache=False)
    
    def test_dependency_parsing(self, tokenizer):
        """Test parsing de dependencias"""
        result = tokenizer.tokenize("Cambiar mensaje")
        
        deps_dict = dict(result.deps)
        assert "Cambiar" in deps_dict
        assert "ROOT" in deps_dict.values() or "VERB" in deps_dict.values()
    
    def test_get_dependencies(self, tokenizer):
        """Test método get_dependencies()"""
        result = tokenizer.tokenize("El gato duerme")
        
        deps = result.get_dependencies()
        assert isinstance(deps, list)
        assert len(deps) > 0
    
    def test_dependency_parsing_returns_list(self, tokenizer):
        """Test que dependency parsing retorna lista"""
        result = tokenizer.tokenize("Hola mundo")
        
        assert isinstance(result.deps, list)
        assert len(result.deps) == 2


class TestBackwardCompatibility:
    """Tests para backward compatibility"""
    
    def test_basic_tokenization(self):
        """Test que tokenización básica sigue funcionando"""
        tokenizer = NLPTokenizer()
        result = tokenizer.tokenize("Hola mundo")
        
        assert result.tokens == ["Hola", "mundo"]
        assert result.text == "Hola mundo"
    
    def test_has_word(self):
        """Test método has_word()"""
        tokenizer = NLPTokenizer()
        result = tokenizer.tokenize("Cambiar mensaje")
        
        assert result.has_word("cambiar")
        assert result.has_word("mensaje")
        assert not result.has_word("perro")
    
    def test_analyze_method(self):
        """Test método analyze()"""
        tokenizer = NLPTokenizer(use_cache=False)
        analysis = tokenizer.analyze("El gato duerme")
        
        assert "tokens" in analysis
        assert "pos_tags" in analysis
        assert "lemmas" in analysis
        assert "deps" in analysis
        assert "intent_hint" in analysis
        assert "noun_count" in analysis
        assert "verb_count" in analysis
    
    def test_tokenizer_singleton(self):
        """Test singleton pattern"""
        from app.nlp.tokenizer import get_tokenizer
        
        tok1 = get_tokenizer()
        tok2 = get_tokenizer()
        
        assert tok1 is tok2
    
    def test_tokenize_text_function(self):
        """Test función de conveniencia"""
        from app.nlp.tokenizer import tokenize_text
        
        result = tokenize_text("Hola mundo")
        assert result.tokens == ["Hola", "mundo"]


class TestSpacyCache:
    """Tests para spaCy model cache - Tarea T1.5"""
    
    def test_cache_stores_model(self):
        """Test que el cache almacena el modelo"""
        _SPACY_MODELS_CACHE.clear()
        
        tokenizer = NLPTokenizer(use_cache=True)
        
        assert "es_core_news_sm" in _SPACY_MODELS_CACHE
    
    def test_cache_reuses_model(self):
        """Test que el cache reutiliza el modelo"""
        _SPACY_MODELS_CACHE.clear()
        
        tokenizer1 = NLPTokenizer(use_cache=True)
        model1 = tokenizer1._nlp
        
        tokenizer2 = NLPTokenizer(use_cache=True)
        model2 = tokenizer2._nlp
        
        assert model1 is model2
    
    def test_cache_disabled(self):
        """Test sin cache (use_cache=False)"""
        _SPACY_MODELS_CACHE.clear()
        
        tokenizer1 = NLPTokenizer(use_cache=False)
        tokenizer1._ensure_model_loaded()
        model1 = tokenizer1._nlp
        
        tokenizer2 = NLPTokenizer(use_cache=False)
        tokenizer2._ensure_model_loaded()
        model2 = tokenizer2._nlp
        
        if model1 is not None and model2 is not None:
            assert model1 is not model2 or "es_core_news_sm" not in _SPACY_MODELS_CACHE
    
    def test_cache_clear_function(self):
        """Test función para limpiar cache"""
        from app.nlp.tokenizer import clear_spacy_cache
        
        _SPACY_MODELS_CACHE["test_model"] = "dummy"
        assert "test_model" in _SPACY_MODELS_CACHE
        
        clear_spacy_cache()
        
        assert "test_model" not in _SPACY_MODELS_CACHE

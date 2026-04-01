import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from app.nlp.classifiers.ensemble_classifier import (
    RegexIntentClassifier,
    LLMIntentClassifier,
    EnsembleIntentClassifier
)
from app.nlp.tokenizer import TokenizationResult


class TestRegexIntentClassifier:
    """Tests para RegexIntentClassifier"""

    @pytest.fixture
    def classifier(self):
        """Fixture con RegexIntentClassifier"""
        return RegexIntentClassifier()

    def test_initialization(self, classifier):
        """Test: RegexIntentClassifier debe inicializar correctamente"""
        assert classifier.intents is not None
        assert len(classifier.intents) == 15

    def test_predict_returns_correct_structure(self, classifier):
        """Test: predict() debe retornar estructura correcta"""
        result = classifier.predict("cambiar mensaje de bienvenida")
        
        assert 'intent' in result
        assert 'confidence' in result
        assert 'method' in result
        assert result['method'] == 'regex_classifier'

    def test_predict_set_welcome(self, classifier):
        """Test: Debe detectar set_welcome"""
        result = classifier.predict("cambiar mensaje de bienvenida")
        
        assert result['intent'] == 'set_welcome'
        assert result['confidence'] > 0

    def test_predict_toggle_feature(self, classifier):
        """Test: Debe detectar toggle_feature"""
        result = classifier.predict("activar modo oscuro")
        
        assert result['intent'] == 'toggle_feature'
        assert result['confidence'] > 0

    def test_predict_add_filter(self, classifier):
        """Test: Debe detectar add_filter"""
        result = classifier.predict("bloquear palabra spam")
        
        assert result['intent'] == 'add_filter'
        assert result['confidence'] > 0

    def test_predict_remove_filter(self, classifier):
        """Test: Debe detectar remove_filter"""
        result = classifier.predict("desbloquear spam")
        
        assert result['intent'] == 'remove_filter'
        assert result['confidence'] > 0

    def test_predict_no_match(self, classifier):
        """Test: Debe retornar None o intent válido para texto sin match claro"""
        result = classifier.predict("xyz123 no match")
        
        assert result['intent'] is None or result['intent'] in classifier.intents
        if result['intent'] is not None:
            assert result['confidence'] > 0

    def test_predict_case_insensitive(self, classifier):
        """Test: Debe ser case insensitive"""
        result1 = classifier.predict("ACTIVAR MODO OSCURO")
        result2 = classifier.predict("activar modo oscuro")
        
        assert result1['intent'] == result2['intent']

    def test_confidence_range(self, classifier):
        """Test: Confidence debe estar en rango [0, 1]"""
        result = classifier.predict("cambiar mensaje de bienvenida")
        
        assert 0.0 <= result['confidence'] <= 1.0

    def test_probabilities_structure(self, classifier):
        """Test: Probabilities debe tener estructura correcta"""
        result = classifier.predict("cambiar mensaje de bienvenida")
        
        if result['intent'] is not None:
            assert 'probabilities' in result
            assert isinstance(result['probabilities'], dict)


class TestLLMIntentClassifier:
    """Tests para LLMIntentClassifier"""

    @pytest.fixture
    def classifier(self):
        """Fixture con LLMIntentClassifier"""
        return LLMIntentClassifier(timeout=2.0)

    def test_initialization(self, classifier):
        """Test: LLMIntentClassifier debe inicializar correctamente"""
        assert classifier.timeout == 2.0
        assert classifier.available is False

    @pytest.mark.asyncio
    async def test_predict_returns_fallback_structure(self, classifier):
        """Test: predict() debe retornar estructura de fallback"""
        result = await classifier.predict("test text")
        
        assert 'intent' in result
        assert 'confidence' in result
        assert 'method' in result
        assert result['method'] == 'llm_fallback'

    @pytest.mark.asyncio
    async def test_predict_returns_none_when_unavailable(self, classifier):
        """Test: Debe retornar None cuando LLM no disponible"""
        result = await classifier.predict("test text")
        
        assert result['intent'] is None

    def test_predict_sync_returns_structure(self, classifier):
        """Test: predict_sync debe retornar estructura correcta"""
        result = classifier.predict_sync("test text")
        
        assert 'intent' in result
        assert 'method' in result


class TestEnsembleIntentClassifier:
    """Tests para EnsembleIntentClassifier"""

    @pytest.fixture
    def ensemble(self):
        """Fixture con EnsembleIntentClassifier"""
        return EnsembleIntentClassifier()

    @pytest.fixture
    def mock_ml_classifier(self):
        """Fixture con mock de ML classifier"""
        mock = MagicMock()
        mock._feature_extractor = MagicMock()
        mock._feature_extractor.extract.return_value = np.random.rand(85)
        mock.predict.return_value = {
            'intent': 'set_welcome',
            'confidence': 0.82,
            'probabilities': {'set_welcome': 0.82, 'toggle_feature': 0.10}
        }
        return mock

    @pytest.fixture
    def tokenization_result(self):
        """Fixture con TokenizationResult"""
        return TokenizationResult(
            tokens=['cambiar', 'mensaje', 'bienvenida'],
            lemmas=['cambiar', 'mensaje', 'bienvenida'],
            pos_tags=[('cambiar', 'VERB'), ('mensaje', 'NOUN'), ('bienvenida', 'NOUN')],
            deps=[('cambiar', 'ROOT'), ('mensaje', 'OBJ')],
            text="Cambiar mensaje de bienvenida",
            intent_hint=None
        )

    def test_initialization(self, ensemble):
        """Test: EnsembleIntentClassifier debe inicializar correctamente"""
        assert ensemble.ml_classifier is None
        assert ensemble.regex_classifier is not None
        assert ensemble.llm_classifier is not None
        assert ensemble.high_confidence_threshold == 0.75
        assert ensemble.medium_confidence_threshold == 0.50

    def test_initialization_with_classifiers(self, mock_ml_classifier):
        """Test: Inicialización con clasificadores externos"""
        regex = RegexIntentClassifier()
        llm = LLMIntentClassifier()
        
        ensemble = EnsembleIntentClassifier(
            ml_classifier=mock_ml_classifier,
            regex_classifier=regex,
            llm_classifier=llm,
            ml_weight=0.6,
            regex_weight=0.4
        )
        
        assert ensemble.ml_classifier == mock_ml_classifier
        assert ensemble.ml_weight == 0.6
        assert ensemble.regex_weight == 0.4

    def test_high_confidence_returns_ml(self, ensemble, mock_ml_classifier, tokenization_result):
        """Test: Si confidence >= 0.75, debe usar ML"""
        ensemble.ml_classifier = mock_ml_classifier
        
        result = ensemble.predict("cambiar mensaje de bienvenida", tokenization_result)
        
        assert result['method'] == 'ml_classifier'
        assert result['confidence_level'] == 'high'

    def test_medium_confidence_ensemble_agreement(self, ensemble, tokenization_result):
        """Test: Confidence 0.5-0.75 con agreement debe retornar ensemble"""
        mock_ml = MagicMock()
        mock_ml._feature_extractor = MagicMock()
        mock_ml._feature_extractor.extract.return_value = np.random.rand(85)
        mock_ml.predict.return_value = {
            'intent': 'set_welcome',
            'confidence': 0.65,
            'probabilities': {'set_welcome': 0.65}
        }
        
        ensemble.ml_classifier = mock_ml
        
        result = ensemble.predict("cambiar mensaje de bienvenida", tokenization_result)
        
        assert result['confidence_level'] == 'medium'
        assert result['method'] in ['ensemble_agreement', 'ensemble_ml_preferred']

    def test_low_confidence_llm_fallback(self, ensemble, tokenization_result):
        """Test: Confidence < 0.5 debe intentar LLM fallback"""
        mock_ml = MagicMock()
        mock_ml._feature_extractor = MagicMock()
        mock_ml._feature_extractor.extract.return_value = np.random.rand(85)
        mock_ml.predict.return_value = {
            'intent': 'set_welcome',
            'confidence': 0.30,
            'probabilities': {'set_welcome': 0.30}
        }
        
        ensemble.ml_classifier = mock_ml
        
        result = ensemble.predict("test text", tokenization_result)
        
        assert result['confidence_level'] in ['low_llm_fallback', 'failed']

    def test_fallback_to_human_review(self, ensemble, tokenization_result):
        """Test: Si todo falla, debe retornar human review queue"""
        mock_ml = MagicMock()
        mock_ml._feature_extractor = MagicMock()
        mock_ml._feature_extractor.extract.return_value = np.random.rand(85)
        mock_ml.predict.return_value = {
            'intent': None,
            'confidence': 0.0
        }
        
        ensemble.ml_classifier = mock_ml
        
        result = ensemble.predict("texto sin sentido", tokenization_result)
        
        assert result['method'] == 'human_review_queue' or result['confidence_level'] == 'failed'

    def test_no_ml_classifier_uses_regex_only(self, ensemble):
        """Test: Sin ML classifier, debe usar solo Regex"""
        result = ensemble.predict("activar modo oscuro", None)
        
        assert 'method' in result
        assert result['method'] in ['regex_classifier', 'ensemble_agreement', 'ensemble_ml_preferred', 'human_review_queue']

    def test_set_ml_classifier(self, ensemble):
        """Test: set_ml_classifier debe funcionar"""
        mock_classifier = MagicMock()
        ensemble.set_ml_classifier(mock_classifier)
        
        assert ensemble.ml_classifier == mock_classifier


class TestEnsembleIntentClassifierEdgeCases:
    """Tests de casos extremos para EnsembleIntentClassifier"""

    @pytest.fixture
    def ensemble(self):
        return EnsembleIntentClassifier()

    def test_empty_text(self, ensemble):
        """Test: Debe manejar texto vacío"""
        result = ensemble.predict("", None)
        
        assert 'intent' in result

    def test_very_long_text(self, ensemble):
        """Test: Debe manejar texto muy largo"""
        long_text = "palabra " * 1000
        result = ensemble.predict(long_text, None)
        
        assert 'intent' in result

    def test_ml_classifier_exception(self, ensemble):
        """Test: Debe manejar excepciones del ML classifier"""
        mock_ml = MagicMock()
        mock_ml._feature_extractor = MagicMock()
        mock_ml._feature_extractor.extract.side_effect = Exception("Test error")
        
        ensemble.ml_classifier = mock_ml
        
        tokenization_result = TokenizationResult(
            tokens=['test'], lemmas=['test'], pos_tags=[], deps=[], text="test"
        )
        result = ensemble.predict("test", tokenization_result)
        
        assert 'intent' in result

    def test_confidence_levels_enum(self, ensemble, mock_ml_classifier=None):
        """Test: Niveles de confianza deben ser válidos"""
        mock_ml = MagicMock()
        mock_ml._feature_extractor = MagicMock()
        mock_ml._feature_extractor.extract.return_value = np.random.rand(85)
        mock_ml.predict.return_value = {
            'intent': 'test',
            'confidence': 0.9
        }
        ensemble.ml_classifier = mock_ml
        
        result = ensemble.predict("test", TokenizationResult(
            tokens=['test'], lemmas=['test'], pos_tags=[], deps=[], text="test"
        ))
        
        assert result['confidence_level'] in ['high', 'medium', 'low_llm_fallback', 'failed']


class TestEnsembleIntentClassifierIntegration:
    """Tests de integración"""

    def test_full_pipeline(self):
        """Test: Pipeline completo debe funcionar"""
        from app.nlp.features import FeatureExtractor
        
        extractor = FeatureExtractor(max_features=10)
        texts = [
            "cambiar mensaje de bienvenida", 
            "activar modo oscuro", 
            "bloquear palabra spam",
            "desactivar antiflood",
            "ver estado del sistema",
            "cambiar configuracion",
            "crear nueva tarea",
            "eliminar filtro",
            "asignar rol",
            "otorgar permiso"
        ]
        extractor.fit(texts)
        
        mock_ml = MagicMock()
        mock_ml._feature_extractor = extractor
        mock_ml.predict.return_value = {
            'intent': 'set_welcome',
            'confidence': 0.85,
            'method': 'ml_classifier',
            'probabilities': {'set_welcome': 0.85}
        }
        
        ensemble = EnsembleIntentClassifier(ml_classifier=mock_ml)
        
        tokenization_result = TokenizationResult(
            tokens=['cambiar', 'mensaje', 'bienvenida'],
            lemmas=['cambiar', 'mensaje', 'bienvenida'],
            pos_tags=[('cambiar', 'VERB'), ('mensaje', 'NOUN'), ('bienvenida', 'NOUN')],
            deps=[('cambiar', 'ROOT'), ('mensaje', 'OBJ')],
            text="cambiar mensaje de bienvenida"
        )
        
        result = ensemble.predict("cambiar mensaje de bienvenida", tokenization_result)
        
        assert result['intent'] is not None
        assert 'confidence' in result

    def test_weights_configuration(self):
        """Test: Configuración de pesos debe respetarse"""
        ensemble = EnsembleIntentClassifier(
            ml_weight=0.7,
            regex_weight=0.3
        )
        
        assert ensemble.ml_weight == 0.7
        assert ensemble.regex_weight == 0.3
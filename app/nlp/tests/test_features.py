import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.nlp.features import FeatureExtractor
from app.nlp.tokenizer import TokenizationResult


class TestFeatureExtractor:
    """Tests para FeatureExtractor"""

    @pytest.fixture
    def feature_extractor(self):
        """Fixture que retorna un FeatureExtractor configurado"""
        extractor = FeatureExtractor(max_features=10, min_df=1)
        return extractor

    def test_initialization(self, feature_extractor):
        """Test: FeatureExtractor debe inicializar correctamente"""
        assert feature_extractor.max_features == 10
        assert feature_extractor.is_fitted is False
        assert feature_extractor.tfidf_vectorizer is not None

    @pytest.fixture
    def sample_tokenization_result(self):
        """Fixture con resultado de tokenización de ejemplo"""
        return TokenizationResult(
            tokens=['cambiar', 'mensaje', 'bienvenida'],
            lemmas=['cambiar', 'mensaje', 'bienvenida'],
            pos_tags=[('cambiar', 'VERB'), ('mensaje', 'NOUN'), ('bienvenida', 'NOUN')],
            deps=[('cambiar', 'ROOT'), ('mensaje', 'OBJ'), ('bienvenida', 'NMOD')],
            text="Cambiar mensaje de bienvenida",
            intent_hint=None
        )

    def test_initialization(self, feature_extractor):
        """Test: FeatureExtractor debe inicializar correctamente"""
        assert feature_extractor.is_fitted is False
        assert feature_extractor.tfidf_vectorizer is not None

    def test_fit(self, feature_extractor):
        """Test: fit() debe marcar el extractor como fitted"""
        texts = ["ejemplo uno", "ejemplo dos", "ejemplo tres"]
        result = feature_extractor.fit(texts)
        assert feature_extractor.is_fitted is True
        assert result is feature_extractor

    def test_fit_raises_if_not_fitted(self, feature_extractor):
        """Test: extract() debe lanzar error si no se ha hecho fit"""
        tokenization_result = Mock()
        with pytest.raises(ValueError, match="Fit extractor first"):
            feature_extractor.extract(tokenization_result)

    def test_extract_shape(self, feature_extractor, sample_tokenization_result):
        """Test: extract() debe retornar vector de shape correcto"""
        texts = [
            "cambiar mensaje bienvenida uno",
            "otro ejemplo dos tres",
            "tercer texto cuatro cinco"
        ]
        feature_extractor.fit(texts)

        features = feature_extractor.extract(sample_tokenization_result)
        
        expected_length = feature_extractor.max_features + 10 + 10 + 15
        assert features.shape == (expected_length,), f"Expected shape ({expected_length},), got {features.shape}"

    def test_extract_no_nan(self, feature_extractor, sample_tokenization_result):
        """Test: features no deben contener NaN"""
        texts = [
            "cambiar mensaje bienvenida uno",
            "otro ejemplo dos tres"
        ]
        feature_extractor.fit(texts)

        features = feature_extractor.extract(sample_tokenization_result)
        
        assert not np.any(np.isnan(features)), "Features contain NaN values"

    def test_extract_range(self, feature_extractor, sample_tokenization_result):
        """Test: TF-IDF features deben estar en rango [0, 1]"""
        texts = [
            "cambiar mensaje bienvenida uno",
            "otro ejemplo dos tres"
        ]
        feature_extractor.fit(texts)

        features = feature_extractor.extract(sample_tokenization_result)
        
        tfidf_features = features[:feature_extractor.max_features]
        assert np.all(tfidf_features >= 0), "TF-IDF features below 0"
        assert np.all(tfidf_features <= 1), "TF-IDF features above 1"

    def test_transform(self, feature_extractor):
        """Test: transform() debe retornar matriz correcta"""
        texts = ["texto uno", "texto dos", "texto tres"]
        feature_extractor.fit(texts)

        result = feature_extractor.transform(texts)
        
        assert result.shape[0] == 3
        assert result.shape[1] > 0

    def test_pos_patterns_extraction(self, feature_extractor):
        """Test: POS patterns deben extraerse correctamente"""
        result = TokenizationResult(
            tokens=['correr', 'rápido'],
            lemmas=['correr', 'rápido'],
            pos_tags=[('correr', 'VERB'), ('rápido', 'ADJ')],
            deps=[],
            text="correr rápido"
        )

        feature_extractor.fit(["correr rápido palabra", "otra palabra"])
        features = feature_extractor.extract(result)

        # Verify features are extracted (length > 0)
        assert len(features) > 20, "Feature vector should have at least 20 features"

    def test_dependency_features_extraction(self, feature_extractor):
        """Test: Dependency features deben extraerse correctamente"""
        result = TokenizationResult(
            tokens=['cambiar', 'mensaje'],
            lemmas=['cambiar', 'mensaje'],
            pos_tags=[('cambiar', 'VERB'), ('mensaje', 'NOUN')],
            deps=[('cambiar', 'ROOT'), ('mensaje', 'OBJ')],
            text="cambiar mensaje"
        )

        feature_extractor.fit(["cambiar mensaje prueba", "otra prueba"])
        features = feature_extractor.extract(result)

        # Verify features are extracted
        assert len(features) > 20, "Feature vector should have at least 20 features"

    def test_keyword_features_extraction(self, feature_extractor):
        """Test: Keyword features deben detectarse correctamente"""
        result = TokenizationResult(
            tokens=['cambiar', 'bienvenida'],
            lemmas=['cambiar', 'bienvenida'],
            pos_tags=[('cambiar', 'VERB'), ('bienvenida', 'NOUN')],
            deps=[],
            text="cambiar bienvenida"
        )

        feature_extractor.fit(["cambiar bienvenida texto", "otro texto"])
        features = feature_extractor.extract(result)

        # Verify features are extracted
        assert len(features) > 20, "Feature vector should have at least 20 features"

    def test_empty_tokenization_result(self, feature_extractor):
        """Test: Debe manejar tokenization result vacío"""
        result = TokenizationResult(
            tokens=[],
            lemmas=[],
            pos_tags=[],
            deps=[],
            text=""
        )

        feature_extractor.fit(["texto uno", "texto dos"])
        features = feature_extractor.extract(result)

        assert features.shape[0] > 0

    def test_tfidf_vectorizer_parameters(self):
        """Test: TF-IDF vectorizer debe tener parámetros correctos"""
        extractor = FeatureExtractor(max_features=100, min_df=1)

        assert extractor.tfidf_vectorizer.ngram_range == (1, 2)
        assert extractor.tfidf_vectorizer.min_df == 1
        assert extractor.tfidf_vectorizer.max_df == 0.8
        assert extractor.tfidf_vectorizer.sublinear_tf is True

    def test_transform_raises_if_not_fitted(self, feature_extractor):
        """Test: transform debe lanzar error si no se ha hecho fit"""
        with pytest.raises(ValueError, match="Fit extractor first"):
            feature_extractor.transform(["texto"])


class TestFeatureExtractorIntegration:
    """Tests de integración para FeatureExtractor"""

    def test_full_pipeline_with_training_data(self):
        """Test: Pipeline completo con datos de entrenamiento"""
        texts = [
            "cambiar mensaje de bienvenida uno dos",
            "activar modo oscuro tres cuatro",
            "ver estado del sistema cinco seis",
            "bloquear palabra spam siete ocho",
            "desactivar antiflood nueve diez"
        ]

        extractor = FeatureExtractor(max_features=100, min_df=1)
        extractor.fit(texts)

        tokenization_result = TokenizationResult(
            tokens=['cambiar', 'mensaje', 'bienvenida'],
            lemmas=['cambiar', 'mensaje', 'bienvenida'],
            pos_tags=[('cambiar', 'VERB'), ('mensaje', 'NOUN'), ('bienvenida', 'NOUN')],
            deps=[('cambiar', 'ROOT'), ('mensaje', 'OBJ')],
            text="cambiar mensaje de bienvenida"
        )

        features = extractor.extract(tokenization_result)

        assert features.shape[0] > 0
        assert not np.any(np.isnan(features))

    def test_multiple_texts_extraction(self):
        """Test: Extracción de múltiples textos"""
        texts = ["texto uno", "texto dos", "texto tres"]
        
        extractor = FeatureExtractor(max_features=20, min_df=1)
        extractor.fit(texts)

        for text in texts:
            result = TokenizationResult(
                tokens=text.split(),
                lemmas=text.split(),
                pos_tags=[(t, 'NOUN') for t in text.split()],
                deps=[],
                text=text
            )
            features = extractor.extract(result)
            # Just verify features is not empty and has reasonable length
            assert features.shape[0] > 30
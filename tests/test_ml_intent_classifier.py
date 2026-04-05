import pytest
import numpy as np
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from app.nlp.classifiers.ml_classifier import MLIntentClassifier


class TestMLIntentClassifier:
    """Tests para MLIntentClassifier"""

    @pytest.fixture
    def temp_model_path(self):
        """Fixture con path temporal para modelo (no existente)"""
        import uuid
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'test_model_{uuid.uuid4()}.joblib')
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def classifier(self, temp_model_path):
        """Fixture que retorna un MLIntentClassifier"""
        return MLIntentClassifier(model_path=temp_model_path)

    @pytest.fixture
    def sample_features(self):
        """Fixture con features de ejemplo"""
        return np.random.rand(85)

    @pytest.fixture
    def training_data(self):
        """Fixture con datos de entrenamiento"""
        X = np.random.rand(100, 85)
        y = ['set_welcome'] * 20 + ['toggle_feature'] * 20 + ['add_filter'] * 20 + \
            ['get_status'] * 20 + ['create_task'] * 20
        return X, y

    def test_initialization(self, classifier, temp_model_path):
        """Test: MLIntentClassifier debe inicializar correctamente"""
        assert classifier.model_path == temp_model_path
        assert classifier.classes is not None
        assert len(classifier.classes) == 15

    def test_intent_classes_complete(self, classifier):
        """Test: Debe tener las 15 clases de intents"""
        expected_classes = [
            'set_welcome', 'set_goodbye', 'toggle_feature',
            'add_filter', 'remove_filter', 'get_status',
            'get_settings', 'update_config', 'query_data',
            'execute_action', 'create_task', 'delete_task',
            'assign_role', 'grant_permission', 'revoke_permission'
        ]
        assert classifier.classes == expected_classes

    def test_model_not_trained_initially(self, classifier):
        """Test: Modelo no debe estar entrenado inicialmente"""
        assert classifier.is_trained is False

    def test_train_model(self, classifier, training_data):
        """Test: Entrenar modelo debe funcionar correctamente"""
        X_train, y_train = training_data
        
        result = classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        assert classifier.is_trained is True
        assert classifier.model is not None
        assert os.path.exists(classifier.model_path)

    def test_train_with_hyperparameter_tuning(self, classifier, training_data):
        """Test: Entrenar con hyperparameter tuning"""
        X_train, y_train = training_data
        
        result = classifier.train(X_train, y_train, hyperparameter_tuning=True)
        
        assert classifier.is_trained is True
        assert 'best_params' in result
        assert 'best_cv_score' in result

    def test_predict_raises_if_not_trained(self, classifier, sample_features):
        """Test: predict() debe lanzar error si no está entrenado"""
        with pytest.raises(ValueError, match="Model not trained"):
            classifier.predict(sample_features)

    def test_predict_returns_correct_structure(self, classifier, training_data, sample_features):
        """Test: predict() debe retornar estructura correcta"""
        X_train, y_train = training_data
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        result = classifier.predict(sample_features)
        
        assert 'intent' in result
        assert 'confidence' in result
        assert 'probabilities' in result
        assert 'method' in result
        assert result['method'] == 'ml_classifier'

    def test_predict_confidence_range(self, classifier, training_data, sample_features):
        """Test: Confidence debe estar en rango [0, 1]"""
        X_train, y_train = training_data
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        result = classifier.predict(sample_features)
        
        assert 0.0 <= result['confidence'] <= 1.0

    def test_predict_probabilities_sum_to_one(self, classifier, training_data, sample_features):
        """Test: Probabilidades deben sumar aproximadamente 1"""
        X_train, y_train = training_data
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        result = classifier.predict(sample_features)
        
        total = sum(result['probabilities'].values())
        assert 0.99 <= total <= 1.01

    def test_1d_features_reshape(self, classifier, training_data):
        """Test: Debe manejar features 1D"""
        X_train, y_train = training_data
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        single_feature = np.random.rand(85)
        result = classifier.predict(single_feature)
        
        assert 'intent' in result

    def test_load_model_file_not_found(self):
        """Test: Debe manejar archivo no encontrado"""
        classifier = MLIntentClassifier(model_path="nonexistent.joblib")
        assert classifier.model is None
        assert classifier.is_trained is False


class TestMLIntentClassifierCrossValidation:
    """Tests de cross-validation"""

    @pytest.fixture
    def temp_model_path(self):
        import uuid
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'test_model_{uuid.uuid4()}.joblib')
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def classifier(self, temp_model_path):
        return MLIntentClassifier(model_path=temp_model_path)

    def test_cross_validate_raises_if_not_trained(self, classifier):
        """Test: cross_validate debe lanzar error si no está entrenado"""
        X = np.random.rand(50, 85)
        y = ['set_welcome'] * 10 + ['toggle_feature'] * 10 + ['add_filter'] * 30
        
        with pytest.raises(ValueError, match="Model not trained"):
            classifier.cross_validate(X, y)

    def test_cross_validate_returns_scores(self, classifier):
        """Test: cross_validate debe retornar métricas"""
        X_train = np.random.rand(100, 85)
        y_train = ['set_welcome'] * 20 + ['toggle_feature'] * 20 + \
                  ['add_filter'] * 20 + ['get_status'] * 40
        
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        scores = classifier.cross_validate(X_train, y_train, cv=3)
        
        assert 'accuracy_mean' in scores
        assert 'precision_mean' in scores
        assert 'recall_mean' in scores
        assert 'f1_mean' in scores
        assert 0 <= scores['accuracy_mean'] <= 1


class TestMLIntentClassifierEvaluation:
    """Tests de evaluación"""

    @pytest.fixture
    def temp_model_path(self):
        import uuid
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'test_model_{uuid.uuid4()}.joblib')
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def trained_classifier(self, temp_model_path):
        classifier = MLIntentClassifier(model_path=temp_model_path)
        X_train = np.random.rand(100, 85)
        y_train = ['set_welcome'] * 25 + ['toggle_feature'] * 25 + \
                  ['add_filter'] * 25 + ['get_status'] * 25
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        return classifier

    def test_evaluate_returns_metrics(self, trained_classifier):
        """Test: evaluate() debe retornar métricas"""
        X_test = np.random.rand(20, 85)
        y_test = ['set_welcome'] * 5 + ['toggle_feature'] * 5 + \
                 ['add_filter'] * 5 + ['get_status'] * 5
        
        result = trained_classifier.evaluate(X_test, y_test)
        
        assert 'accuracy' in result
        assert 'precision' in result
        assert 'recall' in result
        assert 'f1' in result

    def test_evaluate_accuracy_range(self, trained_classifier):
        """Test: Accuracy debe estar en rango válido"""
        X_test = np.random.rand(20, 85)
        y_test = ['set_welcome'] * 5 + ['toggle_feature'] * 5 + \
                 ['add_filter'] * 5 + ['get_status'] * 5
        
        result = trained_classifier.evaluate(X_test, y_test)
        
        assert 0 <= result['accuracy'] <= 1

    def test_evaluate_classification_report(self, trained_classifier):
        """Test: evaluate() debe incluir classification report"""
        X_test = np.random.rand(20, 85)
        y_test = ['set_welcome'] * 5 + ['toggle_feature'] * 5 + \
                 ['add_filter'] * 5 + ['get_status'] * 5
        
        result = trained_classifier.evaluate(X_test, y_test)
        
        assert 'classification_report' in result
        assert 'confusion_matrix' in result


class TestFeatureImportance:
    """Tests de feature importance"""

    @pytest.fixture
    def temp_model_path(self):
        import uuid
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'test_model_{uuid.uuid4()}.joblib')
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def trained_classifier(self, temp_model_path):
        classifier = MLIntentClassifier(model_path=temp_model_path)
        X_train = np.random.rand(100, 85)
        y_train = ['set_welcome'] * 25 + ['toggle_feature'] * 25 + \
                  ['add_filter'] * 25 + ['get_status'] * 25
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        return classifier

    def test_feature_importance_raises_if_not_trained(self, temp_model_path):
        """Test: get_feature_importance debe lanzar error si no entrenado"""
        classifier = MLIntentClassifier(model_path=temp_model_path)
        
        with pytest.raises(ValueError, match="Model not trained"):
            classifier.get_feature_importance()

    def test_feature_importance_returns_list(self, trained_classifier):
        """Test: get_feature_importance debe retornar lista"""
        importance = trained_classifier.get_feature_importance(top_n=10)
        
        assert isinstance(importance, list)
        assert len(importance) <= 10

    def test_feature_importance_structure(self, trained_classifier):
        """Test: cada item debe tener campos correctos"""
        importance = trained_classifier.get_feature_importance(top_n=5)
        
        for item in importance:
            assert 'intent' in item
            assert 'feature_index' in item
            assert 'coefficient' in item


class TestPredictFromText:
    """Tests de predicción desde texto"""

    @pytest.fixture
    def temp_model_path(self):
        import uuid
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'test_model_{uuid.uuid4()}.joblib')
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_predict_from_text_raises_without_extractor(self, temp_model_path):
        """Test: predict_from_text debe lanzar error sin extractor"""
        classifier = MLIntentClassifier(model_path=temp_model_path)
        
        with pytest.raises(ValueError, match="Feature extractor not set"):
            classifier.predict_from_text("test text")

    def test_predict_from_text_with_mock_extractor(self, temp_model_path):
        """Test: predict_from_text con feature extractor"""
        classifier = MLIntentClassifier(model_path=temp_model_path)
        
        mock_extractor = MagicMock()
        mock_extractor.is_fitted = True
        mock_extractor.extract.return_value = np.random.rand(85)
        classifier.set_feature_extractor(mock_extractor)
        
        X_train = np.random.rand(100, 85)
        y_train = ['set_welcome'] * 25 + ['toggle_feature'] * 25 + \
                  ['add_filter'] * 25 + ['get_status'] * 25
        classifier.train(X_train, y_train, hyperparameter_tuning=False)
        
        result = classifier.predict_from_text("cambiar mensaje de bienvenida")
        
        assert 'intent' in result
        assert 'confidence' in result
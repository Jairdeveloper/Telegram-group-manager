import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
import joblib
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class MLIntentClassifier:
    """Logistic Regression para intent classification"""

    INTENT_CLASSES = [
        'set_welcome', 'set_goodbye', 'toggle_feature',
        'add_filter', 'remove_filter', 'get_status',
        'get_settings', 'update_config', 'query_data',
        'execute_action', 'create_task', 'delete_task',
        'assign_role', 'grant_permission', 'revoke_permission'
    ]

    def __init__(self, model_path: str = "models/intent_classifier.joblib"):
        self.model = None
        self.model_path = model_path
        self.classes = self.INTENT_CLASSES
        self.is_trained = False
        self._feature_extractor = None
        self.load_model()

    def load_model(self):
        """Cargar modelo preentrenado si existe"""
        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Model not found at {self.model_path}")
            self.model = None
            self.is_trained = False

    def set_feature_extractor(self, feature_extractor):
        """Set feature extractor for predictions"""
        self._feature_extractor = feature_extractor

    def train(self, X_train: np.ndarray, y_train: List[str],
              hyperparameter_tuning: bool = True) -> Dict[str, Any]:
        """
        Entrenar modelo con datos de entrenamiento
        
        Args:
            X_train: Feature matrix (n_samples, n_features)
            y_train: Intent labels
            hyperparameter_tuning: Whether to perform hyperparameter tuning
            
        Returns:
            Training results with metrics
        """
        from sklearn.model_selection import GridSearchCV
        
        if hyperparameter_tuning:
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'solver': ['lbfgs', 'newton-cg'],
                'max_iter': [1000, 2000]
            }
            
            lr = LogisticRegression(random_state=42)
            grid_search = GridSearchCV(
                lr, param_grid, cv=5, scoring='accuracy', n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            
            self.model = grid_search.best_estimator_
            training_result = {
                'best_params': grid_search.best_params_,
                'best_cv_score': grid_search.best_score_,
                'hyperparameter_tuning': True
            }
            logger.info(f"Best params: {grid_search.best_params_}")
            logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
        else:
            self.model = LogisticRegression(
                C=1.0,
                solver='lbfgs',
                max_iter=1000,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            training_result = {
                'hyperparameter_tuning': False,
                'params': {'C': 1.0, 'solver': 'lbfgs'}
            }

        self.is_trained = True
        self.save_model()
        
        return training_result

    def save_model(self):
        """Guardar modelo entrenado"""
        if self.model is not None:
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")

    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Predecir intent con confianza
        
        Args:
            features: Feature vector (n_features,) or (1, n_features)
            
        Returns:
            {
                'intent': str,
                'confidence': float (0.0-1.0),
                'probabilities': Dict[str, float],
                'method': 'ml_classifier'
            }
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        if features.ndim == 1:
            features = features.reshape(1, -1)

        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(np.max(probabilities))

        prob_dict = {
            intent: float(prob)
            for intent, prob in zip(self.classes, probabilities)
        }

        return {
            'intent': prediction,
            'confidence': confidence,
            'probabilities': prob_dict,
            'method': 'ml_classifier'
        }

    def predict_from_text(self, text: str) -> Dict[str, Any]:
        """Predecir intent directamente desde texto"""
        if self._feature_extractor is None:
            raise ValueError("Feature extractor not set")

        if not self._feature_extractor.is_fitted:
            raise ValueError("Feature extractor not fitted")

        from app.nlp.tokenizer import NLPTokenizer
        
        tokenizer = NLPTokenizer()
        tokenization_result = tokenizer.tokenize(text)
        
        features = self._feature_extractor.extract(tokenization_result)
        return self.predict(features)

    def cross_validate(self, X: np.ndarray, y: List[str], cv: int = 5) -> Dict[str, float]:
        """
        Realizar cross-validation
        
        Args:
            X: Feature matrix
            y: Labels
            cv: Number of folds
            
        Returns:
            Cross-validation scores
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        accuracy_scores = cross_val_score(self.model, X, y, cv=skf, scoring='accuracy')
        precision_scores = cross_val_score(self.model, X, y, cv=skf, scoring='precision_macro')
        recall_scores = cross_val_score(self.model, X, y, cv=skf, scoring='recall_macro')
        f1_scores = cross_val_score(self.model, X, y, cv=skf, scoring='f1_macro')

        return {
            'accuracy_mean': float(np.mean(accuracy_scores)),
            'accuracy_std': float(np.std(accuracy_scores)),
            'precision_mean': float(np.mean(precision_scores)),
            'precision_std': float(np.std(precision_scores)),
            'recall_mean': float(np.mean(recall_scores)),
            'recall_std': float(np.std(recall_scores)),
            'f1_mean': float(np.mean(f1_scores)),
            'f1_std': float(np.std(f1_scores))
        }

    def evaluate(self, X_test: np.ndarray, y_test: List[str]) -> Dict[str, Any]:
        """Evaluar modelo en test set"""
        from sklearn.metrics import (
            accuracy_score, precision_recall_fscore_support,
            classification_report, confusion_matrix
        )

        y_pred = self.model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='macro', zero_division=0
        )

        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        conf_matrix = confusion_matrix(y_test, y_pred)

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'classification_report': report,
            'confusion_matrix': conf_matrix.tolist()
        }

    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Obtener importancia de features (coeficientes del modelo)"""
        if self.model is None:
            raise ValueError("Model not trained yet")

        coefficients = self.model.coef_
        model_classes = self.model.classes_
        feature_importance = []

        for class_idx, class_name in enumerate(model_classes):
            class_coefs = coefficients[class_idx]
            top_indices = np.argsort(np.abs(class_coefs))[-top_n:][::-1]
            
            for idx in top_indices:
                feature_importance.append({
                    'intent': class_name,
                    'feature_index': int(idx),
                    'coefficient': float(class_coefs[idx]),
                    'abs_coefficient': float(np.abs(class_coefs[idx]))
                })

        feature_importance.sort(key=lambda x: x['abs_coefficient'], reverse=True)
        return feature_importance[:top_n]
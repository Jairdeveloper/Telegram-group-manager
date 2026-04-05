import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
import joblib
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Calibra probabilidades usando Platt scaling para confianza confiable"""

    def __init__(self, calibrator_path: str = "models/confidence_calibrator.joblib"):
        self.calibrator = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
        self.is_fitted = False
        self.calibrator_path = calibrator_path
        self.class_labels = None
        self.load_calibrator()

    def load_calibrator(self):
        """Cargar calibrador preentrenado si existe"""
        try:
            data = joblib.load(self.calibrator_path)
            self.calibrator = data['calibrator']
            self.class_labels = data['class_labels']
            self.is_fitted = True
            logger.info(f"Calibrator loaded from {self.calibrator_path}")
        except FileNotFoundError:
            logger.warning("Calibrator not found, will need fitting")

    def fit(self, probabilities: np.ndarray, true_labels: np.ndarray) -> Dict[str, float]:
        """
        Fitear calibrador en validation set usando Platt scaling
        
        Args:
            probabilities: Predicted probabilities (n_samples, n_classes)
            true_labels: True labels (n_samples,)
            
        Returns:
            Fit results with metrics
        """
        if self.class_labels is None:
            raise ValueError("Class labels not set. Set class_labels first.")

        max_probs = np.max(probabilities, axis=1)
        predicted_labels = np.argmax(probabilities, axis=1)

        binary_labels = (predicted_labels == true_labels).astype(int)

        self.calibrator.fit(max_probs.reshape(-1, 1), binary_labels)
        self.is_fitted = True

        accuracy_before = np.mean(predicted_labels == true_labels)
        
        self.save_calibrator()

        logger.info(f"Calibrator fitted. Accuracy before calibration: {accuracy_before:.4f}")

        return {
            'accuracy_before_calibration': accuracy_before,
            'samples_used': len(probabilities),
            'n_classes': probabilities.shape[1]
        }

    def set_class_labels(self, class_labels: List[str]):
        """Set class labels for calibration"""
        self.class_labels = class_labels

    def calibrate(self, probabilities: np.ndarray) -> np.ndarray:
        """
        Aplicar calibración a nuevas probabilidades
        
        Args:
            probabilities: Raw probabilities (n_samples, n_classes)
            
        Returns:
            Calibrated probabilities
        """
        if not self.is_fitted:
            raise ValueError("Calibrator not fitted yet")

        max_probs = np.max(probabilities, axis=1)
        
        calibrated_probs = np.zeros_like(probabilities)
        
        for i in range(len(max_probs)):
            calibrated = self.calibrator.predict_proba(max_probs[i].reshape(1, -1))
            calibrated_probs[i, :] = calibrated[0, 1] * probabilities[i, :]

        row_sums = calibrated_probs.sum(axis=1, keepdims=True)
        calibrated_probs = calibrated_probs / (row_sums + 1e-10)

        return calibrated_probs

    def calibrate_single(self, probabilities: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Calibrar probabilidades de una sola predicción
        
        Args:
            probabilities: Raw probabilities (n_classes,)
            
        Returns:
            (calibrated_probs, confidence)
        """
        if probabilities.ndim == 1:
            probabilities = probabilities.reshape(1, -1)
            
        calibrated = self.calibrate(probabilities)
        confidence = np.max(calibrated)
        
        return calibrated[0], float(confidence)

    def save_calibrator(self):
        """Guardar calibrador entrenado"""
        data = {
            'calibrator': self.calibrator,
            'class_labels': self.class_labels
        }
        joblib.dump(data, self.calibrator_path)
        logger.info(f"Calibrator saved to {self.calibrator_path}")

    def expected_calibration_error(self,
                                   probabilities: np.ndarray,
                                   true_labels: np.ndarray,
                                   n_bins: int = 10) -> Dict[str, float]:
        """
        Calcular ECE (Expected Calibration Error)
        
        Args:
            probabilities: Predicted probabilities (n_samples, n_classes)
            true_labels: True labels (n_samples,)
            n_bins: Number of confidence bins
            
        Returns:
            ECE metrics
        """
        confidences = np.max(probabilities, axis=1)
        predictions = np.argmax(probabilities, axis=1)
        accuracies = (predictions == true_labels).astype(float)

        bins = np.linspace(0, 1, n_bins + 1)
        
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []

        for i in range(len(bins) - 1):
            mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
            count = np.sum(mask)
            
            if count > 0:
                bin_acc = np.mean(accuracies[mask])
                bin_conf = np.mean(confidences[mask])
                bin_accuracies.append(bin_acc)
                bin_confidences.append(bin_conf)
                bin_counts.append(count)

        bin_accuracies = np.array(bin_accuracies)
        bin_confidences = np.array(bin_confidences)
        bin_counts = np.array(bin_counts)

        ece = np.sum(bin_counts * np.abs(bin_accuracies - bin_confidences)) / np.sum(bin_counts)

        return {
            'ece': float(ece),
            'n_bins': n_bins,
            'bin_details': [
                {
                    'bin_start': float(bins[i]),
                    'bin_end': float(bins[i + 1]),
                    'accuracy': float(bin_accuracies[i]) if i < len(bin_accuracies) else None,
                    'confidence': float(bin_confidences[i]) if i < len(bin_confidences) else None,
                    'count': int(bin_counts[i]) if i < len(bin_counts) else 0
                }
                for i in range(n_bins)
            ]
        }

    def reliability_diagram_data(self,
                                  probabilities: np.ndarray,
                                  true_labels: np.ndarray,
                                  n_bins: int = 10) -> Dict:
        """
        Generar datos para reliability diagram
        
        Args:
            probabilities: Predicted probabilities
            true_labels: True labels
            n_bins: Number of bins
            
        Returns:
            Data for plotting reliability diagram
        """
        ece_result = self.expected_calibration_error(probabilities, true_labels, n_bins)
        
        return {
            'ece': ece_result['ece'],
            'bin_accuracies': [b['accuracy'] for b in ece_result['bin_details'] if b['accuracy'] is not None],
            'bin_confidences': [b['confidence'] for b in ece_result['bin_details'] if b['confidence'] is not None],
            'bin_counts': [b['count'] for b in ece_result['bin_details']]
        }

    def calibrate_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """
        Calibrar predicciones del clasificador
        
        Args:
            predictions: List of prediction dicts from MLIntentClassifier
            
        Returns:
            List of calibrated predictions
        """
        if not self.is_fitted:
            raise ValueError("Calibrator not fitted")

        calibrated_predictions = []
        
        for pred in predictions:
            probs = np.array([pred['probabilities'][cls] for cls in self.class_labels])
            
            calibrated_probs, confidence = self.calibrate_single(probs)
            
            calibrated_pred = {
                'intent': pred['intent'],
                'confidence': confidence,
                'calibrated_probabilities': {
                    cls: float(calibrated_probs[i])
                    for i, cls in enumerate(self.class_labels)
                },
                'method': pred.get('method', 'ml_classifier') + '_calibrated',
                'original_confidence': pred.get('confidence', 0)
            }
            
            calibrated_predictions.append(calibrated_pred)
        
        return calibrated_predictions


def fit_calibrator_from_model(classifier,
                               X: np.ndarray,
                               y: np.ndarray,
                               class_labels: List[str]) -> Tuple[ConfidenceCalibrator, Dict]:
    """
    Fit calibrator using cross-validation predictions
    
    Args:
        classifier: Trained MLIntentClassifier
        X: Feature matrix
        y: True labels
        class_labels: List of class labels
        
    Returns:
        (calibrator, results)
    """
    from sklearn.model_selection import cross_val_predict
    
    logger.info("Fitting calibrator using cross-validation predictions...")
    
    probabilities = cross_val_predict(
        classifier.model, X, y, 
        method='predict_proba', 
        cv=5
    )
    
    calibrator = ConfidenceCalibrator()
    calibrator.set_class_labels(class_labels)
    
    fit_results = calibrator.fit(probabilities, y)
    
    ece_result = calibrator.expected_calibration_error(probabilities, y)
    fit_results['ece_before'] = ece_result['ece']
    
    calibrated_probs = calibrator.calibrate(probabilities)
    ece_after = calibrator.expected_calibration_error(calibrated_probs, y)
    fit_results['ece_after'] = ece_after['ece']
    
    logger.info(f"  ECE before calibration: {ece_result['ece']:.4f}")
    logger.info(f"  ECE after calibration: {ece_after['ece']:.4f}")
    
    return calibrator, fit_results
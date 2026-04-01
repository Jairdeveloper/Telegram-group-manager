import os
import json
import hashlib
import joblib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class ModelSerializationManager:
    """Manager para serialización y versionado de modelos"""

    DEFAULT_MODELS_DIR = "models"
    
    MODEL_FILES = {
        'intent_classifier': 'intent_classifier.joblib',
        'feature_extractor': 'feature_extractor.joblib',
        'confidence_calibrator': 'confidence_calibrator.joblib',
        'metadata': 'metadata.json'
    }

    def __init__(self, models_dir: str = DEFAULT_MODELS_DIR):
        self.models_dir = models_dir
        self._ensure_models_dir()

    def _ensure_models_dir(self):
        """Crear directorio de models si no existe"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            logger.info(f"Created models directory: {self.models_dir}")

    def _calculate_checksum(self, filepath: str) -> str:
        """Calcular MD5 checksum de un archivo"""
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def save_model(self, model: Any, model_name: str) -> Dict[str, str]:
        """
        Guardar modelo individual con checksum
        
        Args:
            model: Modelo a guardar
            model_name: Nombre del modelo
            
        Returns:
            Dict con filepath y checksum
        """
        filename = self.MODEL_FILES.get(model_name, f"{model_name}.joblib")
        filepath = os.path.join(self.models_dir, filename)
        
        joblib.dump(model, filepath)
        checksum = self._calculate_checksum(filepath)
        
        logger.info(f"Saved {model_name} to {filepath}")
        logger.info(f"Checksum: {checksum}")
        
        return {
            'filepath': filepath,
            'checksum': checksum,
            'filename': filename
        }

    def load_model(self, model_name: str, verify_checksum: bool = True) -> Optional[Any]:
        """
        Cargar modelo individual
        
        Args:
            model_name: Nombre del modelo
            verify_checksum: Verificar checksum antes de cargar
            
        Returns:
            Modelo cargado o None si no existe
        """
        filename = self.MODEL_FILES.get(model_name, f"{model_name}.joblib")
        filepath = os.path.join(self.models_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Model not found: {filepath}")
            return None
        
        if verify_checksum:
            metadata = self.load_metadata()
            if metadata and model_name in metadata.get('models', {}):
                stored_checksum = metadata['models'][model_name].get('checksum', '')
                current_checksum = self._calculate_checksum(filepath)
                
                if stored_checksum != current_checksum:
                    logger.error(f"Checksum mismatch for {model_name}!")
                    return None
        
        model = joblib.load(filepath)
        logger.info(f"Loaded {model_name} from {filepath}")
        
        return model

    def save_all_models(self, 
                       intent_classifier: Any = None,
                       feature_extractor: Any = None,
                       confidence_calibrator: Any = None,
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Guardar todos los modelos del pipeline
        
        Args:
            intent_classifier: MLIntentClassifier entrenado
            feature_extractor: FeatureExtractor ajustado
            confidence_calibrator: ConfidenceCalibrator entrenado
            metadata: Metadatos adicionales
            
        Returns:
            Dict con resultados de guardado
        """
        results = {}
        timestamp = datetime.now().isoformat()
        
        if intent_classifier:
            result = self.save_model(intent_classifier, 'intent_classifier')
            results['intent_classifier'] = result
        
        if feature_extractor:
            result = self.save_model(feature_extractor, 'feature_extractor')
            results['feature_extractor'] = result
        
        if confidence_calibrator:
            result = self.save_model(confidence_calibrator, 'confidence_calibrator')
            results['confidence_calibrator'] = result
        
        metadata_info = {
            'version': '1.0',
            'timestamp': timestamp,
            'models': {},
            'pipeline_version': 'FASE2'
        }
        
        for model_name, result in results.items():
            metadata_info['models'][model_name] = {
                'filepath': result['filepath'],
                'checksum': result['checksum'],
                'saved_at': timestamp
            }
        
        if metadata:
            metadata_info.update(metadata)
        
        self.save_metadata(metadata_info)
        
        logger.info(f"All models saved successfully. Total: {len(results)}")
        
        return results

    def load_all_models(self) -> Dict[str, Any]:
        """
        Cargar todos los modelos del pipeline
        
        Returns:
            Dict con todos los modelos cargados
        """
        models = {}
        
        models['intent_classifier'] = self.load_model('intent_classifier')
        models['feature_extractor'] = self.load_model('feature_extractor')
        models['confidence_calibrator'] = self.load_model('confidence_calibrator')
        
        loaded_count = sum(1 for m in models.values() if m is not None)
        logger.info(f"Loaded {loaded_count}/3 models")
        
        return models

    def save_metadata(self, metadata: Dict[str, Any]) -> str:
        """Guardar metadatos"""
        filepath = os.path.join(self.models_dir, self.MODEL_FILES['metadata'])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved to {filepath}")
        return filepath

    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """Cargar metadatos"""
        filepath = os.path.join(self.models_dir, self.MODEL_FILES['metadata'])
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        logger.info(f"Metadata loaded from {filepath}")
        return metadata

    def verify_models(self) -> Dict[str, Any]:
        """
        Verificar integridad de todos los modelos
        
        Returns:
            Dict con resultados de verificación
        """
        metadata = self.load_metadata()
        
        if not metadata:
            return {
                'status': 'no_metadata',
                'models': {}
            }
        
        results = {}
        all_valid = True
        
        for model_name in ['intent_classifier', 'feature_extractor', 'confidence_calibrator']:
            filename = self.MODEL_FILES.get(model_name, f"{model_name}.joblib")
            filepath = os.path.join(self.models_dir, filename)
            
            if not os.path.exists(filepath):
                results[model_name] = {'status': 'missing'}
                all_valid = False
                continue
            
            current_checksum = self._calculate_checksum(filepath)
            stored_checksum = metadata.get('models', {}).get(model_name, {}).get('checksum', '')
            
            if current_checksum == stored_checksum:
                results[model_name] = {'status': 'valid', 'checksum': current_checksum}
            else:
                results[model_name] = {'status': 'checksum_mismatch', 'expected': stored_checksum, 'actual': current_checksum}
                all_valid = False
        
        return {
            'status': 'valid' if all_valid else 'invalid',
            'models': results,
            'timestamp': metadata.get('timestamp', 'unknown')
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información de todos los modelos"""
        metadata = self.load_metadata()
        
        info = {
            'models_dir': self.models_dir,
            'models': {}
        }
        
        if metadata:
            info['metadata'] = metadata
            info['version'] = metadata.get('version', 'unknown')
            info['timestamp'] = metadata.get('timestamp', 'unknown')
        
        for model_name in ['intent_classifier', 'feature_extractor', 'confidence_calibrator']:
            filename = self.MODEL_FILES.get(model_name, f"{model_name}.joblib")
            filepath = os.path.join(self.models_dir, filename)
            
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                info['models'][model_name] = {
                    'filepath': filepath,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
        
        return info


def serialize_pipeline(intent_classifier=None,
                       feature_extractor=None,
                       confidence_calibrator=None,
                       models_dir: str = "models") -> Dict[str, Any]:
    """
    Función convenience para serializar todo el pipeline
    
    Args:
        intent_classifier: ML model
        feature_extractor: Feature extractor
        confidence_calibrator: Calibrator
        models_dir: Directorio de salida
        
    Returns:
        Result summary
    """
    manager = ModelSerializationManager(models_dir)
    
    results = manager.save_all_models(
        intent_classifier=intent_classifier,
        feature_extractor=feature_extractor,
        confidence_calibrator=confidence_calibrator
    )
    
    verification = manager.verify_models()
    
    return {
        'saved_models': list(results.keys()),
        'verification': verification,
        'info': manager.get_model_info()
    }
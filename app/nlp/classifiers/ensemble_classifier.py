import logging
from typing import Dict, Any, Optional, List
import asyncio

logger = logging.getLogger(__name__)


class RegexIntentClassifier:
    """Clasificador basado en regex/keywords (Baseline de FASE 1)"""

    INTENT_PATTERNS = {
        'set_welcome': [
            r'cambiar.*bienvenida', r'mensaje.*bienvenida', r'welcome.*message',
            r'configurar.*bienvenida', r'modificar.*bienvenida', r'set.*welcome',
            r'cambiar.*saludo', r'mensaje.*saludo', r'editar.*bienvenida',
            r'bienvenida:\s*', r'establecer.*bienvenida', r'nuevo.*bienvenida',
            r'poner.*bienvenida', r'establecer.*mensaje.*entrada'
        ],
        'set_goodbye': [
            r'cambiar.*despedida', r'mensaje.*despedida', r'goodbye.*message',
            r'configurar.*despedida', r'modificar.*despedida', r'set.*goodbye',
            r'cambiar.*salida', r'mensaje.*salida', r'editar.*despedida',
            r'despedida:\s*', r'establecer.*despedida', r'nueva.*despedida'
        ],
        'toggle_feature': [
            r'\bactivar\b', r'\bdesactivar\b', r'\benable\b', r'\bdisable\b', r'\btoggle\b',
            r'\bencender\b', r'\bapagar\b', r'turn.*on\b', r'turn.*off\b',
            r'modo.*oscuro', r'modo.*mantenimiento',
            r'\bactiva\b', r'\bdesactiva\b', r'\bactive\b', r'\bdesactive\b',
            r'\bpon\b', r'\bquit\b', r'\bon\b', r'\boff\b',
            r'\benciende\b', r'\bapaga\b'
        ],
        'set_limit': [
            r'limite.*mensajes', r'mensajes.*limite', r'poner.*limite',
            r'configurar.*limite', r'ajustar.*limite', r'limite.*segundos',
            r'antiflood.*limite', r'flood.*limite', r'pon.*limite',
            r'limite de \d+', r'\d+.*mensajes', r'\d+.*segundos'
        ],
        'add_filter': [
            r'\bbloquear\b', r'agregar.*filtro', r'add.*filter', r'\bblock\b',
            r'\bfiltrar\b', r'crear.*filtro', r'anadir.*filtro', r'blacklist',
            r'\bbloquea\b', r'\bbloqueo\b', r'palabra.*bloquear',
            r'bloquear.*palabra', r'agregar.*palabra', r'aniadir.*palabra'
        ],
        'remove_filter': [
            r'\bdesbloquear\b', r'quitar.*filtro', r'remove.*filter', r'unblock',
            r'eliminar.*filtro', r'borrar.*filtro', r'whitelist',
            r'\bdesbloquea\b', r'\beliminar\b', r'\bquitar\b',
            r'\bborrar\b', r'desbloquear.*palabra'
        ],
        'get_status': [
            r'ver.*estado\b', r'estado.*sistema\b', r'\bget.*status\b', r'\bcheck.*status\b',
            r'\bcomo.*esta\b', r'\bhow.*is\b', r'\bmonitoring\b', r'verificar.*estado\b',
            r'estado.*bienvenida', r'estado.*antiflood', r'estado.*filtro'
        ],
        'get_settings': [
            r'ver.*configuracion\b', r'\bget.*settings\b', r'\bpreferencias\b',
            r'configuracion.*actual\b', r'ver.*opciones\b', r'\blist.*settings\b',
            r'que.*configurado', r'cuales.*opciones'
        ],
        'update_config': [
            r'actualizar.*config', r'cambiar.*config', r'modificar.*config',
            r'update.*config', r'change.*settings', r'configure'
        ],
        'query_data': [
            r'buscar', r'consultar', r'query', r'search', r'obtener.*datos',
            r'ver.*datos', r'get.*data', r'recuperar'
        ],
        'execute_action': [
            r'ejecutar', r'iniciar', r'start', r'run', r'execute',
            r'launch', r'comenzar', r'perform'
        ],
        'create_task': [
            r'crear.*tarea', r'nueva.*tarea', r'create.*task', r'add.*task',
            r'nuevo.*proyecto', r'abrir.*ticket', r'generar.*orden'
        ],
        'delete_task': [
            r'eliminar.*tarea', r'borrar.*tarea', r'delete.*task', r'remove.*task',
            r'cancelar', r'cerrar.*ticket', r'descartar'
        ],
        'assign_role': [
            r'asignar.*rol', r'assign.*role', r'set.*role', r'dar.*permiso',
            r'configurar.*rol'
        ],
        'grant_permission': [
            r'otorgar.*permiso', r'grant.*permission', r'allow.*access',
            r'permitir', r'dar.*acceso'
        ],
        'revoke_permission': [
            r'revocar.*permiso', r'revoke.*permission', r'deny.*access',
            r'remover.*permiso', r'quitar.*acceso'
        ]
    }

    def __init__(self):
        self.intents = list(self.INTENT_PATTERNS.keys())
        self._build_regex()

    def _build_regex(self):
        """Compilar patrones regex"""
        import re
        self.compiled_patterns = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predecir intent usando regex patterns
        
        Returns:
            {
                'intent': str,
                'confidence': float (0.0-1.0),
                'method': 'regex_classifier'
            }
        """
        text_lower = text.lower()
        scores = {}
        
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(text_lower):
                    score += 1
            scores[intent] = score
        
        max_score = max(scores.values()) if scores else 0
        
        if max_score == 0:
            return {
                'intent': None,
                'confidence': 0.0,
                'method': 'regex_classifier'
            }
        
        best_intent = max(scores.items(), key=lambda x: x[1])[0]
        confidence = min(max_score / 3, 1.0)
        
        all_scores = {k: v / max_score for k, v in scores.items() if v > 0}
        
        return {
            'intent': best_intent,
            'confidence': confidence,
            'probabilities': all_scores,
            'method': 'regex_classifier'
        }


class LLMIntentClassifier:
    """Fallback classifier usando LLM"""

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self.available = False

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predecir intent usando LLM con timeout
        
        Returns:
            {
                'intent': str,
                'confidence': float,
                'method': 'llm_fallback'
            }
        """
        logger.warning(f"LLM fallback requested for: {text[:50]}...")
        
        return {
            'intent': None,
            'confidence': 0.0,
            'method': 'llm_fallback',
            'error': 'LLM not available'
        }

    def predict_sync(self, text: str) -> Dict[str, Any]:
        """Versión síncrona con timeout"""
        return self.predict(text)


class EnsembleIntentClassifier:
    """Ensemble de múltiples clasificadores con fallback"""

    def __init__(self, 
                 ml_classifier=None,
                 regex_classifier=None,
                 llm_classifier=None,
                 ml_weight: float = 0.5,
                 regex_weight: float = 0.5,
                 timeout_llm: float = 2.0):
        
        self.ml_classifier = ml_classifier
        self.regex_classifier = regex_classifier or RegexIntentClassifier()
        self.llm_classifier = llm_classifier or LLMIntentClassifier(timeout=timeout_llm)
        
        self.ml_weight = ml_weight
        self.regex_weight = regex_weight
        self.timeout_llm = timeout_llm
        
        self.high_confidence_threshold = 0.75
        self.medium_confidence_threshold = 0.50

    def predict(self, text: str, tokenization_result=None) -> Dict[str, Any]:
        """
        Pipeline de predicción con fallback inteligente
        
        Flujo:
        1. Try regex classifier first (baseline)
        2. If regex has good confidence: return regex
        3. If ML classifier available with features: try ML
        4. If ML + regex agreement: return ensemble
        5. If low confidence: Try LLM fallback
        6. Else: Return best available
        
        Returns:
            {
                'intent': str,
                'confidence': float,
                'method': str,
                'confidence_level': str
            }
        """
        # Always try regex first (baseline classifier)
        regex_result = self.regex_classifier.predict(text)
        regex_confidence = regex_result.get('confidence', 0.0)
        regex_intent = regex_result.get('intent')

        logger.debug(f"Regex confidence: {regex_confidence:.2f}, intent: {regex_intent}")

        # If regex has high confidence, return it directly
        if regex_confidence >= self.high_confidence_threshold and regex_intent:
            return {
                'intent': regex_intent,
                'confidence': regex_confidence,
                'probabilities': regex_result.get('probabilities', {}),
                'method': 'regex_classifier',
                'confidence_level': 'high'
            }

        # Try ML classifier if tokenization_result provided
        ml_result = None
        ml_confidence = 0.0
        
        if self.ml_classifier and tokenization_result is not None:
            try:
                features = self.ml_classifier._feature_extractor.extract(tokenization_result)
                ml_result = self.ml_classifier.predict(features)
                ml_confidence = ml_result.get('confidence', 0.0)
            except Exception as e:
                logger.warning(f"ML classifier failed: {e}")
                ml_confidence = 0.0

        logger.debug(f"ML confidence: {ml_confidence:.2f}")

        # If ML has high confidence, return it
        if ml_confidence >= self.high_confidence_threshold:
            return {
                'intent': ml_result.get('intent'),
                'confidence': ml_result.get('confidence', ml_confidence),
                'probabilities': ml_result.get('probabilities', {}),
                'method': ml_result.get('method', 'ml_classifier'),
                'confidence_level': 'high'
            }

        # Check for agreement between ML and regex
        ml_intent = ml_result.get('intent') if ml_result else None
        
        if ml_intent and regex_intent and ml_intent == regex_intent:
            return {
                'intent': ml_intent,
                'confidence': (ml_confidence + regex_confidence) / 2,
                'probabilities': ml_result.get('probabilities', {}),
                'method': 'ensemble_agreement',
                'confidence_level': 'medium'
            }

        # If regex has medium confidence, return it
        if regex_confidence >= self.medium_confidence_threshold and regex_intent:
            return {
                'intent': regex_intent,
                'confidence': regex_confidence,
                'probabilities': regex_result.get('probabilities', {}),
                'method': 'regex_classifier',
                'confidence_level': 'medium'
            }

        # If ML has medium confidence, return it
        if ml_confidence >= self.medium_confidence_threshold and ml_intent:
            return {
                'intent': ml_intent,
                'confidence': ml_confidence,
                'probabilities': ml_result.get('probabilities', {}),
                'method': ml_result.get('method', 'ml_classifier'),
                'confidence_level': 'medium'
            }

        # If regex has any intent found, use it with lower confidence
        if regex_intent:
            return {
                'intent': regex_intent,
                'confidence': regex_confidence,
                'probabilities': regex_result.get('probabilities', {}),
                'method': 'regex_classifier',
                'confidence_level': 'low'
            }

        # Try LLM fallback as last resort
        logger.warning(f"Low confidence (regex: {regex_confidence:.2f}, ml: {ml_confidence:.2f}), attempting LLM fallback")

        llm_result = self.llm_classifier.predict_sync(text)
        
        if llm_result.get('intent') is not None:
            return {
                **llm_result,
                'confidence_level': 'low_llm_fallback'
            }

        return {
            'intent': None,
            'confidence': 0.0,
            'method': 'human_review_queue',
            'confidence_level': 'failed',
            'ml_confidence': ml_confidence,
            'regex_confidence': regex_confidence
        }

    def set_ml_classifier(self, ml_classifier):
        """Set ML classifier after initialization"""
        self.ml_classifier = ml_classifier

    def classify(self, text: str, tokenization_result=None) -> tuple:
        """
        Adapter method that wraps predict() to return a tuple compatible with legacy code.
        
        Returns:
            Tuple[str or None, float]: (intent, confidence)
        """
        result = self.predict(text, tokenization_result)
        intent = result.get('intent')
        confidence = result.get('confidence', 0.0)
        return intent, confidence
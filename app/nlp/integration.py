import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActionParseResult:
    action_id: Optional[str]
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    reason: str = ""


class NLPBotIntegration:
    def __init__(self, config: Optional[Any] = None, min_confidence: float = 0.30):
        from app.nlp.pipeline import PipelineConfig
        self.config = config or PipelineConfig()
        self.min_confidence = min_confidence
        self._pipeline = None
        self._classifier = None
        logger.info("NLPBotIntegration initialized")

    @property
    def pipeline(self):
        if self._pipeline is None:
            from app.nlp.pipeline import NLPPipeline
            self._pipeline = NLPPipeline(self.config)
        return self._pipeline

    @property
    def classifier(self):
        if self._classifier is None:
            from app.nlp.classifiers.ensemble_classifier import EnsembleIntentClassifier
            from app.nlp.classifiers.ml_classifier import MLIntentClassifier
            
            # Inicializar ensemble con todos los componentes
            ml_classifier = MLIntentClassifier()  # Carga modelo entrenado
            
            self._classifier = EnsembleIntentClassifier(
                ml_classifier=ml_classifier,
                ml_weight=0.5,
                regex_weight=0.5
            )
        return self._classifier

    def should_use_nlp(self, text: str) -> bool:
        if not text or not text.strip():
            return False
        intent, confidence = self.classifier.classify(text)
        return intent is not None and confidence >= self.min_confidence

    def process_message(self, text: str):
        if not text or not text.strip():
            return None
        try:
            logger.debug(f"Processing message with NLP: {text}")
            result = self.pipeline.process(text)
            logger.info(f"NLP result: action={result.action_result.action_id}, confidence={result.action_result.confidence}")
            return result
        except Exception as e:
            logger.error(f"NLP processing failed: {e}")
            return None

    def get_action_for_message(self, text: str):
        result = self.process_message(text)
        if result and result.action_result.action_id:
            if result.action_result.confidence >= self.min_confidence:
                return result.action_result
        return None

    def classify_intent(self, text: str) -> tuple:
        if not text or not text.strip():
            return None, 0.0
        return self.classifier.classify(text)

    def is_nlp_command(self, text: str) -> bool:
        intent, confidence = self.classify_intent(text)
        return intent is not None and confidence >= self.min_confidence


_integration_instance: Optional[NLPBotIntegration] = None


def get_nlp_integration(config: Optional[Any] = None, min_confidence: float = 0.30) -> NLPBotIntegration:
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = NLPBotIntegration(config, min_confidence)
    return _integration_instance


def process_nlp_message(text: str):
    return get_nlp_integration().get_action_for_message(text)


def should_use_nlp(text: str) -> bool:
    return get_nlp_integration().should_use_nlp(text)

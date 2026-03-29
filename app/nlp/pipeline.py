import logging
from dataclasses import dataclass
from typing import Optional

from app.agent.actions.parser import ActionParseResult
from app.nlp.normalizer import TextNormalizer
from app.nlp.tokenizer import NLPTokenizer
from app.nlp.intent_classifier import IntentClassifier
from app.nlp.ner import EntityExtractor
from app.nlp.action_mapper import ActionMapper
from app.nlp.exceptions import PipelineError, PipelineConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    use_normalizer: bool = True
    use_tokenizer: bool = True
    use_intent_classifier: bool = True
    use_entity_extractor: bool = True
    use_action_mapper: bool = True
    enable_llm_fallback: bool = True
    min_confidence_threshold: float = 0.5


@dataclass
class PipelineResult:
    action_result: ActionParseResult
    normalized_text: str
    tokens: list
    intent: Optional[str]
    intent_confidence: float
    entities: list
    pipeline_used: bool
    fallback_used: bool


class NLPPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self._initialize_components()
        logger.info("NLPPipeline initialized")

    def _initialize_components(self) -> None:
        try:
            self.normalizer = TextNormalizer() if self.config.use_normalizer else None
            self.tokenizer = NLPTokenizer() if self.config.use_tokenizer else None
            self.intent_classifier = IntentClassifier() if self.config.use_intent_classifier else None
            self.entity_extractor = EntityExtractor() if self.config.use_entity_extractor else None
            self.action_mapper = ActionMapper() if self.config.use_action_mapper else None

            logger.info("All NLP components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLP components: {e}")
            raise PipelineConfigurationError(f"Pipeline initialization failed: {e}")

    def process(self, text: str) -> PipelineResult:
        if not text or not text.strip():
            return PipelineResult(
                action_result=ActionParseResult(None, {}, 0.0, "empty_message"),
                normalized_text="",
                tokens=[],
                intent=None,
                intent_confidence=0.0,
                entities=[],
                pipeline_used=False,
                fallback_used=False,
            )

        logger.info(f"Processing text: {text}")

        normalized = self._normalize(text)
        tokens = self._tokenize(normalized)
        intent, intent_confidence = self._classify_intent(normalized)
        entities = self._extract_entities(normalized)

        action_result = self._map_action(text, intent)

        if action_result and action_result.action_id and action_result.confidence >= self.config.min_confidence_threshold:
            logger.info(f"Pipeline succeeded: {action_result.action_id}")
            return PipelineResult(
                action_result=action_result,
                normalized_text=normalized,
                tokens=tokens,
                intent=intent,
                intent_confidence=intent_confidence,
                entities=[e.value for e in entities],
                pipeline_used=True,
                fallback_used=False,
            )

        if self.config.enable_llm_fallback:
            logger.info("Confidence too low, attempting LLM fallback")
            llm_result = self._llm_fallback(text)
            if llm_result:
                return PipelineResult(
                    action_result=llm_result,
                    normalized_text=normalized,
                    tokens=tokens,
                    intent=intent,
                    intent_confidence=intent_confidence,
                    entities=[e.value for e in entities],
                    pipeline_used=True,
                    fallback_used=True,
                )

        logger.warning("Pipeline failed, returning no match")
        return PipelineResult(
            action_result=ActionParseResult(None, {}, 0.0, "no_match"),
            normalized_text=normalized,
            tokens=tokens,
            intent=intent,
            intent_confidence=intent_confidence,
            entities=[e.value for e in entities],
            pipeline_used=True,
            fallback_used=False,
        )

    def _normalize(self, text: str) -> str:
        if not self.normalizer:
            return text
        try:
            normalized = self.normalizer.normalize(text)
            logger.debug(f"Normalized: {normalized}")
            return normalized
        except Exception as e:
            logger.warning(f"Normalization failed: {e}, using original text")
            return text

    def _tokenize(self, text: str) -> list:
        if not self.tokenizer:
            return text.split()
        try:
            result = self.tokenizer.tokenize(text)
            logger.debug(f"Tokens: {result.tokens}")
            return result.tokens
        except Exception as e:
            logger.warning(f"Tokenization failed: {e}")
            return text.split()

    def _classify_intent(self, text: str) -> tuple:
        if not self.intent_classifier:
            return None, 0.0
        try:
            intent, confidence = self.intent_classifier.classify(text)
            logger.debug(f"Intent: {intent} ({confidence})")
            return intent, confidence
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return None, 0.0

    def _extract_entities(self, text: str) -> list:
        if not self.entity_extractor:
            return []
        try:
            entities = self.entity_extractor.extract(text)
            logger.debug(f"Entities: {[e.value for e in entities]}")
            return entities
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return []

    def _map_action(self, original_text: str, intent: Optional[str]) -> Optional[ActionParseResult]:
        if not self.action_mapper:
            return None
        try:
            action_result = self.action_mapper.map(original_text, intent)
            logger.debug(f"Action mapped: {action_result.action_id}")
            return action_result
        except Exception as e:
            logger.warning(f"Action mapping failed: {e}")
            return None

    def _llm_fallback(self, text: str) -> Optional[ActionParseResult]:
        try:
            from app.agent.actions.parser import ActionParser
            parser = ActionParser()
            result = parser._llm_parse(text)
            if result:
                logger.info("LLM fallback succeeded")
            return result
        except Exception as e:
            logger.warning(f"LLM fallback failed: {e}")
            return None

    def process_simple(self, text: str) -> ActionParseResult:
        return self.process(text).action_result


_pipeline_instance: Optional[NLPPipeline] = None

def get_pipeline(config: Optional[PipelineConfig] = None) -> NLPPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = NLPPipeline(config)
    return _pipeline_instance

def process_text(text: str) -> ActionParseResult:
    return get_pipeline().process_simple(text)

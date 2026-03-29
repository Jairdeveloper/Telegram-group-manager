import pytest
from app.nlp.pipeline import (
    NLPPipeline, PipelineConfig, PipelineResult, 
    get_pipeline, process_text
)
from app.agent.actions.parser import ActionParseResult


class TestPipelineConfig:
    def test_default_config(self):
        config = PipelineConfig()
        assert config.use_normalizer == True
        assert config.use_tokenizer == True
        assert config.use_intent_classifier == True
        assert config.use_entity_extractor == True
        assert config.use_action_mapper == True
        assert config.enable_llm_fallback == True
        assert config.min_confidence_threshold == 0.5

    def test_custom_config(self):
        config = PipelineConfig(
            use_normalizer=False,
            enable_llm_fallback=False,
            min_confidence_threshold=0.7
        )
        assert config.use_normalizer == False
        assert config.enable_llm_fallback == False
        assert config.min_confidence_threshold == 0.7


class TestNLPPipeline:
    def setup_method(self):
        self.pipeline = NLPPipeline()

    def test_process_empty_text(self):
        result = self.pipeline.process("")
        assert result.action_result.action_id is None
        assert result.action_result.confidence == 0.0
        assert result.normalized_text == ""
        assert result.pipeline_used == False

    def test_process_whitespace_text(self):
        result = self.pipeline.process("   ")
        assert result.action_result.action_id is None
        assert result.pipeline_used == False

    def test_process_welcome_set_text(self):
        result = self.pipeline.process("bienvenida: Hola bienvenido")
        assert result.action_result.action_id == "welcome.set_text"
        assert result.action_result.payload.get("text") == "Hola bienvenido"
        assert result.pipeline_used == True
        assert result.intent is not None

    def test_process_welcome_toggle_on(self):
        result = self.pipeline.process("activa bienvenida")
        assert result.action_result.action_id == "welcome.toggle"
        assert result.action_result.payload.get("enabled") == True
        assert result.pipeline_used == True

    def test_process_welcome_toggle_off(self):
        result = self.pipeline.process("desactiva bienvenida")
        assert result.action_result.action_id == "welcome.toggle"
        assert result.action_result.payload.get("enabled") == False

    def test_process_antiflood_limits(self):
        result = self.pipeline.process("pon limite de 10 mensajes en 5 segundos")
        assert result.action_result.action_id == "antiflood.set_limits"
        assert result.action_result.payload.get("limit") == 10
        assert result.action_result.payload.get("interval") == 5

    def test_process_antiflood_toggle(self):
        result = self.pipeline.process("desactiva antiflood")
        assert result.action_result.action_id == "antiflood.toggle"
        assert result.action_result.payload.get("enabled") == False

    def test_process_antispam_toggle(self):
        result = self.pipeline.process("activa antispam")
        assert result.action_result.action_id == "antispam.toggle"
        assert result.action_result.payload.get("enabled") == True

    def test_process_add_filter(self):
        result = self.pipeline.process("bloquear palabra spam")
        assert result.action_result.action_id == "filter.add_word"
        assert "spam" in result.action_result.payload.get("word", "")

    def test_process_remove_filter(self):
        result = self.pipeline.process("desbloquea spam")
        assert result.action_result.action_id == "filter.remove_word"
        assert "spam" in result.action_result.payload.get("word", "")

    def test_process_goodbye_set_text(self):
        result = self.pipeline.process("despedida: Hasta luego")
        assert result.action_result.action_id == "goodbye.set_text"
        assert result.action_result.payload.get("text") == "Hasta luego"

    def test_process_goodbye_toggle(self):
        result = self.pipeline.process("desactiva despedida")
        assert result.action_result.action_id == "goodbye.toggle"
        assert result.action_result.payload.get("enabled") == False

    def test_normalized_text_produced(self):
        result = self.pipeline.process("ACTIVA BIENVENIDA")
        assert result.normalized_text == "activa bienvenida"

    def test_tokens_produced(self):
        result = self.pipeline.process("activa bienvenida")
        assert len(result.tokens) > 0
        assert "activa" in result.tokens or "bienvenida" in result.tokens

    def test_intent_detected(self):
        result = self.pipeline.process("bloquear palabra spam")
        assert result.intent == "add_filter"
        assert result.intent_confidence > 0.0

    def test_entities_extracted(self):
        result = self.pipeline.process("pon limite de 10 mensajes en 5 segundos")
        assert isinstance(result.entities, list)


class TestProcessSimple:
    def setup_method(self):
        self.pipeline = NLPPipeline()

    def test_process_simple_returns_action_parse_result(self):
        result = self.pipeline.process_simple("activa bienvenida")
        assert isinstance(result, ActionParseResult)
        assert result.action_id is not None


class TestGetPipeline:
    def test_get_pipeline_returns_pipeline(self):
        pipeline = get_pipeline()
        assert isinstance(pipeline, NLPPipeline)

    def test_get_pipeline_same_instance(self):
        pipeline1 = get_pipeline()
        pipeline2 = get_pipeline()
        assert pipeline1 is pipeline2


class TestProcessTextFunction:
    def test_process_text_function(self):
        result = process_text("activa bienvenida")
        assert isinstance(result, ActionParseResult)
        assert result.action_id == "welcome.toggle"


class TestPipelineSpanish:
    def setup_method(self):
        self.pipeline = NLPPipeline()

    def test_spanish_commands(self):
        test_cases = [
            "bienvenida: Hola mundo",
            "desactiva antiflood",
            "bloquear palabra virus",
            "despedida: Adios amigos",
        ]
        for text in test_cases:
            result = self.pipeline.process(text)
            assert result.action_result.action_id is not None, f"Failed for: {text}"


class TestPipelineConfidenceThreshold:
    def test_low_threshold(self):
        config = PipelineConfig(min_confidence_threshold=0.3)
        pipeline = NLPPipeline(config)
        result = pipeline.process("activa bienvenida")
        assert result.action_result.action_id is not None

    def test_high_threshold(self):
        config = PipelineConfig(min_confidence_threshold=0.99)
        pipeline = NLPPipeline(config)
        result = pipeline.process("activa bienvenida")
        assert result.action_result.action_id is None or result.fallback_used


class TestPipelineResult:
    def test_pipeline_result_dataclass(self):
        result = PipelineResult(
            action_result=ActionParseResult("test.action", {}, 0.9, "test"),
            normalized_text="test text",
            tokens=["test", "text"],
            intent="test_intent",
            intent_confidence=0.9,
            entities=["test"],
            pipeline_used=True,
            fallback_used=False,
        )
        assert result.action_result.action_id == "test.action"
        assert result.normalized_text == "test text"
        assert result.pipeline_used == True
        assert result.fallback_used == False

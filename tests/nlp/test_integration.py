import pytest
from app.nlp.integration import (
    NLPBotIntegration, get_nlp_integration, 
    process_nlp_message, should_use_nlp
)
from app.nlp.pipeline import PipelineConfig


class TestNLPBotIntegration:
    def setup_method(self):
        self.integration = NLPBotIntegration()

    def test_should_use_nlp_with_valid_intent(self):
        assert self.integration.should_use_nlp("activa bienvenida") == True
        assert self.integration.should_use_nlp("desactiva antiflood") == True

    def test_should_use_nlp_with_no_intent(self):
        assert self.integration.should_use_nlp("hola que tal") == False

    def test_should_use_nlp_with_empty_text(self):
        assert self.integration.should_use_nlp("") == False
        assert self.integration.should_use_nlp("   ") == False

    def test_should_use_nlp_with_low_confidence(self):
        integration = NLPBotIntegration(min_confidence=0.99)
        assert integration.should_use_nlp("activa bienvenida") == False

    def test_process_message(self):
        result = self.integration.process_message("activa bienvenida")
        assert result is not None
        assert result.action_result.action_id == "welcome.toggle"

    def test_process_message_empty(self):
        result = self.integration.process_message("")
        assert result is None

    def test_get_action_for_message(self):
        action = self.integration.get_action_for_message("bienvenida: Hola mundo")
        assert action is not None
        assert action.action_id == "welcome.set_text"
        assert action.payload.get("text") == "Hola mundo"

    def test_get_action_for_message_low_confidence(self):
        integration = NLPBotIntegration(min_confidence=0.99)
        action = integration.get_action_for_message("activa bienvenida")
        assert action is None

    def test_classify_intent(self):
        intent, confidence = self.integration.classify_intent("bloquear palabra spam")
        assert intent == "add_filter"
        assert confidence > 0

    def test_is_nlp_command(self):
        assert self.integration.is_nlp_command("desactiva antiflood") == True
        assert self.integration.is_nlp_command("hola mundo") == False


class TestGetNLPIntegration:
    def test_get_nlp_integration_returns_instance(self):
        integration = get_nlp_integration()
        assert isinstance(integration, NLPBotIntegration)

    def test_get_nlp_integration_same_instance(self):
        integration1 = get_nlp_integration()
        integration2 = get_nlp_integration()
        assert integration1 is integration2


class TestProcessNLPMessage:
    def test_process_nlp_message_function(self):
        action = process_nlp_message("activa bienvenida")
        assert action is not None
        assert action.action_id == "welcome.toggle"


class TestShouldUseNLP:
    def test_should_use_nlp_function(self):
        assert should_use_nlp("activa bienvenida") == True
        assert should_use_nlp("hola que tal") == False


class TestNLPBotIntegrationSpanish:
    def setup_method(self):
        self.integration = NLPBotIntegration()

    def test_spanish_commands(self):
        test_cases = [
            "bienvenida: Hola bienvenido",
            "desactiva antiflood", 
            "bloquear palabra spam",
            "pon limite de 5 mensajes",
        ]
        for text in test_cases:
            action = self.integration.get_action_for_message(text)
            assert action is not None, f"Failed for: {text}"


class TestNLPBotIntegrationConfig:
    def test_custom_config(self):
        config = PipelineConfig(
            use_normalizer=True,
            use_tokenizer=True,
            enable_llm_fallback=False,
            min_confidence_threshold=0.6
        )
        integration = NLPBotIntegration(config=config, min_confidence=0.6)
        assert integration.config.enable_llm_fallback == False
        assert integration.min_confidence == 0.6

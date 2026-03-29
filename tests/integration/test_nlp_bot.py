import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.agent.core import AgentCore, AgentContext
from app.agent.intent_router import IntentRouter, IntentKind
from app.nlp import NLPBotIntegration, should_use_nlp, process_nlp_message


class TestNLPBotIntegration:
    def setup_method(self):
        self.integration = NLPBotIntegration()

    def test_process_welcome_toggle(self):
        result = self.integration.get_action_for_message("activa bienvenida")
        assert result is not None
        assert result.action_id == "welcome.toggle"
        assert result.payload.get("enabled") == True

    def test_process_welcome_set_text(self):
        result = self.integration.get_action_for_message("bienvenida: Hola mundo")
        assert result is not None
        assert result.action_id == "welcome.set_text"
        assert result.payload.get("text") == "Hola mundo"

    def test_process_antiflood_limits(self):
        result = self.integration.get_action_for_message("pon limite de 10 mensajes en 5 segundos")
        assert result is not None
        assert result.action_id == "antiflood.set_limits"
        assert result.payload.get("limit") == 10
        assert result.payload.get("interval") == 5

    def test_process_filter_add(self):
        result = self.integration.get_action_for_message("bloquear palabra spam")
        assert result is not None
        assert result.action_id == "filter.add_word"
        assert "spam" in result.payload.get("word", "")

    def test_process_goodbye_set_text(self):
        result = self.integration.get_action_for_message("despedida: Hasta luego")
        assert result is not None
        assert result.action_id == "goodbye.set_text"
        assert result.payload.get("text") == "Hasta luego"

    def test_should_use_nlp_command(self):
        assert self.integration.should_use_nlp("activa bienvenida") == True
        assert self.integration.should_use_nlp("desactiva antiflood") == True

    def test_should_not_use_nlp_chat(self):
        assert self.integration.should_use_nlp("hola que tal") == False
        assert self.integration.should_use_nlp("como estas") == False


class TestIntentRouterWithNLP:
    def setup_method(self):
        self.router = IntentRouter(nlp_enabled=True)

    def test_route_welcome_command(self):
        decision = self.router.route("activa bienvenida")
        assert decision.kind == IntentKind.BOT_ACTION
        assert decision.nlp_intent is not None

    def test_route_antiflood_command(self):
        decision = self.router.route("pon limite de 5 mensajes")
        assert decision.kind == IntentKind.BOT_ACTION

    def test_route_filter_command(self):
        decision = self.router.route("bloquear palabra virus")
        assert decision.kind == IntentKind.BOT_ACTION

    def test_route_help_request(self):
        decision = self.router.route("ayudame con los comandos")
        assert decision.kind in (IntentKind.HELP_REQUEST, IntentKind.BOT_ACTION)

    def test_route_chat_message(self):
        decision = self.router.route("hola que tal amigos")
        assert decision.kind == IntentKind.CHAT

    def test_route_agent_task(self):
        decision = self.router.route("buscar informacion sobre python")
        assert decision.kind in (IntentKind.AGENT_TASK, IntentKind.BOT_ACTION)


class TestProcessNLPMessage:
    def test_process_nlp_message_welcome(self):
        result = process_nlp_message("bienvenida: Hola bienvenido")
        assert result is not None
        assert result.action_id == "welcome.set_text"

    def test_process_nlp_message_antiflood(self):
        result = process_nlp_message("desactiva antiflood")
        assert result is not None
        assert result.action_id == "antiflood.toggle"

    def test_should_use_nlp_function(self):
        assert should_use_nlp("activa bienvenida") == True
        assert should_use_nlp("hola mundo") == False


class TestNLPCaching:
    def test_classify_intent_caching(self):
        from app.nlp.intent_classifier import classify_intent, clear_classify_cache
        
        clear_classify_cache()
        
        result1 = classify_intent("activa bienvenida")
        result2 = classify_intent("activa bienvenida")
        
        assert result1 == result2

    def test_classify_intent_different_texts(self):
        from app.nlp.intent_classifier import classify_intent, clear_classify_cache
        
        clear_classify_cache()
        
        result1 = classify_intent("bloquear palabra spam")
        result2 = classify_intent("desactiva antiflood")
        
        assert result1[0] != result2[0]  # Different intents


class TestNLPConfidenceThreshold:
    def test_high_threshold_rejects_low_confidence(self):
        from app.nlp import NLPBotIntegration, PipelineConfig
        
        integration = NLPBotIntegration(min_confidence=0.99)
        result = integration.get_action_for_message("activa bienvenida")
        assert result is None

    def test_normal_threshold_accepts_command(self):
        integration = NLPBotIntegration(min_confidence=0.5)
        result = integration.get_action_for_message("activa bienvenida")
        assert result is not None


class TestSpanishCommands:
    def test_spanish_welcome_commands(self):
        test_cases = [
            "bienvenida: Hola mundo",
            "Bienvenida con texto de prueba",
            "activa bienvenida",
            "desactiva bienvenida",
        ]
        for text in test_cases:
            result = process_nlp_message(text)
            assert result is not None, f"Failed for: {text}"

    def test_spanish_antiflood_commands(self):
        test_cases = [
            "pon limite de 5 mensajes en 3 segundos",
            "desactiva antiflood",
            "antiflood con mute",
        ]
        for text in test_cases:
            result = process_nlp_message(text)
            assert result is not None, f"Failed for: {text}"

    def test_spanish_filter_commands(self):
        test_cases = [
            "bloquear palabra spam",
            "bloquea palabra virus",
            "desbloquea spam",
            "eliminar palabra malos",
        ]
        for text in test_cases:
            result = process_nlp_message(text)
            assert result is not None, f"Failed for: {text}"


class TestNLPIntegrationE2E:
    def test_full_nlp_flow(self):
        from app.nlp import NLPBotIntegration
        
        integration = NLPBotIntegration()
        
        messages = [
            ("bienvenida: Hola bienvenido", "welcome.set_text"),
            ("activa bienvenida", "welcome.toggle"),
            ("desactiva antiflood", "antiflood.toggle"),
            ("pon limite de 10 mensajes en 5 segundos", "antiflood.set_limits"),
            ("bloquear palabra spam", "filter.add_word"),
            ("despedida: Hasta luego", "goodbye.set_text"),
        ]
        
        for message, expected_action in messages:
            result = integration.get_action_for_message(message)
            assert result is not None, f"Failed for: {message}"
            assert result.action_id == expected_action, f"Expected {expected_action}, got {result.action_id} for: {message}"

    def test_intent_classification_flow(self):
        from app.agent.intent_router import IntentRouter, IntentKind
        
        router = IntentRouter(nlp_enabled=True)
        
        test_cases = [
            ("activa bienvenida", IntentKind.BOT_ACTION),
            ("como esta el antiflood?", IntentKind.BOT_ACTION),
            ("ayudame por favor", IntentKind.HELP_REQUEST),
            ("hola que tal", IntentKind.CHAT),
        ]
        
        for message, expected_kind in test_cases:
            decision = router.route(message)
            assert decision.kind == expected_kind, f"Expected {expected_kind}, got {decision.kind} for: {message}"

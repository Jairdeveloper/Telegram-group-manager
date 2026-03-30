import pytest
from app.agent.intent_router import IntentRouter, IntentKind, IntentDecision, get_default_intent_router


class TestIntentRouter:
    def setup_method(self):
        self.router = IntentRouter(nlp_enabled=True)

    def test_route_empty_message(self):
        decision = self.router.route("")
        assert decision.kind == IntentKind.CHAT
        assert decision.confidence == 0.1

    def test_route_agent_task(self):
        decision = self.router.route("buscar informacion sobre python")
        assert decision.kind in (IntentKind.AGENT_TASK, IntentKind.BOT_ACTION)

    def test_route_chat(self):
        decision = self.router.route("hola que tal")
        assert decision.kind == IntentKind.CHAT

    def test_route_bot_action_welcome(self):
        decision = self.router.route("activa bienvenida")
        assert decision.kind == IntentKind.BOT_ACTION
        assert decision.nlp_intent is not None

    def test_route_bot_action_antiflood(self):
        decision = self.router.route("desactiva antiflood")
        assert decision.kind == IntentKind.BOT_ACTION
        assert decision.nlp_intent is not None

    def test_route_help_request(self):
        decision = self.router.route("ayudame con los comandos")
        assert decision.kind in (IntentKind.HELP_REQUEST, IntentKind.BOT_ACTION)


class TestIntentRouterNLP:
    def setup_method(self):
        self.router = IntentRouter(nlp_enabled=True)

    def test_nlp_classify_welcome(self):
        decision = self.router._nlp_classify("activa bienvenida")
        if decision:
            assert decision.kind == IntentKind.BOT_ACTION
            assert decision.confidence > 0

    def test_nlp_classify_status(self):
        decision = self.router._nlp_classify("como esta el antiflood configurado")
        if decision:
            assert decision.kind == IntentKind.BOT_ACTION
            assert decision.nlp_intent in ("get_status", "toggle_feature")

    def test_nlp_classify_help(self):
        decision = self.router._nlp_classify("ayudame con los comandos")
        if decision:
            assert decision.kind in (IntentKind.HELP_REQUEST, IntentKind.BOT_ACTION)

    def test_nlp_classify_settings(self):
        decision = self.router._nlp_classify("cuales son los filtros activos")
        if decision:
            assert decision.kind == IntentKind.BOT_ACTION

    def test_nlp_classify_returns_none_for_unknown(self):
        decision = self.router._nlp_classify("hola que tal amigos")
        assert decision is None


class TestIntentKind:
    def test_intent_kind_values(self):
        assert IntentKind.CHAT.value == "chat"
        assert IntentKind.AGENT_TASK.value == "agent_task"
        assert IntentKind.BOT_ACTION.value == "bot_action"
        assert IntentKind.HELP_REQUEST.value == "help_request"


class TestIntentDecision:
    def test_intent_decision_defaults(self):
        decision = IntentDecision(kind=IntentKind.CHAT)
        assert decision.kind == IntentKind.CHAT
        assert decision.reason == ""
        assert decision.confidence == 0.5
        assert decision.nlp_intent is None

    def test_intent_decision_with_nlp(self):
        decision = IntentDecision(
            kind=IntentKind.BOT_ACTION,
            reason="nlp_classification",
            confidence=0.85,
            nlp_intent="toggle_feature"
        )
        assert decision.kind == IntentKind.BOT_ACTION
        assert decision.nlp_intent == "toggle_feature"
        assert decision.confidence == 0.85


class TestGetDefaultIntentRouter:
    def test_get_default_intent_router(self):
        router = get_default_intent_router()
        assert isinstance(router, IntentRouter)

    def test_get_default_same_instance(self):
        router1 = get_default_intent_router()
        router2 = get_default_intent_router()
        assert router1 is router2


class TestIntentRouterSpanish:
    def setup_method(self):
        self.router = IntentRouter(nlp_enabled=True)

    def test_spanish_commands(self):
        test_cases = [
            ("bienvenida: Hola mundo", IntentKind.BOT_ACTION),
            ("desactiva antiflood", IntentKind.BOT_ACTION),
            ("bloquear palabra spam", IntentKind.BOT_ACTION),
            ("como esta el antiflood?", IntentKind.BOT_ACTION),
            ("ayudame con los comandos", IntentKind.HELP_REQUEST),
        ]
        for message, expected_kind in test_cases:
            decision = self.router.route(message)
            assert decision.kind == expected_kind, f"Failed for: {message}"

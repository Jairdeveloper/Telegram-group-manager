from app.agent.intent_router import IntentRouter, IntentKind


def test_intent_router_keywords_trigger_agent_task(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    router = IntentRouter()
    decision = router.route("buscar clima madrid")
    assert decision.kind == IntentKind.AGENT_TASK


def test_intent_router_defaults_to_chat(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    router = IntentRouter()
    decision = router.route("hola equipo")
    assert decision.kind == IntentKind.CHAT

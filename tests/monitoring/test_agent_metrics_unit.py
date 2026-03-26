from app.monitoring.agent_metrics import estimate_tokens, record_llm_usage


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") >= 1


def test_record_llm_usage_does_not_crash():
    record_llm_usage(
        provider="test",
        model="test-model",
        prompt="hola",
        response="respuesta",
        source="unit",
    )

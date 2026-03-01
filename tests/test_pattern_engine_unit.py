from chat_service.pattern_engine import PatternEngine


def test_pattern_engine_extracts_named_binding():
    engine = PatternEngine()
    pattern = ["i", "like", [1, "thing"], 0]
    bindings = engine.match(pattern, "i like python a lot")
    assert bindings is not None
    assert ["thing", "python"] in bindings


def test_pattern_engine_returns_none_when_no_match():
    engine = PatternEngine()
    pattern = ["hello"]
    bindings = engine.match(pattern, "goodbye")
    assert bindings is None


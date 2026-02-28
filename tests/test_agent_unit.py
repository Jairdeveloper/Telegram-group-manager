from chat_service.agent import Agent


def build_agent() -> Agent:
    pattern_responses = [
        [["hello", 0], ["Hello!", "It's", "nice", "to", "meet", "you"]],
        [["i", "like", [1, "thing"], 0], [[1, "thing"], "is", "great!"]],
    ]
    default_responses = [["default", "response"]]
    return Agent(pattern_responses, default_responses)


def test_agent_matches_pattern():
    agent = build_agent()
    response = agent.process("hello there")
    assert response.pattern_matched is True
    assert response.source == "pattern"
    assert "Hello!" in response.text


def test_agent_default_response_when_no_match():
    agent = build_agent()
    response = agent.process("texto sin patron")
    assert response.pattern_matched is False
    assert response.source == "default"
    assert response.text == "default response"

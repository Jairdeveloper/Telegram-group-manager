from fastapi.testclient import TestClient

from chatbot_monolith import create_api_app


def test_chat_endpoint_contract():
    app = create_api_app()
    client = TestClient(app)

    response = client.post("/api/v1/chat", params={"message": "hello", "session_id": "s1"})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "s1"
    assert body["message"] == "hello"
    assert isinstance(body["response"], str)
    assert isinstance(body["confidence"], float)
    assert "source" in body
    assert "pattern_matched" in body


def test_chat_rejects_empty_message():
    app = create_api_app()
    client = TestClient(app)

    response = client.post("/api/v1/chat", params={"message": "   "})
    assert response.status_code == 400


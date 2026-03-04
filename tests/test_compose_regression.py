from pathlib import Path


def test_worker_compose_has_chatbot_api_url_env():
    compose_path = Path(__file__).resolve().parents[1] / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")

    assert "worker:" in content
    assert "- CHATBOT_API_URL=http://chatapi:8000/api/v1/chat" in content

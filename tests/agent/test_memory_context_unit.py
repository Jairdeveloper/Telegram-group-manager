from app.agent.memory import MemorySystem
from app.agent.context import ContextBuilder


class FakeConversationRepository:
    def __init__(self):
        self.saved = []

    def save_message(self, tenant_id, session_id, user_message, bot_response, metadata=None):
        self.saved.append(
            {
                "tenant_id": tenant_id,
                "session_id": session_id,
                "user": user_message,
                "bot": bot_response,
                "metadata": metadata or {},
            }
        )

    def get_history(self, tenant_id, session_id, limit=50):
        items = [
            {
                "user": item["user"],
                "bot": item["bot"],
                "metadata": item["metadata"],
            }
            for item in self.saved
            if item["tenant_id"] == tenant_id and item["session_id"] == session_id
        ]
        return items[-limit:]


def test_memory_system_persists_and_limits_buffer():
    repo = FakeConversationRepository()
    memory = MemorySystem(repository=repo, max_messages=2)

    memory.add_exchange("default", "chat-1", "hola", "respuesta 1")
    memory.add_exchange("default", "chat-1", "como estas", "respuesta 2")
    memory.add_exchange("default", "chat-1", "otra", "respuesta 3")

    history = memory.get_history("default", "chat-1", limit=2)
    assert len(history) == 2
    assert history[-1]["bot"] == "respuesta 3"


def test_context_builder_renders_history():
    repo = FakeConversationRepository()
    memory = MemorySystem(repository=repo, max_messages=5)
    memory.add_exchange("default", "chat-2", "ping", "pong")

    builder = ContextBuilder(memory, max_messages=5)
    window = builder.build("default", "chat-2")
    rendered = window.render()
    assert "Usuario: ping" in rendered
    assert "Asistente: pong" in rendered

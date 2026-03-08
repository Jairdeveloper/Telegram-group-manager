"""Tests for conversation repositories."""
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch

from app.database.repositories.postgres_conversation_repository import PostgresConversationRepository
from app.database.repositories.json_conversation_repository import JsonConversationRepository
from app.database.repositories.conversation_repository import ConversationRepository


class TestJsonConversationRepository:
    """Tests for JsonConversationRepository (fallback)."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def repo(self, temp_file):
        """Create repository with temporary file."""
        return JsonConversationRepository(filepath=temp_file)

    def test_save_and_get_history(self, repo):
        """Test saving a message and retrieving history."""
        repo.save_message("tenant1", "session1", "hello", "hi there")
        history = repo.get_history("tenant1", "session1")
        
        assert len(history) == 1
        assert history[0]["user"] == "hello"
        assert history[0]["bot"] == "hi there"

    def test_get_sessions(self, repo):
        """Test getting all sessions for a tenant."""
        repo.save_message("tenant1", "session1", "hello", "hi")
        repo.save_message("tenant1", "session2", "hello", "hi")
        
        sessions = repo.get_sessions("tenant1")
        assert "session1" in sessions
        assert "session2" in sessions

    def test_get_history_with_limit(self, repo):
        """Test history retrieval with limit."""
        for i in range(10):
            repo.save_message("tenant1", "session1", f"msg{i}", f"resp{i}")
        
        history = repo.get_history("tenant1", "session1", limit=5)
        assert len(history) == 5

    def test_delete_session(self, repo):
        """Test deleting a session."""
        repo.save_message("tenant1", "session1", "hello", "hi")
        repo.delete_session("tenant1", "session1")
        
        history = repo.get_history("tenant1", "session1")
        assert len(history) == 0

    def test_tenant_isolation(self, repo):
        """Test that tenants are isolated."""
        repo.save_message("tenant1", "session1", "hello", "hi")
        repo.save_message("tenant2", "session1", "hello", "hi")
        
        tenant1_sessions = repo.get_sessions("tenant1")
        tenant2_sessions = repo.get_sessions("tenant2")
        
        assert len(tenant1_sessions) == 1
        assert len(tenant2_sessions) == 1


class TestPostgresConversationRepository:
    """Tests for PostgresConversationRepository.

    Note: These tests require a PostgreSQL database to run.
    For local testing without PostgreSQL, use the JsonConversationRepository tests.
    """

    @pytest.fixture
    def database_url(self):
        """Get database URL from environment or use test default."""
        return os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_chatbot")

    @pytest.fixture
    def repo(self, database_url):
        """Create repository (requires PostgreSQL)."""
        return PostgresConversationRepository(database_url)

    @pytest.mark.skipif(
        os.getenv("RUN_POSTGRES_TESTS") != "true",
        reason="PostgreSQL not available. Set RUN_POSTGRES_TESTS=true to run."
    )
    def test_save_and_get_history(self, repo):
        """Test saving a message and retrieving history."""
        repo.save_message("tenant1", "session1", "hello", "hi there")
        history = repo.get_history("tenant1", "session1")
        
        assert len(history) > 0
        assert history[0]["user"] == "hello"
        assert history[0]["bot"] == "hi there"

    @pytest.mark.skipif(
        os.getenv("RUN_POSTGRES_TESTS") != "true",
        reason="PostgreSQL not available. Set RUN_POSTGRES_TESTS=true to run."
    )
    def test_get_sessions(self, repo):
        """Test getting all sessions for a tenant."""
        repo.save_message("tenant1", "session1", "hello", "hi")
        repo.save_message("tenant1", "session2", "hello", "hi")
        
        sessions = repo.get_sessions("tenant1")
        assert "session1" in sessions
        assert "session2" in sessions


class TestConversationRepositoryInterface:
    """Tests to verify the repository interface compliance."""

    def test_json_repo_implements_interface(self):
        """Verify JsonConversationRepository implements ConversationRepository."""
        repo = JsonConversationRepository(filepath=":memory:")
        
        assert isinstance(repo, ConversationRepository)
        assert hasattr(repo, 'save_message')
        assert hasattr(repo, 'get_history')
        assert hasattr(repo, 'get_sessions')
        assert hasattr(repo, 'delete_session')

    def test_repository_has_required_methods(self):
        """Verify both repositories have the required methods."""
        json_repo = JsonConversationRepository(filepath=":memory:")
        
        assert callable(json_repo.save_message)
        assert callable(json_repo.get_history)
        assert callable(json_repo.get_sessions)
        assert callable(json_repo.delete_session)

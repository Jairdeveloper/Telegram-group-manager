"""Integration tests for Celery tasks."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any


class TestNLPIntegrationTasks:
    """Integration tests for NLP tasks."""

    @pytest.fixture
    def mock_nlp_integration(self):
        """Mock NLP integration."""
        with patch("app.tasks.nlp_tasks.get_nlp_integration") as mock:
            mock_integration = MagicMock()
            mock_integration.should_use_nlp.return_value = True
            mock_integration.process_message.return_value = MagicMock(
                intent="greet",
                action_result={"action": "respond", "confidence": 0.95}
            )
            mock.return_value = mock_integration
            yield mock

    def test_process_nlp_message_integration(self, mock_nlp_integration):
        """Test NLP message processing integration."""
        from app.tasks.nlp_tasks import process_nlp_message

        result = process_nlp_message("Hello", chat_id=123, update_id=1)

        assert result["status"] == "ok"
        assert result["intent"] == "greet"

    def test_process_batch_nlp_integration(self, mock_nlp_integration):
        """Test batch NLP processing integration."""
        from app.tasks.nlp_tasks import process_batch_nlp

        messages = [
            {"text": "Hello", "chat_id": 123, "update_id": 1},
            {"text": "How are you?", "chat_id": 123, "update_id": 2},
        ]

        results = process_batch_nlp(messages)

        assert len(results) == 2
        assert all(r["status"] == "ok" for r in results)


class TestAnalysisIntegrationTasks:
    """Integration tests for analysis tasks."""

    def test_analyze_message_basic(self):
        """Test basic message analysis."""
        from app.tasks.analysis_tasks import analyze_message

        message_data = {"text": "Hello, this is a test message!", "chat_id": 123}
        result = analyze_message(message_data)

        assert result["word_count"] == 6
        assert result["char_count"] > 0
        assert result["is_spam_likely"] is False

    def test_analyze_message_spam_detection(self):
        """Test spam detection in messages."""
        from app.tasks.analysis_tasks import analyze_message

        message_data = {
            "text": "http://spam.link Check this amazing offer now!!!",
            "chat_id": 123
        }
        result = analyze_message(message_data)

        assert result["is_spam_likely"] is True
        assert result["spam_reason"] == "link_spam"

    def test_analyze_batch(self):
        """Test batch analysis."""
        from app.tasks.analysis_tasks import analyze_batch

        messages = [
            {"text": "Hello", "chat_id": 123},
            {"text": "Test message", "chat_id": 123},
        ]

        results = analyze_batch(messages)

        assert len(results) == 2
        assert all("word_count" in r for r in results)


class TestMaintenanceIntegrationTasks:
    """Integration tests for maintenance tasks."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection."""
        with patch("app.tasks.maintenance_tasks.get_redis_connection") as mock:
            mock_conn = MagicMock()
            mock_conn.ping.return_value = True
            mock_conn.scan.return_value = (0, [])
            mock.return_value = mock_conn
            yield mock_conn

    def test_health_check_integration(self, mock_redis):
        """Test health check integration."""
        from app.tasks.maintenance_tasks import health_check

        result = health_check()

        assert result["status"] == "ok"
        assert "components" in result
        assert result["components"]["redis"] == "ok"

    def test_cleanup_old_data_integration(self, mock_redis):
        """Test cleanup old data integration."""
        from app.tasks.maintenance_tasks import cleanup_old_data

        result = cleanup_old_data(days=7)

        assert result["status"] == "ok"


class TestDatabaseIntegrationTasks:
    """Integration tests for database tasks."""

    @patch("app.tasks.db_tasks.ConversationRepository")
    @patch("app.tasks.db_tasks.MessageRepository")
    def test_fetch_conversations_integration(self, mock_msg_repo, mock_conv_repo):
        """Test fetch conversations integration."""
        from app.tasks.db_tasks import fetch_conversations

        mock_conv = MagicMock()
        mock_conv.id = 1
        mock_conv.user_id = 123
        mock_conv.text = "Test message"
        mock_conv.timestamp = None

        mock_conv_repo.return_value.get_by_chat_id.return_value = [mock_conv]

        result = fetch_conversations(chat_id=123, limit=10)

        assert result["status"] == "ok"
        assert result["chat_id"] == 123

    @patch("app.tasks.db_tasks.ConversationRepository")
    @patch("app.tasks.db_tasks.MessageRepository")
    def test_aggregate_statistics_integration(self, mock_msg_repo, mock_conv_repo):
        """Test aggregate statistics integration."""
        from app.tasks.db_tasks import aggregate_statistics

        mock_msg = MagicMock()
        mock_msg.user_id = 123
        mock_msg.text = "Test message"

        mock_msg_repo.return_value.get_by_chat_id.return_value = [mock_msg]
        mock_conv_repo.return_value.get_by_chat_id.return_value = []

        result = aggregate_statistics(chat_id=123, days=7)

        assert result["status"] == "ok"
        assert result["total_messages"] == 1


class TestTaskSignatures:
    """Tests for task signatures."""

    def test_nlp_pipeline_signature(self):
        """Test NLP pipeline signature creation."""
        from app.tasks.task_signatures import nlp_pipeline_signature

        sig = nlp_pipeline_signature(text="Hello", chat_id=123, update_id=1)

        assert sig is not None

    def test_analysis_pipeline_signature(self):
        """Test analysis pipeline signature creation."""
        from app.tasks.task_signatures import analysis_pipeline_signature

        message_data = {"text": "Test", "chat_id": 123}
        sig = analysis_pipeline_signature(message_data)

        assert sig is not None

    def test_db_pipeline_signature(self):
        """Test DB pipeline signature creation."""
        from app.tasks.task_signatures import db_pipeline_signature

        sig = db_pipeline_signature(chat_id=123, days=7)

        assert sig is not None

    def test_batch_analysis_signature(self):
        """Test batch analysis signature creation."""
        from app.tasks.task_signatures import batch_analysis_signature

        messages = [
            {"text": "Test 1", "chat_id": 123},
            {"text": "Test 2", "chat_id": 123},
        ]

        sig = batch_analysis_signature(messages)

        assert sig is not None

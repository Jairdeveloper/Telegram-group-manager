"""Tests for Celery application configuration."""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestCeleryAppConfiguration:
    """Test Celery application configuration."""

    def test_create_celery_app(self):
        """Test that Celery app is created successfully."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app is not None
            assert app.main == "robot"
            assert "app.tasks.nlp_tasks" in app.conf.task_routes

    def test_celery_app_has_correct_queues(self):
        """Test that task routes are configured correctly."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.task_routes["app.tasks.nlp_tasks.process_nlp_message"]["queue"] == "nlp"
            assert app.conf.task_routes["app.tasks.analysis_tasks.analyze_message"]["queue"] == "heavy"
            assert app.conf.task_routes["app.tasks.maintenance_tasks.cleanup_old_data"]["queue"] == "maintenance"

    def test_celery_app_default_queue(self):
        """Test default queue configuration."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.task_default_queue == "default"

    def test_celery_serializer_configuration(self):
        """Test serializer and result configurations."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.task_serializer == "json"
            assert app.conf.result_serializer == "json"
            assert app.conf.accept_content == ["json"]
            assert app.conf.timezone == "UTC"
            assert app.conf.enable_utc is True

    def test_celery_time_limits(self):
        """Test task time limits configuration."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.task_time_limit == 300
            assert app.conf.task_soft_time_limit == 240

    def test_celery_worker_settings(self):
        """Test worker settings configuration."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.worker_prefetch_multiplier == 4
            assert app.conf.worker_max_tasks_per_child == 1000

    def test_celery_result_expiration(self):
        """Test result expiration configuration."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert app.conf.result_expires == 3600

    def test_celery_beat_schedule(self):
        """Test beat schedule configuration."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import create_celery_app
            
            app = create_celery_app()
            
            assert "cleanup-old-data" in app.conf.beat_schedule
            assert "health-check" in app.conf.beat_schedule

    def test_get_celery_app_singleton(self):
        """Test that get_celery_app returns singleton."""
        with patch("app.celery_app.get_redis_config") as mock_redis:
            mock_redis.return_value = MagicMock(url="redis://localhost:6379/0")
            
            from app.celery_app import get_celery_app, _celery_app
            
            _celery_app = None
            
            app1 = get_celery_app()
            app2 = get_celery_app()
            
            assert app1 is app2


class TestCeleryConfigModule:
    """Test celeryconfig.py module."""

    def test_celeryconfig_exists(self):
        """Test that celeryconfig module can be imported."""
        import celeryconfig
        
        assert celeryconfig.broker_url is not None
        assert celeryconfig.result_backend is not None

    def test_celeryconfig_task_routes(self):
        """Test task routes in celeryconfig."""
        import celeryconfig
        
        assert "app.tasks.nlp_tasks.process_nlp_message" in celeryconfig.task_routes
        assert celeryconfig.task_routes["app.tasks.nlp_tasks.process_nlp_message"]["queue"] == "nlp"

    def test_celeryconfig_beat_schedule(self):
        """Test beat schedule in celeryconfig."""
        import celeryconfig
        
        assert "cleanup-old-data" in celeryconfig.beat_schedule
        assert "health-check" in celeryconfig.beat_schedule


class TestCeleryTasks:
    """Test Celery task definitions."""

    def test_nlp_task_queue(self):
        """Test NLP task is assigned to correct queue."""
        from app.celery_app import get_celery_app
        
        celery_app = get_celery_app()
        
        task = celery_app.tasks["app.tasks.nlp_tasks.process_nlp_async"]
        
        assert task.queue == "nlp"

    def test_analysis_task_queue(self):
        """Test analysis task is assigned to correct queue."""
        from app.celery_app import get_celery_app
        
        celery_app = get_celery_app()
        
        task = celery_app.tasks.get("app.tasks.analysis_tasks.analyze_message_async")
        
        if task:
            assert task.queue == "heavy"

    def test_maintenance_task_queue(self):
        """Test maintenance task is assigned to correct queue."""
        from app.celery_app import get_celery_app
        
        celery_app = get_celery_app()
        
        task = celery_app.tasks.get("app.tasks.maintenance_tasks.cleanup_old_data_async")
        
        if task:
            assert task.queue == "maintenance"

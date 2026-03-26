"""Tests unitarios para constants."""

import pytest


def test_ptb_limits_import():
    """Test que las constantes de PTB se pueden importar."""
    from robot_ptb_compat.constants import ptb_limits
    
    assert ptb_limits.BOT_API_VERSION is not None
    assert ptb_limits.MAX_MESSAGE_LENGTH > 0
    assert ptb_limits.MESSAGES_PER_SECOND > 0


def test_app_limits_import():
    """Test que las constantes de la app se pueden importar."""
    from robot_ptb_compat.constants import app_limits
    
    assert app_limits.MAX_TENANT_NAME_LENGTH > 0
    assert app_limits.RATE_LIMIT_SECONDS > 0
    assert app_limits.DEDUP_TTL_SECONDS > 0


def test_version_info():
    """Test de información de versión."""
    from robot_ptb_compat import version
    
    assert version.__version__ == "0.1.0"
    assert version.PTB_VERSION == "22.6.0"
    assert version.PTB_BOT_API_VERSION == "9.3"


def test_error_imports():
    """Test que los errores se pueden importar."""
    from robot_ptb_compat.errors import telegram_errors
    from robot_ptb_compat.errors import app_errors
    
    assert telegram_errors.TelegramError is not None
    assert app_errors.RobotError is not None
    assert app_errors.ConfigurationError is not None


def test_helpers_import():
    """Test que los helpers se pueden importar."""
    from robot_ptb_compat.helpers import ptb_helpers
    from robot_ptb_compat.helpers import app_helpers
    
    assert pth_helpers.escape_markdown is not None
    assert app_helpers.parse_command is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

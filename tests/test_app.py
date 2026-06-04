"""Test Flask application and configuration."""

import pytest

from app.config.settings import settings


def test_settings_load():
    """Test that settings can be loaded from environment."""
    assert settings is not None
    assert settings.app_name == "VibeDrive"
    assert settings.app_version == "0.1.0"


def test_settings_defaults():
    """Test that settings have proper defaults."""
    assert settings.environment in ["development", "test", "uat", "production"]
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expire_minutes == 30


@pytest.mark.skip(reason="Requires full app initialization with dependencies")
def test_app_creation(app):
    """Test that Flask app can be created."""
    assert app is not None
    assert app.config["TESTING"] is True

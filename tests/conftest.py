"""Pytest configuration and fixtures."""

import pytest

from app import create_app


@pytest.fixture
def client():
    """Create Flask test client."""
    app = create_app(env="test")
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def app():
    """Create Flask application for testing."""
    app = create_app(env="test")
    app.config["TESTING"] = True
    return app

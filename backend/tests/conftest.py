"""Pytest configuration and fixtures."""

import pytest
from httpx import AsyncClient

from src.main import create_app


@pytest.fixture
async def async_client():
    """Create test client with mock database."""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_session():
    """Create test database session."""
    # TODO: Set up in-memory SQLite or test PostgreSQL
    raise NotImplementedError()

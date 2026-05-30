import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from auth import create_access_token
from main import app


def make_token(user_id: int = 1, email: str = "alice@example.com") -> str:
    return create_access_token({"sub": str(user_id), "email": email})


@pytest.fixture
def mock_conn():
    return AsyncMock()


@pytest.fixture
def client(mock_conn):
    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("main.init_db_pool", new_callable=AsyncMock), \
         patch("main.close_db_pool", new_callable=AsyncMock):
        with TestClient(app) as c:
            app.state.pool = mock_pool
            yield c


@pytest.fixture
def auth_headers():
    token = make_token(user_id=1, email="alice@example.com")
    return {"Authorization": f"Bearer {token}"}

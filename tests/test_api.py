from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import bcrypt
import pytest

from tests.conftest import make_token

_NOW = datetime.now(timezone.utc)
_PLAIN = "secret"
_HASHED = bcrypt.hashpw(_PLAIN.encode(), bcrypt.gensalt()).decode()

_USER_ROW = {
    "id": 1,
    "email": "alice@example.com",
    "username": "alice",
    "hashed_password": _HASHED,
}

_ORDER_ROW = {
    "id": 10,
    "user_id": 1,
    "status": "delivered",
    "total_amount": Decimal("49.99"),
    "created_at": _NOW,
    "items": [],
    "total_count": 1,
}


# ---------------------------------------------------------------------------
# POST /auth/token
# ---------------------------------------------------------------------------

def test_issue_token_success(client, mock_conn):
    mock_conn.fetchrow.return_value = _USER_ROW
    resp = client.post("/auth/token", json={"username": "alice", "password": _PLAIN})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_issue_token_invalid_credentials(client, mock_conn):
    mock_conn.fetchrow.return_value = None
    resp = client.post("/auth/token", json={"username": "ghost", "password": "bad"})
    assert resp.status_code == 401


def test_issue_token_wrong_password(client, mock_conn):
    mock_conn.fetchrow.return_value = _USER_ROW
    resp = client.post("/auth/token", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /users/{user_id}/orders
# ---------------------------------------------------------------------------

def test_get_orders_no_token(client):
    resp = client.get("/users/1/orders")
    assert resp.status_code == 401


def test_get_orders_success(client, mock_conn, auth_headers):
    mock_conn.fetchrow.return_value = {"id": 1}
    mock_conn.fetch.return_value = [_ORDER_ROW]
    resp = client.get("/users/1/orders", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["orders"]) == 1
    assert body["orders"][0]["id"] == 10


def test_get_orders_user_has_no_orders(client, mock_conn, auth_headers):
    mock_conn.fetchrow.return_value = {"id": 1}
    mock_conn.fetch.return_value = []
    resp = client.get("/users/1/orders", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["orders"] == []


def test_get_orders_forbidden_other_user(client, auth_headers):
    resp = client.get("/users/2/orders", headers=auth_headers)
    assert resp.status_code == 403


def test_get_orders_user_not_found(client, mock_conn, auth_headers):
    mock_conn.fetchrow.return_value = None
    resp = client.get("/users/1/orders", headers=auth_headers)
    assert resp.status_code == 404


def test_get_orders_invalid_user_id_zero(client, auth_headers):
    resp = client.get("/users/0/orders", headers=auth_headers)
    assert resp.status_code == 422


def test_get_orders_invalid_page_zero(client, mock_conn, auth_headers):
    mock_conn.fetchrow.return_value = {"id": 1}
    resp = client.get("/users/1/orders?page=0", headers=auth_headers)
    assert resp.status_code == 422


def test_get_orders_page_two(client, mock_conn, auth_headers):
    mock_conn.fetchrow.return_value = {"id": 1}
    mock_conn.fetch.return_value = []
    resp = client.get("/users/1/orders?page=2", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["page"] == 2

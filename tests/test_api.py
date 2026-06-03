from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import bcrypt


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


# ---------------------------------------------------------------------------
# GitHub OAuth — GET /auth/github
# ---------------------------------------------------------------------------

def test_github_login_redirects_to_github(client):
    resp = client.get("/auth/github", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert "github.com/login/oauth/authorize" in resp.headers["location"]
    assert "state=" in resp.headers["location"]


# ---------------------------------------------------------------------------
# GitHub OAuth — GET /auth/github/callback
# ---------------------------------------------------------------------------

_GH_USER = {"id": 12345, "login": "gh_user", "email": "gh@example.com"}
_DB_USER = {"id": 99, "email": "gh@example.com"}


def test_github_callback_new_user(client, mock_conn):
    # upsert_user_by_github: github_id miss → email miss → INSERT
    mock_conn.fetchrow.side_effect = [None, None, _DB_USER]
    with patch("main.verify_oauth_state", return_value=True), \
         patch("main.exchange_code_for_token", new_callable=AsyncMock, return_value="gh_token"), \
         patch("main.fetch_github_user", new_callable=AsyncMock, return_value=_GH_USER):
        resp = client.get("/auth/github/callback?code=abc&state=valid_state")
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_github_callback_existing_user_by_github_id(client, mock_conn):
    # upsert_user_by_github: github_id hit → return immediately
    mock_conn.fetchrow.return_value = _DB_USER
    with patch("main.verify_oauth_state", return_value=True), \
         patch("main.exchange_code_for_token", new_callable=AsyncMock, return_value="gh_token"), \
         patch("main.fetch_github_user", new_callable=AsyncMock, return_value=_GH_USER):
        resp = client.get("/auth/github/callback?code=abc&state=valid_state")
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_github_callback_links_existing_email_user(client, mock_conn):
    # upsert_user_by_github: github_id miss → email hit (UPDATE links account)
    mock_conn.fetchrow.side_effect = [None, _DB_USER]
    with patch("main.verify_oauth_state", return_value=True), \
         patch("main.exchange_code_for_token", new_callable=AsyncMock, return_value="gh_token"), \
         patch("main.fetch_github_user", new_callable=AsyncMock, return_value=_GH_USER):
        resp = client.get("/auth/github/callback?code=abc&state=valid_state")
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_github_callback_invalid_state(client):
    with patch("main.verify_oauth_state", return_value=False):
        resp = client.get("/auth/github/callback?code=abc&state=bad_state")
    assert resp.status_code == 401


def test_github_callback_github_exchange_fails(client):
    with patch("main.verify_oauth_state", return_value=True), \
         patch("main.exchange_code_for_token", new_callable=AsyncMock, return_value=None):
        resp = client.get("/auth/github/callback?code=bad&state=valid_state")
    assert resp.status_code == 401


def test_github_callback_no_email(client):
    no_email_user = {"id": 12345, "login": "gh_user", "email": None}
    with patch("main.verify_oauth_state", return_value=True), \
         patch("main.exchange_code_for_token", new_callable=AsyncMock, return_value="gh_token"), \
         patch("main.fetch_github_user", new_callable=AsyncMock, return_value=no_email_user):
        resp = client.get("/auth/github/callback?code=abc&state=valid_state")
    assert resp.status_code == 401

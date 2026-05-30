from datetime import timedelta
from unittest.mock import AsyncMock

import bcrypt
import pytest
from fastapi import HTTPException
from jose import jwt

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_ownership,
    verify_password,
)
from config import settings

_PLAIN = "testpass"
_HASHED = bcrypt.hashpw(_PLAIN.encode(), bcrypt.gensalt()).decode()


# ---------------------------------------------------------------------------
# verify_password
# ---------------------------------------------------------------------------

def test_verify_password_correct():
    assert verify_password(_PLAIN, _HASHED) is True


def test_verify_password_wrong():
    assert verify_password("wrong", _HASHED) is False


# ---------------------------------------------------------------------------
# create_access_token
# ---------------------------------------------------------------------------

def test_create_access_token_is_decodable():
    token = create_access_token({"sub": "42", "email": "a@b.com"})
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["email"] == "a@b.com"


def test_create_access_token_custom_expiry():
    token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=5))
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert "exp" in payload


# ---------------------------------------------------------------------------
# verify_ownership
# ---------------------------------------------------------------------------

def test_verify_ownership_same_user_does_not_raise():
    verify_ownership(caller_id=7, requested_user_id=7)


def test_verify_ownership_different_user_raises_403():
    with pytest.raises(HTTPException) as exc_info:
        verify_ownership(caller_id=1, requested_user_id=2)
    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------

async def test_get_current_user_valid_token():
    token = create_access_token({"sub": "3", "email": "user@test.com"})
    user = await get_current_user(token=token)
    assert user.id == 3
    assert user.email == "user@test.com"


async def test_get_current_user_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="not.a.token")
    assert exc_info.value.status_code == 401


async def test_get_current_user_missing_sub_raises_401():
    token = create_access_token({"email": "no-sub@test.com"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token)
    assert exc_info.value.status_code == 401


async def test_get_current_user_missing_email_raises_401():
    token = create_access_token({"sub": "5"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token)
    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# authenticate_user
# ---------------------------------------------------------------------------

async def test_authenticate_user_success():
    conn = AsyncMock()
    conn.fetchrow.return_value = {
        "id": 1,
        "email": "alice@example.com",
        "username": "alice",
        "hashed_password": _HASHED,
    }
    user = await authenticate_user("alice", _PLAIN, conn)
    assert user.id == 1
    assert user.email == "alice@example.com"


async def test_authenticate_user_not_found_raises_401():
    conn = AsyncMock()
    conn.fetchrow.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("ghost", "any", conn)
    assert exc_info.value.status_code == 401


async def test_authenticate_user_wrong_password_raises_401():
    conn = AsyncMock()
    conn.fetchrow.return_value = {
        "id": 1,
        "email": "alice@example.com",
        "username": "alice",
        "hashed_password": _HASHED,
    }
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("alice", "wrongpass", conn)
    assert exc_info.value.status_code == 401

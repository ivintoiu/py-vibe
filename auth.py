# auth.py
# -----------------------------------------------------------------------
# Auth Middleware + Authorization Guard components (DesignSpec)
#
# Auth Middleware  — get_current_user()
#   FastAPI dependency that extracts, decodes, and validates the Bearer
#   JWT on every protected request. Returns an AuthenticatedUser or
#   raises HTTP 401.
#
# Authorization Guard — verify_ownership()
#   Compares the caller's id (from the token) against the user_id in the
#   request path. Raises HTTP 403 if they don't match.
#
# Token Service helpers — authenticate_user() / create_access_token()
#   Credential verification and JWT issuance, used by POST /auth/token.
# -----------------------------------------------------------------------

import hashlib
import hmac
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone

import asyncpg
import bcrypt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import settings
from repository import fetch_user_by_username
from schemas import AuthenticatedUser

logger = logging.getLogger(__name__)

# FastAPI's built-in OAuth2 helper — extracts the Bearer token from the
# Authorization header and passes it to get_current_user as a string.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# ---------------------------------------------------------------------------
# Token Service helpers (DesignSpec: Token Service)
# ---------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Sign and return a JWT containing `data`.
    Expiry defaults to JWT_EXPIRE_MINUTES from settings if not provided.

    DataFlow step 4: Token Service issues a signed JWT containing
    user id and email.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def authenticate_user(
    username: str,
    password: str,
    conn: asyncpg.Connection,
) -> AuthenticatedUser:
    """
    Validate credentials against the database.

    DataFlow steps 2–3:
      - Fetch user row by username; raise 401 if not found.
      - Verify submitted password against bcrypt hash; raise 401 on mismatch.

    Note: We deliberately return the same 401 message whether the username
    or password is wrong, to avoid leaking account existence (EdgeCase).
    GitHub-only accounts (hashed_password IS NULL) always fail here — they
    must authenticate via /auth/github.
    """
    user = await fetch_user_by_username(conn, username)
    if (
        not user
        or not user.get("hashed_password")
        or not verify_password(password, user["hashed_password"])
    ):
        logger.warning("Failed login attempt for username=%r", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthenticatedUser(id=user["id"], email=user["email"])


# ---------------------------------------------------------------------------
# Auth Middleware (DesignSpec: Auth Middleware)
# ---------------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """
    FastAPI dependency injected into every protected route.

    DataFlow step 7:
      Decodes and validates the JWT; raises 401 if the token is
      missing, malformed, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: int | None = payload.get("sub")
        email: str | None = payload.get("email")
        if user_id is None or email is None:
            raise credentials_exception
    except JWTError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise credentials_exception

    return AuthenticatedUser(id=int(user_id), email=email)


# ---------------------------------------------------------------------------
# Authorization Guard (DesignSpec: Authorization Guard)
# ---------------------------------------------------------------------------

def verify_ownership(caller_id: int, requested_user_id: int) -> None:
    """
    Enforce that the authenticated caller can only access their own orders.

    DataFlow step 8:
      Raises HTTP 403 if caller_id != requested_user_id.
    """
    if caller_id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource",
        )


# ---------------------------------------------------------------------------
# GitHub OAuth helpers
# ---------------------------------------------------------------------------

def generate_oauth_state() -> str:
    """Return a stateless CSRF token: `{timestamp}.{nonce}.{hmac_sig}`."""
    ts = str(int(time.time()))
    nonce = secrets.token_hex(16)
    payload = f"{ts}.{nonce}"
    sig = hmac.new(
        settings.JWT_SECRET.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{sig}"


def verify_oauth_state(state: str, max_age: int = 300) -> bool:
    """Return True iff the state is a valid, unexpired token we generated."""
    try:
        parts = state.split(".")
        if len(parts) != 3:
            return False
        ts_str, nonce, sig = parts
        payload = f"{ts_str}.{nonce}"
        expected = hmac.new(
            settings.JWT_SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        return 0 <= int(time.time()) - int(ts_str) <= max_age
    except Exception:
        return False


async def exchange_code_for_token(code: str) -> str | None:
    """Exchange a GitHub OAuth `code` for an access token. Returns None on failure."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
    return resp.json().get("access_token")


async def fetch_github_user(access_token: str) -> dict:
    """
    Fetch authenticated GitHub user profile.
    Falls back to /user/emails when the primary email is set to private.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        user = (
            await client.get("https://api.github.com/user", headers=headers)
        ).json()
        if not user.get("email"):
            emails = (
                await client.get("https://api.github.com/user/emails", headers=headers)
            ).json()
            primary = next(
                (
                    e["email"]
                    for e in emails
                    if e.get("primary") and e.get("verified")
                ),
                None,
            )
            user["email"] = primary
    return user

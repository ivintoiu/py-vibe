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

import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import asyncpg
from fastapi import Depends, HTTPException, Request, status
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
    """
    user = await fetch_user_by_username(conn, username)
    if not user or not verify_password(password, user["hashed_password"]):
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
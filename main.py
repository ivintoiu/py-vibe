# main.py
# -----------------------------------------------------------------------
# API Layer component (DesignSpec: API Layer)
# Exposes two HTTP endpoints:
#
#   POST /auth/token
#     Issues a signed JWT given valid username + password credentials.
#     DataFlow steps 1–4.
#
#   GET /users/{user_id}/orders?page=1
#     Returns a paginated, descending-sorted order history for the
#     authenticated user. Enforces ownership: callers may only fetch
#     their own orders.
#     DataFlow steps 5–13.
#
# Application lifecycle:
#   - startup:  init_db_pool  (DesignSpec: Database Connection Pool)
#   - shutdown: close_db_pool
# -----------------------------------------------------------------------

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from logger import setup_logging
from auth import authenticate_user, create_access_token, get_current_user, verify_ownership
from database import close_db_pool, init_db_pool

setup_logging()
logger = logging.getLogger(__name__)
from schemas import (
    AuthenticatedUser,
    ErrorResponse,
    PaginatedOrderResponse,
    TokenRequest,
    TokenResponse,
)
from services import get_orders_for_user


# ---------------------------------------------------------------------------
# Application lifespan — database pool init / teardown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Runs init_db_pool on startup and close_db_pool on shutdown,
    per the Database Connection Pool component spec.
    """
    await init_db_pool(app)
    logger.info("Application startup complete")
    yield
    await close_db_pool(app)
    logger.info("Application shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Order History API",
    description=(
        "REST API for retrieving a user's order history. "
        "Users can only access their own orders."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    DataFlow step 13:
    Catch any unhandled exception (e.g. unexpected DB errors) and return
    a sanitized 503 — never expose internal details to the client.
    """
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Service temporarily unavailable. Please try again later."},
    )


# ---------------------------------------------------------------------------
# POST /auth/token — Token Service endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/auth/token",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Issue a JWT access token",
    tags=["Auth"],
)
async def issue_token(
    request: Request,
    body: TokenRequest,
) -> TokenResponse:
    """
    Token Service endpoint (DesignSpec: Token Service).

    DataFlow steps 1–4:
      1. Client POSTs credentials to /auth/token.
      2. authenticate_user() fetches the user row and verifies the
         bcrypt password hash.
      3. Returns 401 (with identical message) if username or password
         is wrong — avoids leaking account existence (EdgeCase).
      4. On success, issues a signed JWT containing user id and email.
    """
    async with request.app.state.pool.acquire() as conn:
        user: AuthenticatedUser = await authenticate_user(
            username=body.username,
            password=body.password,
            conn=conn,
        )

    # Embed user id as "sub" (JWT standard claim) and email as a custom claim
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    return TokenResponse(access_token=access_token)


# ---------------------------------------------------------------------------
# GET /users/{user_id}/orders — Order History endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/users/{user_id}/orders",
    response_model=PaginatedOrderResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"description": "Validation error (invalid user_id or page param)"},
        503: {"model": ErrorResponse},
    },
    summary="Get paginated order history for a user",
    tags=["Orders"],
)
async def get_order_history(
    request: Request,
    user_id: int,
    page: int = 1,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PaginatedOrderResponse:
    """
    Paginated order history endpoint (DesignSpec: API Layer).

    DataFlow steps 5–12:
      5.  Client sends GET /users/{user_id}/orders?page=N with Bearer token.
      6.  FastAPI validates user_id > 0 and page >= 1 (422 on failure).
      7.  get_current_user() dependency decodes JWT (401 on failure).
      8.  verify_ownership() checks caller == requested user (403 on mismatch).
      9–12. Order Service retrieves and paginates orders, returns JSON.

    EdgeCases:
      - user_id <= 0           → 422 (FastAPI path validation)
      - page <= 0              → 422 (FastAPI query validation)
      - expired / bad JWT      → 401
      - caller != user_id      → 403
      - user not in DB         → 404
      - user has no orders     → 200 with empty list
      - page beyond last page  → 200 with empty list + correct metadata
    """
    # EdgeCase: user_id must be a positive integer
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be a positive integer",
        )

    # EdgeCase: page must be >= 1
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be >= 1",
        )

    # DataFlow step 8: Authorization Guard — caller may only see their own orders
    verify_ownership(
        caller_id=current_user.id,
        requested_user_id=user_id,
    )

    # DataFlow steps 9–12: delegate to Order Service
    async with request.app.state.pool.acquire() as conn:
        return await get_orders_for_user(conn=conn, user_id=user_id, page=page)
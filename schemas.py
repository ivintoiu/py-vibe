# schemas.py
# -----------------------------------------------------------------------
# Pydantic Schemas component (DesignSpec: Pydantic Schemas)
# Defines and validates all request inputs and response outputs.
# Models used:
#   - TokenRequest / TokenResponse  (auth endpoint)
#   - AuthenticatedUser             (decoded JWT identity)
#   - OrderItem                     (single order row)
#   - PaginatedOrderResponse        (paginated orders envelope)
#   - ErrorResponse                 (error detail wrapper)
# -----------------------------------------------------------------------

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class TokenRequest(BaseModel):
    """Credentials submitted to POST /auth/token."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"


class AuthenticatedUser(BaseModel):
    """
    Decoded identity extracted from a valid JWT.
    Populated by the Auth Middleware and passed into route handlers.
    """
    id: int
    email: str


# ---------------------------------------------------------------------------
# Order schemas
# ---------------------------------------------------------------------------

class OrderItem(BaseModel):
    """
    Represents a single row from the orders table.
    Assumed schema: id, user_id, status, total_amount, created_at, items (jsonb).
    """
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list[Any]  # JSONB column — flexible list of order line items

    model_config = {"from_attributes": True}


class PaginatedOrderResponse(BaseModel):
    """
    Paginated envelope returned by GET /users/{user_id}/orders.
    Includes all metadata a client needs to render pagination controls.
    """
    orders: list[OrderItem]
    page: int
    page_size: int
    total: int        # total matching rows across all pages
    total_pages: int  # ceil(total / page_size)


# ---------------------------------------------------------------------------
# Error schemas
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error body returned on 4xx / 5xx responses."""
    detail: str
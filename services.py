# services.py
# -----------------------------------------------------------------------
# Order Service component (DesignSpec: Order Service)
# Contains business logic for retrieving paginated order history.
# Sits between the API layer and the Repository, keeping route handlers
# thin and logic independently testable.
#
# Public interface:
#   get_orders_for_user(conn, user_id, page, page_size=10)
#       -> PaginatedOrderResponse
# -----------------------------------------------------------------------

import logging
import math

import asyncpg
from fastapi import HTTPException, status

from repository import fetch_orders_by_user_id, fetch_user_by_id
from schemas import OrderItem, PaginatedOrderResponse

logger = logging.getLogger(__name__)

PAGE_SIZE = 10  # Fixed per spec: 10 orders per page


async def get_orders_for_user(
    conn: asyncpg.Connection,
    user_id: int,
    page: int,
) -> PaginatedOrderResponse:
    """
    Retrieve one page of orders for a user, sorted by created_at DESC.

    DataFlow steps 9–11:
      9.  Compute offset = (page - 1) * PAGE_SIZE.
      10. Delegate to Repository with LIMIT / OFFSET.
      11. Map raw dicts to OrderItem models; compute total_pages.

    EdgeCases handled:
      - user_id not in users table           → 404 Not Found
      - user exists but has zero orders      → 200 with empty list
      - page exceeds total_pages             → 200 with empty list + correct metadata
    """
    # EdgeCase: verify the user exists before querying orders.
    # This distinguishes a 404 (unknown user) from an empty order list.
    user = await fetch_user_by_id(conn, user_id)
    if user is None:
        logger.warning("Order history requested for non-existent user_id=%d", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    # DataFlow step 9: calculate SQL OFFSET from the 1-based page number
    offset = (page - 1) * PAGE_SIZE

    # DataFlow step 10: fetch orders + total count from the repository
    result = await fetch_orders_by_user_id(
        conn,
        user_id=user_id,
        limit=PAGE_SIZE,
        offset=offset,
    )

    total: int = result["total"]
    total_pages: int = math.ceil(total / PAGE_SIZE) if total > 0 else 0

    # DataFlow step 11: map raw dicts to validated Pydantic models
    orders = [OrderItem(**row) for row in result["orders"]]

    return PaginatedOrderResponse(
        orders=orders,
        page=page,
        page_size=PAGE_SIZE,
        total=total,
        total_pages=total_pages,
    )
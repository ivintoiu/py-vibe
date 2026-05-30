from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from services import get_orders_for_user

_NOW = datetime.now(timezone.utc)

_ORDER_ROW = {
    "id": 10,
    "user_id": 1,
    "status": "delivered",
    "total_amount": Decimal("49.99"),
    "created_at": _NOW,
    "items": [{"product_id": 7, "name": "Widget", "qty": 1, "unit_price": "49.99"}],
    "total_count": 1,
}


def _make_conn(user_row, order_rows):
    conn = AsyncMock()
    conn.fetchrow.return_value = user_row
    conn.fetch.return_value = order_rows
    return conn


# ---------------------------------------------------------------------------
# user not found
# ---------------------------------------------------------------------------

async def test_user_not_found_raises_404():
    conn = _make_conn(user_row=None, order_rows=[])
    with pytest.raises(HTTPException) as exc_info:
        await get_orders_for_user(conn=conn, user_id=99, page=1)
    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# user with orders
# ---------------------------------------------------------------------------

async def test_user_with_orders_returns_paginated():
    conn = _make_conn(user_row={"id": 1}, order_rows=[_ORDER_ROW])
    result = await get_orders_for_user(conn=conn, user_id=1, page=1)
    assert result.total == 1
    assert result.total_pages == 1
    assert result.page == 1
    assert result.page_size == 10
    assert len(result.orders) == 1
    assert result.orders[0].id == 10


# ---------------------------------------------------------------------------
# user exists but has no orders
# ---------------------------------------------------------------------------

async def test_user_with_no_orders_returns_empty_200():
    conn = _make_conn(user_row={"id": 1}, order_rows=[])
    result = await get_orders_for_user(conn=conn, user_id=1, page=1)
    assert result.orders == []
    assert result.total == 0
    assert result.total_pages == 0


# ---------------------------------------------------------------------------
# page beyond last page
# ---------------------------------------------------------------------------

async def test_page_beyond_last_returns_empty_with_correct_metadata():
    conn = _make_conn(user_row={"id": 1}, order_rows=[])
    result = await get_orders_for_user(conn=conn, user_id=1, page=99)
    assert result.orders == []
    assert result.total == 0
    assert result.page == 99


# ---------------------------------------------------------------------------
# total_pages calculation
# ---------------------------------------------------------------------------

async def test_total_pages_rounds_up():
    rows = [{**_ORDER_ROW, "id": i, "total_count": 11} for i in range(10)]
    conn = _make_conn(user_row={"id": 1}, order_rows=rows)
    result = await get_orders_for_user(conn=conn, user_id=1, page=1)
    assert result.total == 11
    assert result.total_pages == 2

# repository.py
# -----------------------------------------------------------------------
# Database Layer / Repository component (DesignSpec: Database Layer)
# Executes all parameterized SQL queries against PostgreSQL.
# No string interpolation is ever used in SQL — all values are passed
# as asyncpg positional parameters ($1, $2, ...) to prevent SQL injection.
#
# Public interface:
#   fetch_user_by_username(conn, username) -> dict | None
#   fetch_orders_by_user_id(conn, user_id, limit, offset)
#       -> {"orders": list[dict], "total": int}
# -----------------------------------------------------------------------

import asyncpg


async def fetch_user_by_username(
    conn: asyncpg.Connection,
    username: str,
) -> dict | None:
    """
    Look up a user row by username.
    Returns a Record (behaves like a dict) or None if not found.
    Used by the Token Service to validate login credentials.
    """
    row = await conn.fetchrow(
        """
        SELECT id, email, username, hashed_password
        FROM users
        WHERE username = $1
        """,
        username,
    )
    return dict(row) if row else None


async def fetch_user_by_id(
    conn: asyncpg.Connection,
    user_id: int,
) -> dict | None:
    """
    Check whether a user with the given ID exists.
    Used by the Order Service to distinguish 404 (no user) from
    200-with-empty-list (user exists but has no orders).
    """
    row = await conn.fetchrow(
        """
        SELECT id FROM users WHERE id = $1
        """,
        user_id,
    )
    return dict(row) if row else None


async def fetch_orders_by_user_id(
    conn: asyncpg.Connection,
    user_id: int,
    limit: int,
    offset: int,
) -> dict:
    """
    Fetch one page of orders for a user, plus the total matching row count.

    DataFlow step 10:
      - ORDER BY created_at DESC  (most recent orders first, per spec)
      - LIMIT $2 OFFSET $3        (pagination — 10 rows per page)
      - COUNT(*) OVER()           (window function: total without a second query)

    Returns:
        {
            "orders": [list of order dicts],
            "total":  int  (total orders across all pages)
        }
    """
    rows = await conn.fetch(
        """
        SELECT
            id,
            user_id,
            status,
            total_amount,
            created_at,
            items,
            COUNT(*) OVER() AS total_count
        FROM orders
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id,
        limit,
        offset,
    )

    if not rows:
        return {"orders": [], "total": 0}

    # total_count is the same on every row (window function result)
    total = rows[0]["total_count"]

    orders = [
        {
            "id":           row["id"],
            "user_id":      row["user_id"],
            "status":       row["status"],
            "total_amount": row["total_amount"],
            "created_at":   row["created_at"],
            "items":        row["items"] or [],
        }
        for row in rows
    ]

    return {"orders": orders, "total": total}
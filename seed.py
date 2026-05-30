"""
seed.py — populate the database with development fixtures.

Usage:
    python seed.py

Requires a valid DATABASE_URL in .env. Safe to re-run (ON CONFLICT DO NOTHING).

Seeded credentials
------------------
  alice / password123
  bob   / password456
"""

import asyncio
import json

import asyncpg
import bcrypt

from config import settings

# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123"},
    {"username": "bob",   "email": "bob@example.com",   "password": "password456"},
]

ORDERS = [
    # alice (resolved at insert time by username)
    {
        "username": "alice",
        "status": "delivered",
        "total_amount": "49.99",
        "items": [{"product_id": 1, "name": "Widget", "qty": 2, "unit_price": "19.99"},
                  {"product_id": 2, "name": "Gadget", "qty": 1, "unit_price": "10.01"}],
    },
    {
        "username": "alice",
        "status": "shipped",
        "total_amount": "129.00",
        "items": [{"product_id": 3, "name": "Doohickey", "qty": 3, "unit_price": "43.00"}],
    },
    {
        "username": "alice",
        "status": "pending",
        "total_amount": "9.99",
        "items": [{"product_id": 4, "name": "Thingamajig", "qty": 1, "unit_price": "9.99"}],
    },
    # bob
    {
        "username": "bob",
        "status": "delivered",
        "total_amount": "299.95",
        "items": [{"product_id": 5, "name": "Gizmo Pro", "qty": 1, "unit_price": "299.95"}],
    },
    {
        "username": "bob",
        "status": "cancelled",
        "total_amount": "14.50",
        "items": [{"product_id": 6, "name": "Sprocket", "qty": 2, "unit_price": "7.25"}],
    },
]


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def seed() -> None:
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        # -- users ----------------------------------------------------------
        user_ids: dict[str, int] = {}
        for u in USERS:
            row = await conn.fetchrow(
                """
                INSERT INTO users (username, email, hashed_password)
                VALUES ($1, $2, $3)
                ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username
                RETURNING id
                """,
                u["username"],
                u["email"],
                _hash(u["password"]),
            )
            user_ids[u["username"]] = row["id"]
            print(f"  user  : {u['username']} (id={row['id']})")

        # -- orders ---------------------------------------------------------
        for o in ORDERS:
            uid = user_ids[o["username"]]
            await conn.execute(
                """
                INSERT INTO orders (user_id, status, total_amount, items)
                VALUES ($1, $2, $3, $4)
                """,
                uid,
                o["status"],
                o["total_amount"],
                json.dumps(o["items"]),
            )
        print(f"\n  orders: {len(ORDERS)} inserted")

        print("\nSeed complete. Credentials:")
        for u in USERS:
            print(f"  {u['username']:10s} / {u['password']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    if not settings.DATABASE_URL:
        raise SystemExit("DATABASE_URL is not set in .env")
    asyncio.run(seed())

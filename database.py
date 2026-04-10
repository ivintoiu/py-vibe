# database.py
# -----------------------------------------------------------------------
# Database Connection Pool component (DesignSpec: Database Connection Pool)
# Manages a pool of reusable async PostgreSQL connections via asyncpg.
# The pool is attached to app.state so every request handler can acquire
# a connection without creating a new one each time.
#
# Usage:
#   - Call init_db_pool(app) in the FastAPI lifespan startup hook.
#   - Call close_db_pool(app) in the FastAPI lifespan shutdown hook.
#   - Acquire connections via: async with request.app.state.pool.acquire() as conn
# -----------------------------------------------------------------------

import asyncpg
from fastapi import FastAPI

from config import settings


async def init_db_pool(app: FastAPI) -> None:
    """
    Create the asyncpg connection pool and attach it to app.state.pool.
    Called once at application startup.
    """
    app.state.pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,   # keep at least 2 connections warm
        max_size=10,  # cap at 10 concurrent connections
    )


async def close_db_pool(app: FastAPI) -> None:
    """
    Gracefully close all connections in the pool.
    Called once at application shutdown.
    """
    await app.state.pool.close()
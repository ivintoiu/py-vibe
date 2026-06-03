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

import logging

import asyncpg
from fastapi import FastAPI

from config import settings

logger = logging.getLogger(__name__)


async def init_db_pool(app: FastAPI) -> None:
    """
    Create the asyncpg connection pool and attach it to app.state.pool.
    Called once at application startup.
    Raises DatabaseInitError if connection fails.
    """
    try:
        app.state.pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=2,   # keep at least 2 connections warm
            max_size=10,  # cap at 10 concurrent connections
        )
        logger.info("Database connection pool created (min=2, max=10)")
    except (asyncpg.PostgresConnectionError, OSError) as e:
        error_msg = (
            "Cannot connect to PostgreSQL. "
            "Is the database running? Check: docker compose up -d"
        )
        logger.error(error_msg)
        raise DatabaseInitError(error_msg) from e
    except (asyncpg.ClientConfigurationError, ValueError) as e:
        error_msg = f"Invalid DATABASE_URL in .env: {e}"
        logger.error(error_msg)
        raise DatabaseInitError(error_msg) from e
    except Exception as e:
        error_msg = f"Database initialization failed: {e}"
        logger.error(error_msg)
        raise DatabaseInitError(error_msg) from e


class DatabaseInitError(Exception):
    """Raised when database pool initialization fails."""
    pass


async def close_db_pool(app: FastAPI) -> None:
    """
    Gracefully close all connections in the pool.
    Called once at application shutdown.
    """
    if hasattr(app.state, 'pool') and app.state.pool:
        await app.state.pool.close()
        logger.info("Database connection pool closed")

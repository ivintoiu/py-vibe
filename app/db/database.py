"""Database connection pool management using psycopg2."""

from flask import current_app, g
from psycopg2 import pool

from app.config.settings import get_settings


def init_db_pool(app) -> None:
    """Initialize psycopg2 connection pool."""
    settings = get_settings()
    db_pool = pool.ThreadedConnectionPool(
        1,
        settings.database_pool_size,
        settings.database_url.get_secret_value(),
    )
    app.extensions["db_pool"] = db_pool


def close_db_pool(app) -> None:
    """Close database pool."""
    db_pool = app.extensions.pop("db_pool", None)
    if db_pool is not None:
        db_pool.closeall()


def get_db():
    """Get connection from pool for the current request."""
    if "db_conn" not in g:
        db_pool = current_app.extensions["db_pool"]
        g.db_conn = db_pool.getconn()
    return g.db_conn


def teardown_db(exception) -> None:
    """Return connection to pool at request end."""
    conn = g.pop("db_conn", None)
    if conn is not None:
        db_pool = current_app.extensions["db_pool"]
        if exception:
            conn.rollback()
        db_pool.putconn(conn)

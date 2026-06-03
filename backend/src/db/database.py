"""Database connection pool management."""

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.config import settings


async def init_db_engine() -> AsyncEngine:
    """Initialize and return async SQLAlchemy engine."""
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.database_pool_size,
        pool_pre_ping=True,
    )
    return engine


async def close_db_engine(engine: AsyncEngine) -> None:
    """Close database engine."""
    await engine.dispose()


def get_session_factory(engine: AsyncEngine):
    """Create session factory."""
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )

"""Data access layer for users."""

import logging
from typing import Optional

import psycopg2.extras

from app.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data access using psycopg2."""

    def __init__(self, conn):
        self.conn = conn

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
        return User(**row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
        return User(**row) if row else None

    def create(self, username: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                RETURNING id, username, password_hash
                """,
                (username, email, password_hash),
            )
            row = cur.fetchone()
        self.conn.commit()
        return User(**row)

    def user_exists(self, username: str) -> bool:
        """Check if user exists by username."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
        return row is not None

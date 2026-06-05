"""Data access layer for skills."""

import logging
from datetime import datetime
from typing import Optional

import psycopg2.extras

from app.models import Skill, SkillCreate, SkillUpdate

logger = logging.getLogger(__name__)


class SkillRepository:
    """Repository for skill data access using psycopg2."""

    def __init__(self, conn):
        self.conn = conn

    def create(self, user_id: int, skill_create: SkillCreate) -> Skill:
        """Create a new skill."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO skills (user_id, name, description, difficulty_level,
                                    estimated_hours, icon_url, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'planning')
                RETURNING id, user_id, name, description, difficulty_level,
                          estimated_hours, icon_url, status, created_at, updated_at
                """,
                (
                    user_id,
                    skill_create.name,
                    skill_create.description,
                    skill_create.difficulty_level,
                    skill_create.estimated_hours,
                    skill_create.icon_url,
                ),
            )
            row = cur.fetchone()
        self.conn.commit()
        return Skill(**row)

    def get_by_id(self, skill_id: int, user_id: int) -> Optional[Skill]:
        """Get skill by ID (with user ownership check)."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM skills WHERE id = %s AND user_id = %s",
                (skill_id, user_id),
            )
            row = cur.fetchone()
        return Skill(**row) if row else None

    def get_all_for_user(self, user_id: int, skip: int = 0, limit: int = 10) -> list[Skill]:
        """Get all skills for a user with pagination."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM skills WHERE user_id = %s
                ORDER BY created_at DESC LIMIT %s OFFSET %s
                """,
                (user_id, limit, skip),
            )
            rows = cur.fetchall()
        return [Skill(**row) for row in rows]

    def update(self, skill: Skill, skill_update: SkillUpdate) -> Skill:
        """Update a skill."""
        updates = skill_update.model_dump(exclude_unset=True)
        if not updates:
            return skill

        updates["updated_at"] = datetime.utcnow()
        set_clauses = ", ".join(f"{key} = %s" for key in updates)
        values = list(updates.values()) + [skill.id, skill.user_id]

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"""
                UPDATE skills SET {set_clauses}
                WHERE id = %s AND user_id = %s
                RETURNING id, user_id, name, description, difficulty_level,
                          estimated_hours, icon_url, status, created_at, updated_at
                """,
                values,
            )
            row = cur.fetchone()
        self.conn.commit()
        return Skill(**row)

    def delete(self, skill: Skill) -> None:
        """Delete a skill."""
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM skills WHERE id = %s AND user_id = %s",
                (skill.id, skill.user_id),
            )
        self.conn.commit()

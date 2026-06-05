"""Business logic for skill management."""

import logging
from typing import Optional

from app.db.database import get_db
from app.models import SkillCreate, SkillRead, SkillUpdate
from app.repository.skill_repository import SkillRepository

logger = logging.getLogger(__name__)


class SkillService:
    """Skill management service."""

    @staticmethod
    def create_skill(user_id: int, skill_create: SkillCreate) -> SkillRead:
        """Create a new skill for a user."""
        repo = SkillRepository(get_db())
        skill = repo.create(user_id, skill_create)
        logger.info(f"Created skill {skill.id} for user {user_id}")
        return SkillRead.model_validate(vars(skill))

    @staticmethod
    def get_user_skills(user_id: int, skip: int = 0, limit: int = 10) -> list[SkillRead]:
        """Get all skills for a user."""
        repo = SkillRepository(get_db())
        skills = repo.get_all_for_user(user_id, skip, limit)
        return [SkillRead.model_validate(vars(s)) for s in skills]

    @staticmethod
    def get_skill(user_id: int, skill_id: int) -> Optional[SkillRead]:
        """Get a specific skill."""
        repo = SkillRepository(get_db())
        skill = repo.get_by_id(skill_id, user_id)
        if skill is None:
            return None
        return SkillRead.model_validate(vars(skill))

    @staticmethod
    def update_skill(user_id: int, skill_id: int, skill_update: SkillUpdate) -> Optional[SkillRead]:
        """Update a skill."""
        repo = SkillRepository(get_db())
        skill = repo.get_by_id(skill_id, user_id)
        if skill is None:
            return None
        updated = repo.update(skill, skill_update)
        logger.info(f"Updated skill {skill_id} for user {user_id}")
        return SkillRead.model_validate(vars(updated))

    @staticmethod
    def delete_skill(user_id: int, skill_id: int) -> bool:
        """Delete a skill."""
        repo = SkillRepository(get_db())
        skill = repo.get_by_id(skill_id, user_id)
        if skill is None:
            return False
        repo.delete(skill)
        logger.info(f"Deleted skill {skill_id} for user {user_id}")
        return True

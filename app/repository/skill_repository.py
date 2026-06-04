"""Data access layer for skills."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Skill, SkillCreate, SkillUpdate

logger = logging.getLogger(__name__)


class SkillRepository:
    """Repository for skill data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, skill_create: SkillCreate) -> Skill:
        """Create a new skill."""
        skill = Skill(**skill_create.model_dump(), user_id=user_id)
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def get_by_id(self, skill_id: int, user_id: int) -> Optional[Skill]:
        """Get skill by ID (with user ownership check)."""
        stmt = select(Skill).where(Skill.id == skill_id, Skill.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_for_user(self, user_id: int, skip: int = 0, limit: int = 10) -> list[Skill]:
        """Get all skills for a user with pagination."""
        stmt = (
            select(Skill)
            .where(Skill.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Skill.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, skill: Skill, skill_update: SkillUpdate) -> Skill:
        """Update a skill."""
        for key, value in skill_update.model_dump(exclude_unset=True).items():
            setattr(skill, key, value)
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def delete(self, skill: Skill) -> None:
        """Delete a skill."""
        await self.session.delete(skill)
        await self.session.commit()

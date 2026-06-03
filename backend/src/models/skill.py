"""Skill data models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SkillBase(SQLModel):
    """Base skill model with common fields."""

    name: str
    description: Optional[str] = None
    difficulty_level: int = 1  # 1-5
    estimated_hours: int = 0
    icon_url: Optional[str] = None


class Skill(SkillBase, table=True):
    """Skill database model."""

    __tablename__ = "skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "planning"  # planning, learning, completed


class SkillCreate(SkillBase):
    """Schema for creating a skill."""

    pass


class SkillUpdate(SQLModel):
    """Schema for updating a skill."""

    name: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    estimated_hours: Optional[int] = None
    status: Optional[str] = None


class SkillRead(SkillBase):
    """Schema for reading a skill."""

    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

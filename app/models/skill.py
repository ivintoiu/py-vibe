"""Skill data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


@dataclass
class Skill:
    """Skill data holder (read from database)."""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    difficulty_level: int
    estimated_hours: int
    icon_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class SkillCreate(BaseModel):
    """Schema for creating a skill."""

    name: str
    description: Optional[str] = None
    difficulty_level: int = 1
    estimated_hours: int = 0
    icon_url: Optional[str] = None


class SkillUpdate(BaseModel):
    """Schema for updating a skill (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    estimated_hours: Optional[int] = None
    status: Optional[str] = None


class SkillRead(BaseModel):
    """Schema for reading a skill in responses."""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    difficulty_level: int
    estimated_hours: int
    icon_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

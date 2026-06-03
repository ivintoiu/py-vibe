"""Skill management API routes."""

import logging

from fastapi import APIRouter, Depends, status

from src.auth import get_current_user
from src.models import SkillCreate, SkillRead, SkillUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_create: SkillCreate,
    user_id: int = Depends(get_current_user),
):
    """Create a new skill."""
    # TODO: Implement
    raise NotImplementedError()


@router.get("", response_model=list[SkillRead])
async def list_skills(
    skip: int = 0,
    limit: int = 10,
    user_id: int = Depends(get_current_user),
):
    """List user's skills."""
    # TODO: Implement
    raise NotImplementedError()


@router.get("/{skill_id}", response_model=SkillRead)
async def get_skill(
    skill_id: int,
    user_id: int = Depends(get_current_user),
):
    """Get a specific skill."""
    # TODO: Implement
    raise NotImplementedError()


@router.patch("/{skill_id}", response_model=SkillRead)
async def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    user_id: int = Depends(get_current_user),
):
    """Update a skill."""
    # TODO: Implement
    raise NotImplementedError()


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    user_id: int = Depends(get_current_user),
):
    """Delete a skill."""
    # TODO: Implement
    raise NotImplementedError()

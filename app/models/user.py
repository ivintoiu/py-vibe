"""User data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User data holder."""

    id: int
    username: str
    password_hash: str
    email: Optional[str] = None

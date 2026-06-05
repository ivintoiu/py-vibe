"""User data models."""

from dataclasses import dataclass


@dataclass
class User:
    """User data holder."""

    id: int
    username: str
    password_hash: str

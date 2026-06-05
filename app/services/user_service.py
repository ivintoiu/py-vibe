"""Business logic for user management."""

import logging
from typing import Optional

from app.auth.auth import verify_password
from app.db import get_db
from app.models import User
from app.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """User management service."""

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username and password.

        Returns User if credentials valid, None otherwise.
        """
        repo = UserRepository(get_db())
        user = repo.get_by_username(username)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

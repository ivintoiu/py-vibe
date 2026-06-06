#!/usr/bin/env python3
"""
Seed database with test data including hashed passwords.

Run: python scripts/seed.py
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask

from app.auth.auth import hash_password
from app.config.settings import get_settings
from app.db import get_db, init_db_pool


def seed_users(db):
    """Insert test users with real hashed passwords."""

    test_users = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "alicepass123",
        },
        {
            "username": "bob",
            "email": "bob@example.com",
            "password": "bobpass123",
        },
    ]

    cursor = db.cursor()

    for user in test_users:
        hashed_password = hash_password(user["password"])

        try:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """,
                (
                    user["username"],
                    user["email"],
                    hashed_password,
                    datetime.utcnow(),
                    datetime.utcnow(),
                ),
            )
            print(f"✓ Created user: {user['username']}")
        except Exception as e:
            print(f"✗ Failed to create user {user['username']}: {e}")

    db.commit()
    cursor.close()


def seed_skills(db):
    """Insert sample skills for testuser (user_id=1)."""

    sample_skills = [
        {
            "user_id": 1,
            "name": "Python Mastery",
            "description": "Master Python programming from basics to advanced",
            "difficulty_level": 3,
            "estimated_hours": 40,
            "status": "learning",
        },
        {
            "user_id": 1,
            "name": "Flask Framework",
            "description": "Learn Flask web framework",
            "difficulty_level": 2,
            "estimated_hours": 20,
            "status": "planning",
        },
        {
            "user_id": 1,
            "name": "Machine Learning",
            "description": "Introduction to ML with scikit-learn",
            "difficulty_level": 4,
            "estimated_hours": 60,
            "status": "planning",
        },
    ]

    cursor = db.cursor()

    for skill in sample_skills:
        try:
            cursor.execute(
                """
                INSERT INTO skills (user_id, name, description, difficulty_level,
                                   estimated_hours, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    skill["user_id"],
                    skill["name"],
                    skill["description"],
                    skill["difficulty_level"],
                    skill["estimated_hours"],
                    skill["status"],
                    datetime.utcnow(),
                    datetime.utcnow(),
                ),
            )
            print(f"✓ Created skill: {skill['name']}")
        except Exception as e:
            print(f"✗ Failed to create skill {skill['name']}: {e}")

    db.commit()
    cursor.close()


def main():
    """Run all seed operations."""
    settings = get_settings()
    print(f"Seeding database: {settings.database_url.get_secret_value()}")

    # Create Flask app to use get_db()
    app = Flask(__name__)
    init_db_pool(app)

    with app.app_context():
        db = get_db()

        try:
            seed_users(db)
            seed_skills(db)
            print("\n✓ Seeding complete!")
            print("\nTest credentials:")
            print("  testuser / testpass123")
            print("  alice / alicepass123")
            print("  bob / bobpass123")
        except Exception as e:
            print(f"✗ Seeding failed: {e}")
            sys.exit(1)
        finally:
            db.close()


if __name__ == "__main__":
    main()

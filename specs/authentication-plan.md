# Authentication Implementation Plan

## Overview

This document outlines the plan to implement a complete, production-ready authentication system in VibeDrive. Currently, the project has JWT token generation but lacks password verification, user registration, token refresh, and token revocation. This plan addresses all five gaps.

---

## 1. Password Verification in Login Endpoint

### Current State
- `app/routes/api/auth.py:get_token()` accepts username/password but doesn't verify them
- Always returns a token for user ID 1 (hardcoded)
- TODO comment on line 24

### Why This Matters
- **Security**: Without verification, anyone can log in as anyone
- **User isolation**: Different users must access only their own data
- **Compliance**: Required for any production system

### Changes Required

#### 1.1 Update User Repository
**File**: `app/repository/user_repository.py` (new file)

Create a new repository layer for user database operations:
```python
from app.db import get_db
from app.models.user import User

class UserRepository:
    @staticmethod
    def get_by_username(username: str) -> User | None:
        """Fetch user by username from database."""
        # Raw SQL query to find user
        # Return User dataclass or None

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """Fetch user by ID from database."""
        # Used for token validation

    @staticmethod
    def create(username: str, email: str, password_hash: str) -> User:
        """Create a new user (for registration)."""
        # Insert into users table
        # Return created User

    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if username already exists."""
```

**Why**:
- Separates database logic from route logic
- Reusable for login and registration
- Follows repository pattern defined in CLAUDE.md

#### 1.2 Create User Service
**File**: `app/services/user_service.py` (new file)

```python
from app.auth.auth import verify_password
from app.repository.user_repository import UserRepository
from app.models.user import User

class UserService:
    @staticmethod
    def authenticate_user(username: str, password: str) -> User | None:
        """
        Authenticate user by username and password.

        Returns User if credentials valid, None otherwise.
        """
        user = UserRepository.get_by_username(username)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
```

**Why**:
- Business logic layer (distinct from HTTP routes and database)
- Password verification is centralized
- Follows service pattern defined in CLAUDE.md

#### 1.3 Update Auth Route
**File**: `app/routes/api/auth.py`

Replace the `get_token()` function:

```python
from app.services.user_service import UserService
from app.auth.auth import create_access_token

@bp.route("/token", methods=["POST"])
def get_token():
    """POST /api/auth/token - Get JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Authenticate user
    user = UserService.authenticate_user(username, password)
    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    # Create token
    token = create_access_token({"user_id": user.id})
    return jsonify({"access_token": token, "token_type": "bearer"}), 200
```

**Why**:
- Uses real password verification
- Returns 401 for invalid credentials (not 400)
- No hardcoded user ID

### Testing
```bash
# Test valid credentials
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "correctpassword"}'
# Expected: 200 with access_token

# Test invalid credentials
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "wrongpassword"}'
# Expected: 401 with "Invalid username or password"
```

---

## 2. Token Refresh Endpoint

### Current State
- `app/routes/api/auth.py:refresh_token()` returns 501 (not implemented)
- Tokens expire after 30 minutes with no way to refresh

### Why This Matters
- **UX**: Users shouldn't be logged out mid-session
- **Security**: Short-lived access tokens + long-lived refresh tokens is best practice
- **Token rotation**: Allows invalidating old tokens without logging everyone out

### Architecture Pattern

**Dual-token system:**
- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), stored in httpOnly cookie, used only to get new access tokens

### Changes Required

#### 2.1 Update User Model
**File**: `app/models/user.py`

Add refresh token storage capability:
```python
@dataclass
class User:
    id: int
    username: str
    password_hash: str
    refresh_token_hash: str | None = None  # Hash of refresh token
    refresh_token_expires_at: datetime | None = None
```

#### 2.2 Update User Repository
**File**: `app/repository/user_repository.py`

Add methods:
```python
@staticmethod
def update_refresh_token(user_id: int, refresh_token_hash: str, expires_at: datetime) -> None:
    """Store hashed refresh token and expiration."""

@staticmethod
def get_refresh_token(user_id: int) -> tuple[str | None, datetime | None]:
    """Retrieve refresh token hash and expiration for user."""
```

#### 2.3 Update Auth Module
**File**: `app/auth/auth.py`

Add refresh token handling:
```python
def create_tokens(user_id: int) -> tuple[str, str]:
    """
    Create access token and refresh token.

    Returns (access_token, refresh_token) tuple.
    """
    # Access token: 15 minutes
    access_token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=15)
    )

    # Refresh token: 7 days (stored hashed in DB)
    refresh_token = create_access_token(
        {"user_id": user_id, "type": "refresh"},
        expires_delta=timedelta(days=7)
    )

    # Store hashed refresh token in DB
    refresh_token_hash = hash_password(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=7)
    UserRepository.update_refresh_token(user_id, refresh_token_hash, expires_at)

    return access_token, refresh_token

def validate_refresh_token(token: str, user_id: int) -> bool:
    """
    Validate refresh token.

    Checks:
    - Token signature is valid
    - Token hasn't expired
    - Token exists in database and matches hash
    - Token type is "refresh"
    """
    payload = decode_token(token)
    if payload is None:
        return False

    if payload.get("type") != "refresh":
        return False

    if payload.get("user_id") != user_id:
        return False

    # Check DB for hashed token
    stored_hash, expires_at = UserRepository.get_refresh_token(user_id)
    if stored_hash is None or expires_at is None:
        return False

    if datetime.utcnow() > expires_at:
        return False

    return verify_password(token, stored_hash)
```

#### 2.4 Update Login Endpoint
**File**: `app/routes/api/auth.py`

Modify `get_token()` to return both tokens:
```python
@bp.route("/token", methods=["POST"])
def get_token():
    """POST /api/auth/token - Get JWT tokens."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = UserService.authenticate_user(username, password)
    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    # Create both tokens
    access_token, refresh_token = create_tokens(user.id)

    response = jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 minutes in seconds
    })

    # Store refresh token in httpOnly cookie (can't be accessed by JavaScript)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=604800,  # 7 days in seconds
        httponly=True,
        secure=settings.environment == "production",  # HTTPS only in prod
        samesite="Strict"
    )

    return response, 200
```

#### 2.5 Implement Refresh Endpoint
**File**: `app/routes/api/auth.py`

Replace the 501 endpoint:
```python
@bp.route("/refresh", methods=["POST"])
def refresh_token():
    """POST /api/auth/refresh - Refresh JWT token."""
    # Get refresh token from cookie or body
    refresh_token = request.cookies.get("refresh_token") or request.get_json().get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 401

    # Decode to get user_id
    payload = decode_token(refresh_token)
    if payload is None:
        return jsonify({"error": "Invalid refresh token"}), 401

    user_id = payload.get("user_id")

    # Validate refresh token against DB
    if not validate_refresh_token(refresh_token, user_id):
        return jsonify({"error": "Refresh token expired or invalid"}), 401

    # Create new access token (and optionally new refresh token)
    new_access_token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=15)
    )

    return jsonify({
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 900
    }), 200
```

### Database Migration
**File**: `scripts/schema.sql`

Add columns to `users` table:
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token_expires_at TIMESTAMPTZ;
```

### Testing
```bash
# 1. Login (get both tokens)
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "correctpassword"}'
# Returns: access_token, refresh_token, expires_in

# 2. Use access token for API calls
curl http://localhost:5000/api/skills \
  -H "Authorization: Bearer <access_token>"

# 3. When access token expires, use refresh token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
# Returns: new access_token
```

---

## 3. Token Blacklist for Early Revocation (Logout)

### Current State
- No way to invalidate tokens before expiration
- Users can't explicitly log out (token remains valid)

### Why This Matters
- **Security**: Users can't revoke access if device is stolen or compromised
- **Session management**: No explicit logout capability
- **Compliance**: Many regulations require logout functionality

### Architecture

Use Redis to store a blacklist of invalidated tokens:
- When user logs out, add token to Redis set with expiration = token's `exp` claim
- On every request, check if token is in blacklist
- Redis auto-deletes expired entries (no cleanup needed)

### Changes Required

#### 3.1 Create Token Blacklist Service
**File**: `app/services/token_blacklist_service.py` (new file)

```python
from datetime import datetime
from app.db import get_redis
from app.config.settings import settings

class TokenBlacklistService:
    BLACKLIST_PREFIX = "token_blacklist:"

    @staticmethod
    def revoke_token(token: str, exp_timestamp: int) -> None:
        """
        Add token to blacklist.

        Args:
            token: JWT token to revoke
            exp_timestamp: Unix timestamp when token expires
        """
        redis = get_redis()

        # Calculate TTL (time until token naturally expires)
        now = int(datetime.utcnow().timestamp())
        ttl = exp_timestamp - now

        if ttl > 0:
            key = f"{TokenBlacklistService.BLACKLIST_PREFIX}{token}"
            redis.setex(key, ttl, "revoked")

    @staticmethod
    def is_revoked(token: str) -> bool:
        """Check if token is blacklisted."""
        redis = get_redis()
        key = f"{TokenBlacklistService.BLACKLIST_PREFIX}{token}"
        return redis.exists(key) > 0

    @staticmethod
    def clear_all_user_tokens(user_id: int) -> None:
        """
        Revoke all tokens for a user (e.g., password change).

        Note: This requires storing a mapping of user_id -> tokens,
        which is more complex. Alternative: use Redis hash.
        """
        # For now, individual token revocation is sufficient
        pass
```

#### 3.2 Update Token Validation
**File**: `app/auth/auth.py`

Update `decode_token()` to check blacklist:
```python
from app.services.token_blacklist_service import TokenBlacklistService

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        # Check if token is blacklisted (revoked)
        if TokenBlacklistService.is_revoked(token):
            logger.warning(f"Token is blacklisted")
            return None

        return payload
    except JWTError as e:
        logger.error(f"Token decode error: {e}")
        return None
```

#### 3.3 Create Logout Endpoint
**File**: `app/routes/api/auth.py`

Add new route:
```python
from app.services.token_blacklist_service import TokenBlacklistService

@bp.route("/logout", methods=["POST"])
@require_api_auth  # Need token to logout
def logout():
    """POST /api/auth/logout - Revoke current token."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[1] if "Bearer " in auth_header else None

    if not token:
        return jsonify({"error": "Missing token"}), 401

    # Decode to get expiration
    payload = decode_token(token)
    if payload is None:
        return jsonify({"error": "Invalid token"}), 401

    # Revoke token
    exp_timestamp = payload.get("exp")
    TokenBlacklistService.revoke_token(token, exp_timestamp)

    return jsonify({"message": "Logged out successfully"}), 200
```

#### 3.4 Update Redis Connection
**File**: `app/db/__init__.py`

Ensure Redis pool is initialized:
```python
import redis
from app.config.settings import settings

_redis_pool = None

def get_redis():
    """Get Redis connection from pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool
```

### Testing
```bash
# 1. Get token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass"}' | jq -r '.access_token')

# 2. Use token (should work)
curl http://localhost:5000/api/skills \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 with skills list

# 3. Logout (revoke token)
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 "Logged out successfully"

# 4. Try using token again (should fail)
curl http://localhost:5000/api/skills \
  -H "Authorization: Bearer $TOKEN"
# Expected: 401 "Invalid token"
```

---

## 4. Proper Seed Data with Hashed Passwords

### Current State
- `scripts/seed.sql` uses placeholder hash: `$2b$12$placeholder_hash_for_dev`
- Not a real password hash, can't actually log in
- Seed data is static SQL

### Why This Matters
- **Testability**: Developers need real accounts to test with
- **Security**: Even dev data should follow security practices
- **Documentation**: Real hashes show how the system should work

### Changes Required

#### 4.1 Create Python Seed Script
**File**: `scripts/seed.py` (new file)

```python
#!/usr/bin/env python3
"""
Seed database with test data including hashed passwords.

Run: python scripts/seed.py
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.auth import hash_password
from app.db import get_db
from app.config.settings import settings

def seed_users(db):
    """Insert test users with real hashed passwords."""

    test_users = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"  # Password in plaintext for reference
        },
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "alicepass123"
        },
        {
            "username": "bob",
            "email": "bob@example.com",
            "password": "bobpass123"
        }
    ]

    cursor = db.cursor()

    for user in test_users:
        hashed_password = hash_password(user["password"])

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (
                user["username"],
                user["email"],
                hashed_password,
                datetime.utcnow(),
                datetime.utcnow()
            ))
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
            "status": "learning"
        },
        {
            "user_id": 1,
            "name": "Flask Framework",
            "description": "Learn Flask web framework",
            "difficulty_level": 2,
            "estimated_hours": 20,
            "status": "planning"
        },
        {
            "user_id": 1,
            "name": "Machine Learning",
            "description": "Introduction to ML with scikit-learn",
            "difficulty_level": 4,
            "estimated_hours": 60,
            "status": "planning"
        }
    ]

    cursor = db.cursor()

    for skill in sample_skills:
        try:
            cursor.execute("""
                INSERT INTO skills (user_id, name, description, difficulty_level,
                                   estimated_hours, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                skill["user_id"],
                skill["name"],
                skill["description"],
                skill["difficulty_level"],
                skill["estimated_hours"],
                skill["status"],
                datetime.utcnow(),
                datetime.utcnow()
            ))
            print(f"✓ Created skill: {skill['name']}")
        except Exception as e:
            print(f"✗ Failed to create skill {skill['name']}: {e}")

    db.commit()
    cursor.close()

def main():
    """Run all seed operations."""
    print(f"Seeding database: {settings.database_url}")

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
```

**Why this approach:**
- Uses actual password hashing (bcrypt via passlib)
- Passwords stored plaintext in script for dev reference only (never in DB)
- Pythonic: imports app config directly, reuses hashing function
- Creates both users and sample skills
- Better than SQL because it reuses actual app code

#### 4.2 Update schema.sql
**File**: `scripts/schema.sql`

Keep the raw SQL schema as-is (it's still needed for DDL). The seed script will handle data.

#### 4.3 Update Docker Compose
**File**: `docker-compose.yml`

Add seeding step to ensure DB is initialized:
```yaml
services:
  app:
    build: .
    environment:
      DATABASE_URL: postgresql://vibedrive:vibedrive@postgres:5432/vibedrive
    depends_on:
      postgres:
        condition: service_healthy
    command: sh -c "
      python scripts/schema_init.py &&
      python scripts/seed.py &&
      python main.py
    "
```

Or keep it manual with Makefile:
```makefile
.PHONY: seed
seed:
	python scripts/seed.py

.PHONY: db-init
db-init:
	docker compose exec postgres psql -U vibedrive -d vibedrive -f /app/scripts/schema.sql
	python scripts/seed.py
```

#### 4.4 Create .gitignore Entry
**File**: `.gitignore`

Ensure seed script runs are logged but not committed:
```
scripts/seed.log
.env
.env.local
```

### Testing
```bash
# Run seed script
python scripts/seed.py

# Verify users were created
docker compose exec postgres psql -U vibedrive -d vibedrive -c "SELECT username, email FROM users;"

# Test login with seeded credentials
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
# Expected: 200 with access_token

# Verify skills were created
curl http://localhost:5000/api/skills \
  -H "Authorization: Bearer <token_from_above>"
# Expected: 200 with 3 skills
```

---

## 5. User Registration Endpoint

### Current State
- No registration endpoint
- Only admin can create users (manually via SQL)
- Users can't sign up themselves

### Why This Matters
- **User experience**: Self-service signup is essential
- **Onboarding**: Users should be able to create accounts
- **Validation**: Input validation prevents bad data

### Changes Required

#### 5.1 Create Request/Response Models
**File**: `app/models/__init__.py`

Add to imports:
```python
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr  # Validates email format
    password: str = Field(..., min_length=8)  # Min 8 chars

    class Config:
        json_schema_extra = {
            "example": {
                "username": "newuser",
                "email": "user@example.com",
                "password": "securepass123"
            }
        }

class UserRead(BaseModel):
    """User response (public data only)."""
    id: int
    username: str
    email: str
    created_at: datetime
```

#### 5.2 Add Repository Methods
**File**: `app/repository/user_repository.py`

Add registration method:
```python
@staticmethod
def create_user(username: str, email: str, password_hash: str) -> User:
    """
    Create a new user.

    Raises ValueError if username/email already exists.
    """
    db = get_db()
    cursor = db.cursor()

    # Check if username exists
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        raise ValueError(f"Username '{username}' already exists")

    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        raise ValueError(f"Email '{email}' already exists")

    # Insert user
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        RETURNING id, username, email, password_hash
    """, (username, email, password_hash))

    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return User(**row) if row else None
```

#### 5.3 Create Registration Service
**File**: `app/services/user_service.py`

Add method:
```python
from app.models import UserRegister
from app.auth.auth import hash_password

class UserService:
    # ... existing methods ...

    @staticmethod
    def register_user(data: UserRegister) -> User:
        """
        Register a new user.

        Args:
            data: Registration request with username, email, password

        Returns:
            Created User object

        Raises:
            ValueError: If username/email already exists or validation fails
        """
        # Validate username format (alphanumeric + underscore)
        if not re.match(r"^[a-zA-Z0-9_]+$", data.username):
            raise ValueError("Username can only contain letters, numbers, and underscores")

        # Hash password
        password_hash = hash_password(data.password)

        # Create user in database
        try:
            user = UserRepository.create_user(data.username, data.email, password_hash)
            return user
        except ValueError as e:
            raise e
```

#### 5.4 Create Registration Route
**File**: `app/routes/api/auth.py`

Add endpoint:
```python
from pydantic import ValidationError
from app.models import UserRegister, UserRead

@bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register - Register a new user."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        # Validate request
        user_register = UserRegister(**data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422

    try:
        # Create user
        user = UserService.register_user(user_register)

        # Create tokens
        access_token, refresh_token = create_tokens(user.id)

        response = jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900
        })

        # Set refresh token cookie
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=604800,
            httponly=True,
            secure=settings.environment == "production",
            samesite="Strict"
        )

        return response, 201

    except ValueError as e:
        # Username/email already exists
        return jsonify({"error": str(e)}), 409  # 409 Conflict
```

#### 5.5 Add Email Validation (Optional)
**File**: `app/services/user_service.py`

For production, add email verification:
```python
@staticmethod
def send_verification_email(email: str, token: str) -> bool:
    """
    Send email verification link.

    Implementation depends on email service (SendGrid, SES, etc).
    """
    # TODO: Implement email verification
    # For now, skip
    pass
```

### Database Schema
No changes needed; users table already supports registration.

### Testing

**Postman Collection**:

1. **Register new user**
   ```
   POST http://localhost:5000/api/auth/register
   Content-Type: application/json

   {
     "username": "newuser",
     "email": "newuser@example.com",
     "password": "securepass123"
   }
   ```
   Expected: `201 Created` with user data and tokens

2. **Try duplicate username**
   ```
   POST http://localhost:5000/api/auth/register

   {
     "username": "newuser",
     "email": "another@example.com",
     "password": "pass123"
   }
   ```
   Expected: `409 Conflict` with "Username 'newuser' already exists"

3. **Try invalid email**
   ```
   POST http://localhost:5000/api/auth/register

   {
     "username": "another",
     "email": "not-an-email",
     "password": "pass123"
   }
   ```
   Expected: `422 Unprocessable Entity` with validation error

4. **Try weak password**
   ```
   POST http://localhost:5000/api/auth/register

   {
     "username": "another",
     "email": "another@example.com",
     "password": "weak"
   }
   ```
   Expected: `422 Unprocessable Entity` with "at least 8 characters"

---

## Implementation Order

### Phase 1: Core Auth (Tasks 1 & 4)
1. Create `UserRepository` (query DB for users)
2. Create `UserService` (business logic)
3. Update auth routes for password verification
4. Create Python seed script with hashed passwords
5. Test login with real credentials

**Effort**: ~2-3 hours
**Risk**: Low (isolated to auth flow)

### Phase 2: Token Refresh (Task 2)
6. Update `User` model for refresh tokens
7. Add refresh token methods to `UserRepository`
8. Update `app/auth/auth.py` with token creation functions
9. Implement `/api/auth/refresh` endpoint
10. Update login to return both tokens

**Effort**: ~2-3 hours
**Risk**: Medium (new DB columns, cookie handling)

### Phase 3: Token Revocation (Task 3)
11. Create `TokenBlacklistService` (Redis-backed)
12. Update token validation to check blacklist
13. Implement `/api/auth/logout` endpoint
14. Test logout + token invalidation

**Effort**: ~1-2 hours
**Risk**: Low (Redis is simple, doesn't affect existing logic)

### Phase 4: Registration (Task 5)
15. Create `UserRegister` and `UserRead` models
16. Add registration method to `UserService`
17. Implement `/api/auth/register` endpoint
18. Add password validation rules
19. Test registration flow

**Effort**: ~1-2 hours
**Risk**: Low (isolated endpoint, no existing logic affected)

### Total Effort: ~7-10 hours

---

## Testing Strategy

### Unit Tests
- **Password hashing**: `hash_password()` produces consistent bcrypt hashes
- **Token creation**: Tokens contain correct claims and expiration
- **Token validation**: Invalid tokens are rejected (bad signature, expired, blacklisted)

### Integration Tests
- **Login flow**: Valid credentials → tokens; invalid → 401
- **API access**: Valid token → allowed; invalid/missing → 401
- **Logout flow**: Post-logout requests with same token → 401
- **Token refresh**: Valid refresh token → new access token
- **Registration**: Valid data → user created + tokens; duplicates → 409; invalid → 422

### Manual Testing (Postman)
See specific testing sections under each task.

---

## Security Considerations

### Password Security
- ✅ Bcrypt hashing (automatic salt generation)
- ✅ Minimum 8 characters enforced
- ✅ Never log passwords

### Token Security
- ✅ Signed with secret key (HMAC-SHA256)
- ✅ Short expiration (15 minutes for access token)
- ✅ Refresh token in httpOnly cookie (can't be stolen by XSS)
- ✅ Token blacklist for logout

### API Security
- ✅ All protected routes require `Authorization: Bearer <token>`
- ✅ Token validation checks signature + expiration + blacklist
- ✅ Rate limiting (future: implement on auth endpoints)

### Environment Secrets
- ✅ `JWT_SECRET` and `SECRET_KEY` loaded from `.env` (not in code)
- ✅ Different secrets per environment
- ⚠️ TODO: Add secret rotation mechanism

---

## Files Changed Summary

| File | Change | Type |
|------|--------|------|
| `app/repository/user_repository.py` | Create | New |
| `app/services/user_service.py` | Create | New |
| `app/services/token_blacklist_service.py` | Create | New |
| `app/auth/auth.py` | Update | Add functions for refresh tokens, blacklist check |
| `app/routes/api/auth.py` | Update | Implement all endpoints (token, refresh, logout, register) |
| `app/models/user.py` | Update | Add refresh token fields |
| `app/models/__init__.py` | Update | Add UserRegister, UserRead Pydantic models |
| `scripts/seed.py` | Create | New |
| `scripts/schema.sql` | Update | Add refresh token columns to users table |
| `docker-compose.yml` | Update | Add seeding step (optional) |
| `tests/test_auth.py` | Create | New |

---

## Definition of Done

For this plan to be complete:

- [ ] All 5 endpoints implemented: `/token`, `/refresh`, `/logout`, `/register`, `/token` (with password verification)
- [ ] Tests pass: `pytest tests/test_auth.py -v --cov=app/auth --cov=app/routes/api/auth --cov=app/services --cov=app/repository`
- [ ] Linting passes: `ruff check . && black --check . && mypy app/`
- [ ] Manual testing in Postman: all endpoints tested with valid/invalid inputs
- [ ] Seed data works: `python scripts/seed.py` creates users with real passwords
- [ ] Documentation updated: API docs reflect new endpoints
- [ ] CI passes: All GitHub Actions checks pass

---

## Future Enhancements

1. **Email verification**: Send confirmation link on registration
2. **Password reset**: Forgot password flow with email token
3. **Social login**: OAuth2 with Google/GitHub
4. **Multi-factor authentication**: TOTP/SMS second factor
5. **Rate limiting**: Max login attempts, registration spam prevention
6. **Audit logging**: Track auth events (login, logout, password change)
7. **Secret rotation**: Periodic JWT secret rotation with grace period
8. **Refresh token rotation**: Issue new refresh token on each use

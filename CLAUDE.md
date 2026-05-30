# CLAUDE.md — py-vibe context

## What this project is

A FastAPI + asyncpg REST API that lets authenticated users retrieve their own paginated order history from a PostgreSQL database. Personal exercise in Vibe and Agent Coding — no production intent.

## Tech stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| DB driver | asyncpg (async, no ORM) |
| Auth | python-jose (JWT) + bcrypt |
| Config | pydantic-settings (.env) |
| Package manager | **uv** (not pip — no requirements.txt) |
| Linter | ruff |
| Tests | pytest + pytest-asyncio + httpx |
| Local DB | Docker Compose (postgres:16-alpine) |

## Project structure

```
main.py          — API routes + lifespan (pool init/teardown)
auth.py          — JWT issue/decode, bcrypt verify, ownership guard
services.py      — business logic: pagination, 404 guard
repository.py    — all SQL (asyncpg, parameterised, no string interpolation)
database.py      — asyncpg pool init/close, attached to app.state.pool
schemas.py       — Pydantic request/response models
config.py        — Settings singleton (import `settings` everywhere)
logger.py        — structured logging → py-vibe.log
schema.sql       — CREATE TABLE users, orders + index
seed.py          — inserts alice/bob with hashed passwords + 5 orders
docker-compose.yml — postgres:16-alpine on :5432, schema auto-applied on first boot
tests/
  conftest.py    — client fixture (mocked pool), mock_conn, auth_headers
  test_auth.py   — unit tests for auth.py functions
  test_services.py — unit tests for services.py with mocked repository
  test_api.py    — integration tests for all endpoints via TestClient
```

## Important design decisions

### setup_logging() before local imports (main.py)
`setup_logging()` is called at module level *before* the local imports so the logger is configured before any module-level code in auth/database/etc runs. The downstream imports carry `# noqa: E402` — this is intentional, do not "fix" it.

### No ORM
Raw asyncpg SQL only. All queries are in `repository.py` with positional `$1/$2` parameters. Never use string interpolation in SQL.

### Connection pool on app.state
`app.state.pool` is set by `init_db_pool()` at startup. Route handlers acquire connections via `async with request.app.state.pool.acquire() as conn`.

### Tests mock the DB — no real DB needed
The test suite mocks `asyncpg.Connection` via `unittest.mock.AsyncMock`. Tests run without a running PostgreSQL instance. The pool is patched by mocking `main.init_db_pool` and `main.close_db_pool` (not `database.*` — the names are imported into `main`).

## Dev workflow

```bash
# 1. Start the database
docker compose up -d

# 2. Install all deps (including dev)
uv pip install -e ".[dev]"

# 3. Populate fixtures
python seed.py
# → alice / password123,  bob / password456

# 4. Run the server
uvicorn main:app --reload

# 5. Run tests (no DB needed)
python -m pytest tests/ -v

# 6. Lint
python -m ruff check .
```

## Git workflow

- **Never push directly to main** — always open a PR and merge via `gh pr merge`
- Branch naming: `feat/`, `fix/`, `docs/`, `ci/`
- Commit messages follow conventional commits style

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to main:
1. `ruff check .` — lint
2. `pytest tests/ -v` — test (JWT_SECRET injected as env var, no DB)

## Key env vars (.env — not committed)

```
DATABASE_URL = "postgresql://pyvibe:pyvibe@localhost:5432/pyvibe"
JWT_SECRET   = "dev-jwt-secret-change-in-production"
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_MINUTES = 30
```

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/token` | — | Issue JWT given username + password |
| GET | `/users/{user_id}/orders` | Bearer JWT | Paginated order history (10/page) |
| GET | `/docs` | — | OpenAPI UI |

## Status codes

| Code | When |
|---|---|
| 200 | Success |
| 401 | Missing/expired/invalid JWT, or wrong credentials |
| 403 | Token valid but accessing another user's orders |
| 404 | User not found |
| 422 | `user_id ≤ 0` or `page < 1` |
| 503 | Unhandled exception (DB down, etc.) |

# CLAUDE.md — VibeDrive Project Context

## What this project is

VibeDrive is an AI-powered personal learning planner. Users define skills, break them into milestones, track progress, and receive weekly AI-generated study plans with curated resources. Built as a Python monolith using Flask.

**Status:** Scaffold phase — actively building out the architecture iteratively.

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Flask (Python) with Jinja2 templates |
| **Database** | PostgreSQL (psycopg2 DBAPI + ThreadedConnectionPool) |
| **Cache/Jobs** | Redis + Celery |
| **Vector DB** | Qdrant |
| **Auth** | JWT (python-jose) + bcrypt |
| **AI** | LangChain + OpenAI API |
| **Styling** | TailwindCSS |
| **Testing** | pytest + pytest-cov |
| **Linting** | ruff, black, mypy |
| **Deployment** | Docker, Kubernetes, Terraform |

## Project Structure

```
vibedrive/
├── app/                              — Flask application
│   ├── __init__.py                   — App factory
│   ├── config/
│   │   ├── settings.py               — Pydantic BaseSettings
│   │   └── constants.py
│   ├── core/
│   │   ├── exceptions.py
│   │   ├── security.py               — JWT, password hashing
│   │   └── dependencies.py
│   ├── models/                       — Pydantic schemas + dataclasses
│   ├── services/                     — Business logic layer
│   ├── repository/                   — Data access layer (psycopg2 DBAPI)
│   ├── db/                           — Connection pool (ThreadedConnectionPool)
│   ├── routes/
│   │   ├── api/                      — JSON API endpoints
│   │   │   ├── auth.py               — /api/auth/*
│   │   │   └── skills.py             — /api/skills/*
│   │   └── views/                    — HTML template routes
│   │       ├── auth.py               — /login, /register
│   │       └── dashboard.py          — /dashboard, /skills/*
│   ├── templates/                    — Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   └── skills/
│   ├── static/
│   │   ├── css/                      — TailwindCSS + custom styles
│   │   ├── js/
│   │   └── images/
│   └── utils/
│
├── tests/                            — Test suite
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── migrations/                       — Alembic database migrations
├── scripts/                          — Utility scripts (seed, init)
│
├── infrastructure/
│   ├── Dockerfile
│   ├── docker-compose.yml            — Local dev
│   ├── docker-compose.test.yml       — Test environment
│   ├── docker-compose.uat.yml        — UAT environment
│   ├── terraform/                    — IaC for cloud
│   ├── k8s/                          — Kubernetes manifests
│   └── scripts/
│
├── docs/                             — Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   ├── setup.md
│   ├── environments.md
│   ├── routes.md
│   └── architecture-decisions/
│       └── adr-001-flask-consolidation.md
│
├── specs/                            — Product specifications
├── .env.example                      — Environment template
├── .env.test                         — Test environment config
├── main.py                           — Application entry point
├── pyproject.toml
├── Makefile
├── docker-compose.yml                — Root orchestration
└── README.md
```

## Key Design Decisions

### 1. Flask Monolith (not FastAPI + Next.js)
- **Why:** Single Python framework, unified config, simpler deployment
- **How:** Flask serves both HTML templates (Jinja2) and JSON APIs; single Docker image; single deployment pipeline

### 2. Separate API and View Routes
- **Why:** Clean separation of concerns; JSON endpoints distinct from HTML rendering
- **How:** `app/routes/api/` handles `/api/*` JSON endpoints; `app/routes/views/` handles `/` HTML pages

### 3. Raw DBAPI (psycopg2) instead of ORM
- **Why:** Explicit control, no ORM overhead, simpler for synchronous Flask workloads, all SQL visible and auditable
- **How:** `ThreadedConnectionPool` for connection management; raw parameterized SQL in `app/repository/`; RealDictCursor for named column access; explicit connection acquisition via `get_db()`

### 4. Repository + Service Pattern
- **Why:** Layered architecture; easy to test; dependency injection
- **How:** Service layer has business logic; Repository handles database access; routes call services

### 5. JWT Authentication with Flask Sessions
- **Why:** Stateless tokens + persistent cookies for HTML routes
- **How:** `app/auth/auth.py` handles token creation; API routes validate Bearer tokens; HTML routes use Flask sessions

### 6. Multi-Environment Configuration
- **Why:** Seamless dev/test/uat/prod deployments
- **How:** Single `.env` template; environment-specific overrides (`.env.test`, `.env.uat`); docker-compose files per environment

### 7. Jinja2 Templates + TailwindCSS
- **Why:** No Node.js dependency; simpler architecture; built-in to Flask
- **How:** Templates in `app/templates/`; TailwindCSS via CDN; static files serve CSS/JS/images

## Development Workflow

### Local Setup
```bash
# Option 1: Using Docker Compose
docker compose up -d

# App runs at http://localhost:5000
# Postgres at localhost:5432
# Redis at localhost:6379
# Qdrant at localhost:6333

# Option 2: Local development (Python venv)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
python main.py
```

### Running Tests
```bash
pytest tests/ -v
pytest tests/ -v --cov=app
```

### Pre-commit Setup (Recommended)
Pre-commit hooks automatically run linting, formatting, and tests before each commit, preventing bad code from being committed.

**First-time setup:**
```bash
make pre-commit-install
# or manually: pre-commit install
```

**After this, on every `git commit`:**
- ruff validates and fixes import ordering
- black formats code
- mypy type-checks
- pytest runs tests
- trailing-whitespace and debug-statements are caught automatically

**To run pre-commit manually on all files:**
```bash
pre-commit run --all-files
```

**To skip pre-commit (use sparingly):**
```bash
git commit --no-verify
```

### Linting & Formatting (Manual)
If pre-commit is not installed, run these manually:
```bash
ruff check .
black app/ tests/
mypy app/
```

### Database Schema
Schema is defined in raw SQL (no ORM migrations):
```bash
# Apply schema to local database
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/schema.sql

# Apply seed data
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/seed.sql
```

For production deployments, use standard database migration tools (Alembic, Flyway) to manage schema versions.

## Git Workflow

- **Branch naming:** `feat/`, `fix/`, `docs/`, `ci/`, `reorg/` prefixes
- **Commit style:** Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **PR requirement:** All PRs must pass tests and linting before merge
- **Main protection:** Never push directly to main - always PR

## CI/CD (GitHub Actions)

**ci.yml** (on every push/PR):
- Validate pre-commit config: `pre-commit validate-config`
- Run all pre-commit hooks: `pre-commit run --all-files` (ruff, black, mypy, pytest, debug-statements, trailing-whitespace)

**deploy-test.yml** (on develop branch):
- Build Docker image
- Deploy to test environment
- Run integration tests

**deploy-uat.yml** (on release/* branch):
- Build Docker image
- Deploy to UAT with Kustomize
- Smoke tests

**deploy-prod.yml** (on tag v*.*.* ):
- Build Docker image
- Require manual approval
- Deploy to production with Terraform

## Environment Variables

See `.env.example` for all available vars. Key ones:

```
ENVIRONMENT=development|test|uat|production
DEBUG=true|false
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=<flask-secret-key>
JWT_SECRET=<jwt-signing-secret>
REDIS_URL=redis://host:6379/db
QDRANT_URL=http://host:6333
OPENAI_API_KEY=<your-api-key>
```

**Environment-specific files:**
- `.env` — local development (git-ignored)
- `.env.test` — test environment (in git)
- `.env.uat` — UAT template (not in git)
- `.env.prod.example` — production template (not in git)

## Important Notes

### Configuration Loading
Environment-specific `.env` files are loaded automatically. `app/config/settings.py` will load `.env` first, then `.env.{environment}` to override. Set `ENVIRONMENT=test` to load `.env.test`.

### SQL Queries
All SQL uses parameterized queries via psycopg2. Never concatenate user input into SQL strings. Queries are raw SQL in repositories (e.g., `app/repository/skill_repository.py`) for maximum visibility.

### Connection Management
Connections are acquired from `ThreadedConnectionPool` via `get_db()` which is automatically wired to Flask's request context. Import `from app.db import get_db` in services or repositories to get a connection. Connections are automatically returned to the pool at request end via `teardown_db()`.

### Models & Schemas
- **Row objects:** Plain `@dataclass` instances returned from repository queries (e.g., `Skill`)
- **Request/response schemas:** Pydantic `BaseModel` subclasses (e.g., `SkillCreate`, `SkillRead`) for validation and serialization
- **Database mapping:** Explicit in repository—convert dict rows to dataclass via `Skill(**row)` or to Pydantic via `SkillRead.model_validate(vars(skill))`

## Status & Next Steps

**Currently:** Scaffold phase with DBAPI integration
- [x] Directory structure
- [x] Flask monolith scaffold (config, auth, models...)
- [x] Frontend scaffold (Jinja2, landing page, dashboard stub)
- [x] Docker Compose (PostgreSQL, Redis, Qdrant, API, Web services)
- [x] Database layer (psycopg2 DBAPI, connection pool, schema DDL)
- [x] Skill CRUD API endpoints (list, create, read, update, delete)
- [x] Auth API endpoints (password verification, login with tokens) — Phase 1
- [ ] Auth API endpoints (token refresh, logout, registration) — Phase 2-4
- [ ] Skill CRUD view endpoints (HTML forms)
- [ ] Learning path generator (LLM integration)
- [ ] Frontend auth pages
- [ ] Dashboard UI
- [ ] Test suite (unit + integration)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Deployment pipeline (Terraform + ArgoCD)

## Debugging & Common Issues

**Flask app won't start?**
- Check `.env` exists and `DATABASE_URL` is valid
- Verify PostgreSQL is running: `docker compose ps`
- Check Flask env: `ENVIRONMENT=development python main.py`

**Tests failing?**
- Ensure dev dependencies: `pip install -e ".[dev]"`
- Check pytest discovers tests: `pytest tests/ --collect-only`
- Run with verbose output: `pytest tests/ -vv`

**Database connection errors?**
- Verify PostgreSQL container is healthy: `docker compose exec postgres pg_isready`
- Check `DATABASE_URL` matches container network (use `postgres` not `localhost`)

**Templates not rendering?**
- Verify `app/templates/` directory exists
- Check Jinja2 syntax in `.html` files
- Enable Flask debug mode: `DEBUG=true` in `.env`

## Related Reading

- [Architecture Blueprint](specs/architecture_blueprint.md) — Full product spec
- [psycopg2 Documentation](https://www.psycopg.org/docs/) — Database API
- [Flask Documentation](https://flask.palletsprojects.com/en/stable/) — Web framework
- [Pydantic Documentation](https://docs.pydantic.dev/) — Request/response validation

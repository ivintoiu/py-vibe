# VibeDrive - AI-Powered Personal Learning Planner

**Flask monolith** for defining skills, tracking milestones, and receiving AI-generated study plans.

> **Note:** VibeDrive is built as a **Flask monolith** (single Python app with Jinja2 templates), not the FastAPI/Next.js stack mentioned in early specs. This decision prioritizes simplicity, faster development, and unified deployment. See [CLAUDE.md](CLAUDE.md) for architectural decisions.

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose
```bash
docker compose up -d
```
App runs at http://localhost:5000

### Option 2: Local Development
```bash
uv sync --extra dev --no-install-project
cp .env.example .env
python main.py
```

Visit http://localhost:5000

## Project Structure

```
vibedrive/
├── app/              # Flask application
├── tests/            # Test suite
├── migrations/       # Database migrations
├── infrastructure/   # Docker, Terraform, K8s
├── docs/             # Documentation
├── main.py           # Entry point
├── pyproject.toml    # Dependencies
└── Makefile          # Convenience commands
```

## Tech Stack

- **Framework:** Flask + Jinja2
- **Database:** PostgreSQL + psycopg2 (raw DBAPI)
- **Connection Pool:** ThreadedConnectionPool
- **Cache:** Redis
- **Vector DB:** Qdrant
- **Auth:** JWT (python-jose)
- **Styling:** TailwindCSS
- **Testing:** pytest

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Lint & Format
```bash
ruff check .
black app/ tests/
mypy app/
```

### Database
```bash
# Apply schema (using raw SQL, no ORM migrations)
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/schema.sql

# Apply seed data
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/seed.sql
```

## Multi-Environment Deployment

- **Local:** `docker-compose.yml` (development mode)
- **Test:** `docker-compose.test.yml`
- **UAT:** `docker-compose.uat.yml` + Kustomize
- **Prod:** Terraform + Kubernetes

See [docs/environments.md](docs/environments.md) for details.

## Architecture

See [docs/architecture.md](docs/architecture.md) for system design.

## API Routes

- `POST /api/auth/token` — Get JWT token (username/password auth)
- `POST /api/auth/refresh` — Refresh JWT token (not implemented)
- `POST /api/auth/logout` — Revoke JWT token (not implemented)
- `POST /api/auth/register` — Register new user (not implemented)
- `GET /api/skills` — List skills (JSON)
- `POST /api/skills` — Create skill (JSON)
- `GET /api/skills/{id}` — Get skill (JSON)
- `PATCH /api/skills/{id}` — Update skill (JSON)
- `DELETE /api/skills/{id}` — Delete skill (JSON)

## HTML Routes

- `GET /` — Home page
- `GET /login` — Login page
- `POST /login` — Handle login
- `GET /register` — Registration page
- `POST /register` — Handle registration
- `GET /dashboard` — Skills dashboard
- `GET /skills/create` — Create skill form
- `GET /skills/{id}` — Skill detail page

See [docs/routes.md](docs/routes.md) for full reference.

## Contributing

1. Create branch: `git checkout -b feat/feature-name`
2. Make changes
3. Test: `pytest tests/ -v`
4. Lint: `ruff check . && black app/`
5. Commit: `git commit -m "feat: description"`
6. Push & open PR

## License

MIT

## Status

🏗️ **Scaffold phase** — Early development

**Completed:**
- ✅ Directory structure & Flask monolith
- ✅ Database layer (psycopg2 DBAPI, connection pool, schema)
- ✅ API routes (skills CRUD with full implementation)
- ✅ Frontend scaffold (Jinja2, TailwindCSS, landing page)
- ✅ Docker Compose (dev, test, UAT environments)
- ✅ Pre-commit hooks & CI/CD

**In Progress:**
- 🚧 Token refresh & logout endpoints
- 🚧 User registration endpoint
- 🚧 Frontend auth & dashboard pages
- 🚧 Learning path generator (LLM)

**Not Started:**
- ⏳ Milestones & subskill hierarchy
- ⏳ Weekly AI study plans
- ⏳ Resource embeddings & discovery
- ⏳ Notifications & streaks
- ⏳ Progress analytics

See [CLAUDE.md](CLAUDE.md) for project context and [docs/](docs/) for detailed guides.

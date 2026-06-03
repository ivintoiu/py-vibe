# CLAUDE.md — VibeDrive Project Context

## What this project is

VibeDrive is a full-stack AI-powered personal learning planner. Users define skills, break them into milestones, track progress, and receive weekly AI-generated study plans with curated resources.

**Status:** Scaffold phase — actively building out the architecture iteratively.

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI (Python), Next.js (React/TS) |
| **Database** | PostgreSQL + asyncpg (async) |
| **Cache/Jobs** | Redis + Celery |
| **Vector DB** | Qdrant |
| **Auth** | python-jose + JWT |
| **AI** | LangChain + OpenAI API |
| **Testing** | pytest + pytest-asyncio |
| **Linting** | ruff, black, mypy |
| **Deployment** | Docker, Kubernetes (optional), Terraform |

## Project Structure

```
vibedrive/
├── backend/
│   ├── src/
│   │   ├── api/           — API route handlers
│   │   ├── auth/          — JWT, OAuth2, password hashing
│   │   ├── models/        — SQLModel ORM definitions
│   │   ├── services/      — business logic layer
│   │   ├── repository/    — data access layer
│   │   ├── db/            — database initialization
│   │   ├── config.py      — Settings & env vars
│   │   └── main.py        — FastAPI app entry point
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/         — Next.js pages & routes
│   │   ├── components/    — React components
│   │   ├── hooks/         — Custom React hooks
│   │   ├── utils/         — Helper functions
│   │   └── styles/        — Global styles
│   ├── public/            — Static assets
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── infrastructure/
│   ├── docker-compose.yml — local dev stack
│   ├── terraform/         — IaC for cloud deployment
│   ├── k8s/              — Kubernetes manifests
│   └── scripts/          — utility scripts
│
├── docs/                  — API, architecture, deployment guides
├── specs/                 — Product specifications
├── .env.example
├── README.md
└── CLAUDE.md (this file)
```

## Key Design Decisions

### 1. Monorepo with Module Separation
- **Why:** Easier to manage frontend+backend together, shared types/constants in future
- **How:** Root `docker-compose.yml` orchestrates all services; each module has its own Dockerfile

### 2. FastAPI + SQLModel (not Django ORM)
- **Why:** Modern async-first framework, lightweight, educational
- **How:** Raw SQLAlchemy async queries; structured logging; clean separation of layers

### 3. SQLModel (not raw asyncpg)
- **Why:** Type safety, auto-generated schemas, lighter than full ORM
- **How:** Models defined once, used for DB schema + API validation

### 4. Repository + Service Pattern
- **Why:** Clean layering; easy to test services with mocked repos
- **How:** Service layer has business logic; Repository handles SQL; API routes call services

### 5. JWT Authentication (OAuth2 flow)
- **Why:** Stateless, scalable, integrates with Google/GitHub logins later
- **How:** `src/auth/auth.py` handles token creation/validation; routes use `Depends(get_current_user)`

### 6. Tests Mock the Database
- **Why:** Tests run fast without PostgreSQL; simpler CI
- **How:** Use `unittest.mock` to patch SQLAlchemy sessions in tests

### 7. Environment Variables via Pydantic Settings
- **Why:** 12-factor app compliance; type-safe config
- **How:** `src/config.py` reads `.env` on startup; import `settings` everywhere

## Development Workflow

### Local Setup
```bash
# Start all services
docker compose -f infrastructure/docker-compose.yml up -d

# Backend (if developing locally)
cd backend
uv pip install -e ".[dev]"
uvicorn src.main:app --reload

# Frontend (if developing locally)
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
cd backend
pytest tests/ -v
```

### Linting & Formatting
```bash
cd backend
ruff check . && black src/
```

## Git Workflow

- **Branch naming:** `feat/`, `fix/`, `docs/`, `ci/`, `reorg/` prefixes
- **Commit style:** Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **PR requirement:** All PRs must pass tests and linting before merge
- **Main protection:** Never push directly to main — always PR

## CI/CD (GitHub Actions)

Runs on every push/PR to main:
1. `ruff check .` — lint
2. `pytest tests/ -v` — unit + integration tests
3. `next build` — frontend build verification

## Environment Variables

See `.env.example` for all available vars. Key ones:

```
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=dev-secret-change-in-production
REDIS_URL=redis://...
QDRANT_URL=http://...
OPENAI_API_KEY=...
DEBUG=true|false
```

## Important Notes

### Setup Logging Early
In `src/main.py`, logging is configured *before* local imports so all downstream modules have the logger set up. This is intentional.

### No String Interpolation in SQL
All SQL uses parameterized queries with SQLAlchemy ORM safety. Never concatenate user input into SQL.

### Async-First
Backend is fully async. Use `await` with all database, Redis, and HTTP calls.

### Frontend Type Safety
TypeScript strict mode enforced. No `any` types without // @ts-ignore (document the reason).

## Status & Next Steps

**Currently:** Scaffold phase
- [x] Directory structure
- [x] Backend skeleton (FastAPI, config, auth, models, services, repository)
- [x] Frontend scaffold (Next.js, landing page, dashboard stub)
- [x] Docker Compose (PostgreSQL, Redis, Qdrant, API, Web services)
- [ ] Database migrations
- [ ] Auth API endpoints (login, register, token refresh)
- [ ] Skill CRUD endpoints
- [ ] Learning path generator (LLM integration)
- [ ] Frontend auth pages
- [ ] Dashboard UI
- [ ] Test suite
- [ ] API documentation
- [ ] Deployment pipeline (Terraform + ArgoCD)

## Debugging & Common Issues

**API won't start?**
- Check `.env` is set and `DATABASE_URL` is valid
- Verify PostgreSQL is running: `docker compose -f infrastructure/docker-compose.yml ps`

**Tests failing?**
- Make sure you've installed dev dependencies: `uv pip install -e ".[dev]"`
- Check pytest is discovering tests: `pytest tests/ --collect-only`

**Frontend not connecting to API?**
- Check `NEXT_PUBLIC_API_URL` in `.env`
- Verify API is running on port 8000

## Related Reading

- [Architecture Blueprint](specs/architecture_blueprint.md) — Full product spec
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Guide](https://sqlmodel.tiangolo.com/)
- [Next.js Learn](https://nextjs.org/learn)

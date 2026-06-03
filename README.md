# VibeDrive

> AI-powered personal learning planner

VibeDrive helps you define skills, track progress, and receive weekly AI-generated study plans with curated resources.

## 🏗️ Architecture

This is a **monorepo** with module-based separation:

```
vibedrive/
├── backend/          # FastAPI REST API (Python)
├── frontend/         # Next.js web app (React/TypeScript)
├── infrastructure/   # Docker Compose, Terraform, K8s configs
├── docs/            # API documentation, architecture notes
└── specs/           # Project specifications and blueprints
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, SQLModel, asyncpg |
| **Frontend** | Next.js, React, TypeScript, TailwindCSS |
| **Database** | PostgreSQL |
| **Cache & Jobs** | Redis, Celery |
| **Vector Search** | Qdrant |
| **Auth** | JWT + OAuth2 |
| **AI** | LangChain, OpenAI API |
| **Observability** | Prometheus, OpenTelemetry |
| **Deployment** | Docker, Kubernetes, Terraform |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node 18+ (for local frontend development)

### Development

1. **Clone and setup**
```bash
git clone <repo>
cd vibedrive
cp .env.example .env
```

2. **Start all services**
```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

3. **Access the app**
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Redis: localhost:6379
- PostgreSQL: localhost:5432

### Local Backend Development

```bash
cd backend

# Install dependencies
uv pip install -e ".[dev]"

# Run migrations (TODO)
# python -m alembic upgrade head

# Start API with hot reload
uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Lint and format
ruff check .
black src/
```

### Local Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Type check
npm run type-check

# Format code
npm run format
```

## 📚 Features (Roadmap)

- [x] Project scaffold
- [ ] User authentication (OAuth2 + JWT)
- [ ] Skill definition & hierarchy
- [ ] Progress tracking dashboard
- [ ] Learning path generator (LLM)
- [ ] Weekly AI study plans
- [ ] Resource embedding & discovery
- [ ] Notifications (email, push)
- [ ] Gamification (XP, badges, streaks)
- [ ] API documentation
- [ ] Kubernetes deployment
- [ ] Monitoring & observability
- [ ] Mobile-friendly UI

## 📖 Documentation

- [API Endpoints](docs/api.md) — REST & GraphQL specifications
- [Architecture](docs/architecture.md) — System design and patterns
- [Deployment](docs/deployment.md) — Cloud and local deployment guides
- [Blueprint](specs/architecture_blueprint.md) — Full product specification

## 🔐 Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing (bcrypt)
- Rate limiting on API endpoints
- CORS configuration per environment
- Vault for secrets management (production)

## 📊 Observability

- Prometheus metrics
- OpenTelemetry traces
- Structured logging
- Grafana dashboards (future)

## 🤝 Contributing

1. Branch naming: `feat/`, `fix/`, `docs/`, `ci/`
2. All PRs require code review
3. Tests must pass before merge
4. Conventional commits style

## 📝 License

Private project (TBD)

## 🙋 Support

See [CLAUDE.md](CLAUDE.md) for project context and developer instructions.

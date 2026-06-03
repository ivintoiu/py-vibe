# Architecture

## System Design

VibeDrive follows a clean hexagonal (ports & adapters) architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│               Presentation Layer                         │
│  (Next.js Frontend, API Routes, WebSocket Handlers)     │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│               API Layer                                  │
│  (FastAPI Routes, Request/Response Validation)          │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│               Service Layer                             │
│  (Business Logic, LLM Integration, Orchestration)       │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│               Repository Layer                          │
│  (Data Access, SQL, Cache, Vector Search)               │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│               Infrastructure Layer                      │
│  (PostgreSQL, Redis, Qdrant, OpenAI API)                │
└─────────────────────────────────────────────────────────┘
```

## Backend Stack

### FastAPI Application
- **Location:** `backend/src/main.py`
- **Entry Point:** `app = create_app()`
- **Lifespan:** Manages database and Redis connection pools on startup/shutdown
- **Middleware:** CORS, request logging, error handling

### Database Layer

**PostgreSQL + SQLAlchemy**
- Async connections via asyncpg
- Connection pooling managed by SQLAlchemy
- Models defined once in SQLModel (database schema + API validation)

**Repository Pattern**
- `backend/src/repository/` — Data access objects
- Each entity (Skill, User, etc.) has a repository
- Encapsulates all SQL queries
- Easily testable with mocks

### Service Layer

**Business Logic**
- `backend/src/services/` — Service classes
- Orchestrate repositories and external APIs (LLM, embedding search)
- No direct database access
- Testable in isolation

### API Routes

**FastAPI Routers**
- `backend/src/api/` — Route handlers
- Models use Pydantic for validation
- Dependency injection via FastAPI's `Depends()`
- Auth guard: `get_current_user` dependency

### Authentication

**JWT-Based**
- `backend/src/auth/auth.py` — Token creation/validation
- Password hashing with bcrypt
- OAuth2 scheme with HTTPBearer
- Token refresh (future)

## Frontend Stack

### Next.js Application
- **Location:** `frontend/src/`
- **Type Safety:** TypeScript strict mode
- **Styling:** TailwindCSS
- **State Management:** Zustand (minimal store)
- **HTTP Client:** Axios with interceptors for JWT

### Page Structure
- `pages/` — Next.js pages (file-based routing)
- `components/` — Reusable React components
- `hooks/` — Custom React hooks
- `utils/` — Helper functions and API client
- `styles/` — Global styles and Tailwind config

## Data Flow

### Creating a Skill (Happy Path)

```
User (Frontend)
    ↓
[POST /api/skills]
    ↓
FastAPI Route (api/skills.py)
    ├─ Validates input (Pydantic)
    ├─ Calls get_current_user (auth guard)
    ↓
Service Layer (SkillService.create_skill)
    ├─ Business logic (if any)
    ├─ Calls repository
    ↓
Repository Layer (SkillRepository.create)
    ├─ Inserts into PostgreSQL
    ├─ Returns created model
    ↓
Service returns created skill
    ↓
Route returns 201 + JSON
    ↓
Frontend updates state (Zustand)
    ↓
UI re-renders
```

### Learning Path Generation (LLM Integration)

```
User clicks "Generate Learning Path"
    ↓
Frontend calls [POST /api/skills/{id}/learning-path]
    ↓
FastAPI route calls LearningPathService
    ↓
Service calls LangChain agent
    ├─ Input: skill definition
    ├─ LLM (OpenAI): generates structured JSON
    ├─ Returns: milestones, estimated hours, resources
    ↓
Service calls EmbeddingSearch
    ├─ Embeds milestone descriptions
    ├─ Searches Qdrant for matching resources
    ├─ Returns curated learning materials
    ↓
Service stores learning path + resources in DB
    ↓
Frontend displays generated path
```

### Weekly Study Plan Generation (Scheduled Job)

```
Celery Beat triggers at Sunday 09:00 UTC
    ↓
Celery Worker runs generate_weekly_plan task
    ↓
Task queries user skills + progress
    ↓
LLM Agent generates weekly study plan
    ├─ Input: skills, milestones, past progress
    ├─ Output: prioritized tasks for the week
    ↓
Stores plan in DB
    ↓
Sends notifications (email, push)
```

## Caching Strategy

**Redis Cache Layers**
1. **Session Cache** — Store JWT tokens temporarily
2. **Query Cache** — Cache user skills, learning paths (TTL: 1 hour)
3. **Embedding Cache** — Store resource embeddings (TTL: 1 week)
4. **Job Queue** — Celery tasks for async work

## Security Model

1. **Authentication** — JWT tokens (30-min expiry)
2. **Authorization** — Role-based (user, admin)
3. **Ownership Guard** — Users can only access their own data
4. **Secrets** — Environment variables + Vault in production
5. **Rate Limiting** — Per-user API limits
6. **SQL Injection** — Parameterized queries (SQLAlchemy)

## Observability

### Logging
- Structured logs to `py-vibe.log`
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging middleware

### Metrics
- Prometheus metrics exported at `/metrics`
- API latency, error rates, database connection pool

### Tracing
- OpenTelemetry traces
- Distributed tracing support (Jaeger, etc.)

## Deployment

### Docker Composition
- `api` service — FastAPI on port 8000
- `web` service — Next.js on port 3000
- `postgres` service — Database on port 5432
- `redis` service — Cache on port 6379
- `qdrant` service — Vector DB on port 6333

### Kubernetes (Future)
- Helm charts for configuration
- HPA (Horizontal Pod Autoscaling) for API
- StatefulSet for PostgreSQL
- ConfigMaps for non-secrets

### Infrastructure as Code
- Terraform modules for AWS (RDS, ElastiCache, S3)
- Network policies, RBAC, secrets management
- ArgoCD for GitOps deployment

## Future Enhancements

1. **GraphQL Layer** — Query flexibility for frontend
2. **Real-time Updates** — WebSocket for live progress
3. **Mobile App** — React Native or Flutter
4. **Browser Extension** — Save-to-VibeDrive feature
5. **Community Features** — Share learning paths, mentor matching
6. **Analytics Dashboard** — Learning trends, insights
7. **Marketplace** — Publish/sell skill packs

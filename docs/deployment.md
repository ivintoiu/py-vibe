# Deployment Guide

## Local Development

### Prerequisites
- Docker & Docker Compose 2.0+
- Python 3.12+
- uv

### Option 1: Docker Compose (recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd py-vibe

# 2. Copy environment
cp .env.example .env

# 3. Start all services
docker compose up -d

# App:      http://localhost:5000
# Postgres: localhost:5432
# Redis:    localhost:6379
# Qdrant:   localhost:6333

# Check service health
docker compose ps
```

### Option 2: Local Python (no Docker)

```bash
# Install dependencies
uv sync --extra dev --no-install-project

# Copy and edit environment
cp .env.example .env

# Start Flask dev server
python main.py
```

Requires a running PostgreSQL, Redis, and Qdrant (use `docker compose up postgres redis qdrant -d`).

## Database

```bash
# Apply schema
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/schema.sql

# Seed test data
psql postgresql://vibedrive:vibedrive@localhost:5432/vibedrive -f scripts/seed.sql

# Or via Makefile
make seed
```

## Testing

```bash
# Run all tests (local)
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run tests in Docker
make docker-test
# equivalent: docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## Code Quality

```bash
# Lint + format (auto-fix)
make format

# Lint check only
ruff check .

# Format check only
black --check app/ tests/

# Type check
mypy app/

# All checks (no auto-fix)
make lint
```

## Docker Build

### Build image locally

```bash
docker build -f infrastructure/Dockerfile -t vibedrive:latest .
```

### Push to registry

```bash
docker tag vibedrive:latest myregistry.azurecr.io/vibedrive:latest
docker push myregistry.azurecr.io/vibedrive:latest
```

## Environments

Three compose files cover the full deployment lifecycle:

| File | Environment | Usage |
|---|---|---|
| `docker-compose.yml` | Development | `docker compose up` |
| `docker-compose.test.yml` | Test | `make docker-test` / CI |
| `docker-compose.uat.yml` | UAT | Requires `.env.uat` with `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `DB_PASSWORD` |

### UAT deployment

```bash
# Set environment variables (or populate .env.uat)
export DATABASE_URL=postgresql://vibedrive:<pass>@<host>:5432/vibedrive
export REDIS_URL=redis://<host>:6379/0
export QDRANT_URL=http://<host>:6333
export DB_PASSWORD=<pass>

docker compose -f docker-compose.uat.yml up -d --build
```

## CI/CD (GitHub Actions)

Workflows in `.github/workflows/`:

| Workflow | Trigger | Actions |
|---|---|---|
| `ci.yml` | Every push / PR | pre-commit hooks (ruff, black, mypy, pytest) |
| `deploy-test.yml` | `develop` branch | Docker build → test environment |
| `deploy-uat.yml` | `release/*` branch | Docker build → UAT (Kustomize) |
| `deploy-prod.yml` | Tag `v*.*.*` | Docker build → production (Terraform, manual approval) |

## Cloud Deployment (Planned)

### Kubernetes

```bash
# Apply manifests
kubectl apply -f infrastructure/k8s/

# Check rollout
kubectl rollout status deployment/vibedrive -n production

# View logs
kubectl logs -f deployment/vibedrive -n production

# Rollback
kubectl rollout undo deployment/vibedrive -n production
```

### Terraform

```bash
cd infrastructure/terraform

terraform init
terraform plan -var-file=production.tfvars
terraform apply -var-file=production.tfvars
```

## Monitoring

```bash
# Prometheus metrics
curl http://localhost:5000/metrics

# Container logs
docker logs -f vibedrive-app

# Kubernetes logs
kubectl logs -f deployment/vibedrive -n production
```

## Troubleshooting

### Services won't start

```bash
docker compose logs app
docker compose ps
docker compose up -d --build
```

### Database connection errors

```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U vibedrive

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Database backup / restore

```bash
# Backup
docker exec vibedrive-postgres pg_dump -U vibedrive vibedrive > backup.sql

# Restore
docker exec -i vibedrive-postgres psql -U vibedrive vibedrive < backup.sql
```

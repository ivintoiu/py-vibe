# Deployment Guide

## Local Development

### Prerequisites
- Docker & Docker Compose 2.0+
- Python 3.11+
- Node 18+
- Git

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd vibedrive

# 2. Copy environment
cp .env.example .env

# 3. Start all services
docker compose -f infrastructure/docker-compose.yml up -d

# 4. Wait for services (check health)
docker compose -f infrastructure/docker-compose.yml ps

# 5. Access the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Local Backend Development

```bash
cd backend

# Install dependencies
uv pip install -e ".[dev]"

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://vibedrive:vibedrive@localhost:5432/vibedrive"
export JWT_SECRET="dev-secret"

# Run migrations (when added)
# python -m alembic upgrade head

# Start with hot reload
uvicorn src.main:app --reload --port 8000
```

## Local Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check
```

## Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run in watch mode
pytest tests/ -v --looponfail
```

## Code Quality

```bash
cd backend

# Lint
ruff check .

# Format
black src/ tests/

# Type check
mypy src/

# All checks
ruff check . && black --check src/ && mypy src/
```

## Docker Build

### Build Images Locally

```bash
# Backend
docker build -f backend/Dockerfile -t vibedrive-api:latest .

# Frontend
docker build -f frontend/Dockerfile -t vibedrive-web:latest .
```

### Push to Registry

```bash
# Tag for registry
docker tag vibedrive-api:latest myregistry.azurecr.io/vibedrive-api:latest
docker tag vibedrive-web:latest myregistry.azurecr.io/vibedrive-web:latest

# Push
docker push myregistry.azurecr.io/vibedrive-api:latest
docker push myregistry.azurecr.io/vibedrive-web:latest
```

## Cloud Deployment (Planned)

### AWS Deployment

#### Terraform Setup
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file=production.tfvars

# Apply
terraform apply -var-file=production.tfvars
```

Resources provisioned:
- ECS Cluster for containerized workloads
- RDS PostgreSQL (Multi-AZ, automated backups)
- ElastiCache Redis
- Application Load Balancer (ALB)
- CloudFront CDN
- S3 buckets for assets/backups
- IAM roles and policies
- Security groups and VPC configuration

#### Environment Variables in AWS

Secrets stored in AWS Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name vibedrive/prod \
  --secret-string '{
    "JWT_SECRET": "...",
    "OPENAI_API_KEY": "...",
    "DATABASE_PASSWORD": "..."
  }'
```

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS)
- Helm 3+
- kubectl

#### Deploy with Helm

```bash
# Add Helm repository (when available)
helm repo add vibedrive https://helm.vibedrive.dev
helm repo update

# Install release
helm install vibedrive vibedrive/vibedrive \
  --namespace production \
  --create-namespace \
  --values values-prod.yaml

# Upgrade
helm upgrade vibedrive vibedrive/vibedrive \
  --namespace production \
  --values values-prod.yaml
```

#### Manual K8s Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Check rollout
kubectl rollout status deployment/vibedrive-api -n production

# Check pod status
kubectl get pods -n production

# View logs
kubectl logs -f deployment/vibedrive-api -n production
```

## CI/CD Pipeline

### GitHub Actions

Workflows defined in `.github/workflows/`:

1. **test.yml** — Run on every push/PR
   - Lint (ruff)
   - Tests (pytest)
   - Type check (mypy)
   - Frontend build (next build)

2. **deploy-staging.yml** — On merge to develop
   - Build Docker images
   - Push to staging registry
   - Deploy to staging cluster

3. **deploy-production.yml** — On tag release
   - Build Docker images
   - Push to production registry
   - Deploy to production cluster (manual approval)

### Example Workflow

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: cd backend && pytest tests/ -v
      - name: Lint
        run: cd backend && ruff check .
      - name: Frontend build
        run: cd frontend && npm ci && npm run build
```

## Monitoring & Observability

### Prometheus Setup

```bash
# Verify metrics endpoint
curl http://localhost:8000/metrics

# Configure Prometheus to scrape
# infrastructure/prometheus.yml
```

### Grafana Dashboards

Dashboards available at:
- API Performance: http://grafana:3000/d/api-performance
- Database Metrics: http://grafana:3000/d/database-health
- Resource Usage: http://grafana:3000/d/resource-usage

### Log Aggregation

Logs can be aggregated with ELK or Datadog:

```bash
# Local logs
tail -f py-vibe.log

# Container logs
docker logs -f vibedrive-api

# Kubernetes logs
kubectl logs -f deployment/vibedrive-api -n production
```

## Backup & Disaster Recovery

### Database Backups

**Automated**
- RDS automated backups (35-day retention)
- Point-in-time recovery enabled

**Manual**
```bash
# Backup PostgreSQL
pg_dump postgresql://user:pass@host:5432/vibedrive > backup.sql

# Restore
psql postgresql://user:pass@host:5432/vibedrive < backup.sql
```

### Data Exports

```bash
# Export user data
docker exec vibedrive-postgres pg_dump -U vibedrive vibedrive > export.sql

# Restore to new environment
docker exec vibedrive-postgres psql -U vibedrive vibedrive < export.sql
```

## Scaling

### Horizontal Scaling

**Backend**
```bash
# Docker Compose (manual)
docker compose -f infrastructure/docker-compose.yml up -d --scale api=3

# Kubernetes
kubectl scale deployment vibedrive-api --replicas=5 -n production
```

**Frontend**
```bash
# Kubernetes
kubectl scale deployment vibedrive-web --replicas=3 -n production
```

### Database Scaling

**Read Replicas** (RDS)
- Enable read replicas in RDS console
- Update app to use read replica for SELECT queries

**Connection Pooling**
- Use PgBouncer or RDS Proxy
- Configure pool size: `backend/src/db/database.py`

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose -f infrastructure/docker-compose.yml logs api

# Health checks
docker compose -f infrastructure/docker-compose.yml ps

# Rebuild
docker compose -f infrastructure/docker-compose.yml up -d --build
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker compose -f infrastructure/docker-compose.yml exec postgres pg_isready

# Check connection string in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### High Memory Usage

```bash
# Check resource limits
docker stats vibedrive-api

# Update limits in docker-compose.yml
# Or Kubernetes resource requests/limits in k8s manifests
```

## Rollback Procedures

### Docker Compose
```bash
# Revert to previous image
docker pull vibedrive-api:v1.0.0
docker compose -f infrastructure/docker-compose.yml up -d api
```

### Kubernetes
```bash
# Check rollout history
kubectl rollout history deployment/vibedrive-api -n production

# Rollback to previous
kubectl rollout undo deployment/vibedrive-api -n production

# Rollback to specific revision
kubectl rollout undo deployment/vibedrive-api --to-revision=3 -n production
```

### Git
```bash
# Revert last commit
git revert HEAD

# Force push (use with caution!)
git push --force-with-lease
```

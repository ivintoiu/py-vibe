.PHONY: help smoke all install dev test lint format clean docker-up docker-down db-migrate seed pre-commit-install docker-test db-downgrade

help:
	@echo "VibeDrive - Flask Monolith"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Quick Start:"
	@echo "  make all               Install, format, lint, and test"
	@echo ""
	@echo "Development:"
	@echo "  make install           Install dependencies"
	@echo "  make pre-commit-install Install pre-commit hooks"
	@echo "  make dev               Run Flask dev server"
	@echo "  make test              Run test suite"
	@echo "  make lint              Run linting checks"
	@echo "  make format            Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up         Start Docker services (dev)"
	@echo "  make docker-down       Stop Docker services"
	@echo "  make docker-test       Run tests in Docker"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate        Apply migrations"
	@echo "  make db-downgrade      Rollback one migration"
	@echo "  make seed              Seed database with test data"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean             Remove caches and builds"

smoke:
#    Smoke test all dev tools
   pytest --version && ruff --version && black --version && mypy --version && python -c "import flask_testing; print('flask-testing OK')"

all:
	@echo "🚀 Running full development setup..."
	$(MAKE) install
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test
	@echo ""
	@echo "✅ All tasks complete! Ready to develop."

install:
	@echo "📦 Installing dependencies..."
	uv sync --extra dev --no-install-project || (echo "❌ Installation failed" && exit 1)
	@echo "✓ Dependencies installed"

pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install || (echo "❌ Pre-commit installation failed" && exit 1)
	@echo "✓ Pre-commit hooks installed"

dev:
	@echo "🚀 Starting Flask development server..."
	APP_ENV=development python main.py || (echo "❌ Server crashed" && exit 1)

test:
	@echo "🧪 Running test suite with coverage..."
	pytest tests/ -v --cov=app --cov-report=html || (echo "❌ Tests failed" && exit 1)
	@echo "✓ Tests complete (see htmlcov/index.html for coverage)"

lint:
	@echo "🔍 Running linting checks..."
	ruff check . || (echo "❌ Ruff checks failed" && exit 1)
	black --check app/ tests/ || (echo "❌ Black formatting check failed" && exit 1)
	mypy app/ || (echo "❌ Type checking failed" && exit 1)
	@echo "✓ All linting checks passed"

format:
	@echo "🎨 Formatting code..."
	black app/ tests/ || (echo "❌ Black formatting failed" && exit 1)
	ruff check . --fix || (echo "❌ Ruff fix failed" && exit 1)
	@echo "✓ Code formatted"

clean:
	@echo "🧹 Cleaning Python cache and build artifacts..."
	python shared/clean.py || (echo "❌ Clean failed" && exit 1)
	@echo "✓ Clean complete"

docker-up:
	@echo "🐳 Starting Docker services..."
	docker compose up -d || (echo "❌ Docker start failed" && exit 1)
	@echo "✓ App running at http://localhost:5000"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker compose down || (echo "❌ Docker stop failed" && exit 1)
	@echo "✓ Docker services stopped"

docker-test:
	@echo "🐳 Running tests in Docker..."
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit || (echo "❌ Docker tests failed" && exit 1)
	@echo "✓ Docker tests complete"

db-migrate:
	@echo "📊 Applying database migrations..."
	alembic upgrade head || (echo "❌ Migration failed" && exit 1)
	@echo "✓ Migrations complete"

db-downgrade:
	@echo "⏮️  Rolling back one migration..."
	alembic downgrade -1 || (echo "❌ Rollback failed" && exit 1)
	@echo "✓ Rollback complete"

seed:
	@echo "🌱 Seeding database with test data..."
	python scripts/seed.py || (echo "❌ Seed failed" && exit 1)
	@echo "✓ Seed complete"

.DEFAULT_GOAL := help

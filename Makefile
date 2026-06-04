.PHONY: help install dev test lint format clean docker-up docker-down db-migrate seed

help:
	@echo "VibeDrive - Flask Monolith"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install dependencies"
	@echo "  make dev           Run Flask dev server"
	@echo "  make test          Run test suite"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     Start Docker services (dev)"
	@echo "  make docker-down   Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate    Apply migrations"
	@echo "  make seed          Seed database with test data"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove caches and builds"

install:
	pip install -e ".[dev]"

dev:
	ENVIRONMENT=development python main.py

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check .
	black --check app/ tests/
	mypy app/

format:
	black app/ tests/
	ruff check . --fix

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage

docker-up:
	docker compose up -d
	@echo "App running at http://localhost:5000"

docker-down:
	docker compose down

docker-test:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

seed:
	python scripts/seed.py

.DEFAULT_GOAL := help

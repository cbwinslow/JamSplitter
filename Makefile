.PHONY: help install test lint format check-format type-check security-check check pre-commit clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  check-format - Check code formatting"
	@echo "  type-check  - Run type checking"
	@echo "  security-check - Run security checks"
	@echo "  check       - Run all checks (lint, format, type-check, security)"
	@echo "  pre-commit  - Run pre-commit checks"
	@echo "  clean       - Clean up temporary files"

# Install development dependencies
install:
	pip install -e '.[dev]'
	pre-commit install

# Run tests
test:
	pytest -v --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml

# Run linting checks
lint:
	ruff check .
	black --check .
	isort --check-only .

# Format code
format:
	black .
	isort .

# Check code formatting
check-format:
	black --check .
	isort --check-only .

# Run type checking
type-check:
	mypy .

# Run security checks
security-check:
	bandit -r app

# Run all checks
check: lint check-format type-check security-check

# Run pre-commit checks
pre-commit:
	pre-commit run --all-files

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -f .coverage coverage.xml

# Docker compose commands
docker-up:
	docker-compose -f docker-compose.dev.yml up --build

docker-down:
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Database commands
db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-revision:
	alembic revision --autogenerate -m "$(m)"

# Development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
prod:
	gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

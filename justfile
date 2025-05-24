# Justfile for JamSplitter
# Install Just: https://github.com/casey/just

# Default target
default:
    just --list

# Run tests
pytest args="":
    #!/usr/bin/env bash
    set -euxo pipefail
    python -m pytest {{args}}

# Run tests with coverage
coverage:
    #!/usr/bin/env bash
    set -euxo pipefail
    python -m pytest --cov=src --cov-report=term-missing

# Run linters
lint:
    #!/usr/bin/env bash
    set -euxo pipefail
    black --check .
    isort --check-only .
    flake8 .
    mypy .

# Format code
format:
    #!/usr/bin/env bash
    set -euxo pipefail
    black .
    isort .

# Run development server
dev:
    #!/usr/bin/env bash
    set -euxo pipefail
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
docker-build:
    #!/usr/bin/env bash
    set -euxo pipefail
    docker-compose build

# Start services
docker-up:
    #!/usr/bin/env bash
    set -euxo pipefail
    docker-compose up -d

# Stop services
docker-down:
    #!/usr/bin/env bash
    set -euxo pipefail
    docker-compose down

# View logs
docker-logs service="":
    #!/usr/bin/env bash
    set -euxo pipefail
    if [ -z "{{service}}" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f {{service}}
    fi

# Run migrations
migrate message:
    #!/usr/bin/env bash
    set -euxo pipefail
    alembic revision --autogenerate -m "{{message}}"
    alembic upgrade head

# Install dependencies
install:
    #!/usr/bin/env bash
    set -euxo pipefail
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pre-commit install

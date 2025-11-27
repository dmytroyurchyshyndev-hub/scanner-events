.PHONY: help install dev run test clean docker-up docker-down docker-logs db-init db-migrate db-upgrade db-downgrade db-current db-history db-reset shell lint format

# Variables
APP = app.main:app
PYTHON = python
LITESTAR = litestar --app $(APP)
DOCKER_COMPOSE = docker-compose

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Install dev dependencies"
	@echo "  make run            - Run the application"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up cache files"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-restart - Restart Docker containers"
	@echo ""
	@echo "Database commands:"
	@echo "  make db-init        - Initialize database migrations"
	@echo "  make db-migrate MSG='message' - Create new migration"
	@echo "  make db-upgrade     - Apply all migrations"
	@echo "  make db-downgrade   - Rollback one migration"
	@echo "  make db-current     - Show current migration"
	@echo "  make db-history     - Show migration history"
	@echo "  make db-reset       - Reset database (downgrade all + upgrade)"
	@echo ""
	@echo "Development commands:"
	@echo "  make shell          - Open Python shell with app context"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"

# Installation
install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

# Run application
run:
	$(LITESTAR) run --reload

# Testing
test:
	pytest

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Docker commands
docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f

docker-restart:
	$(DOCKER_COMPOSE) restart

docker-clean:
	$(DOCKER_COMPOSE) down -v

# Database commands
db-init:
	$(LITESTAR) database init ./migrations

db-migrate:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a migration message with MSG='your message'"; \
		echo "Example: make db-migrate MSG='add users table'"; \
		exit 1; \
	fi
	$(LITESTAR) database make-migrations -m "$(MSG)"

db-upgrade:
	$(LITESTAR) database upgrade

db-downgrade:
	$(LITESTAR) database downgrade -1

db-current:
	$(LITESTAR) database current

db-history:
	$(LITESTAR) database history

db-reset:
	$(LITESTAR) database downgrade base
	$(LITESTAR) database upgrade

db-revision:
	$(LITESTAR) database show head

# Development tools
shell:
	$(PYTHON) -i -c "from app.main import app; print('App loaded. Available: app')"

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

# Quick setup for new developers
setup: docker-up install db-init db-migrate db-upgrade
	@echo "Setup complete! Run 'make run' to start the application."

# Full application start (with Docker)
start: docker-up
	@echo "Waiting for database to be ready..."
	@sleep 3
	$(MAKE) db-upgrade
	$(MAKE) run

# Stop everything
stop: docker-down
	@echo "All services stopped."
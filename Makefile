# Makefile for PhD Timeline Intelligence Platform

.PHONY: help install setup-dev up down logs clean test lint

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements-dev.txt
	@echo "Installation complete!"

setup-dev: ## Setup development environment
	@echo "Setting up development environment..."
	cp backend/.env.example backend/.env || true
	@echo "Please update .env file with your configuration"

up: ## Start all services with Docker Compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

clean: ## Clean up containers, volumes, and build artifacts
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

test-backend: ## Run backend tests
	cd backend && pytest

test: test-backend ## Run all tests

lint-backend: ## Lint backend code
	cd backend && flake8 app/ && black --check app/ && mypy app/

lint: lint-backend ## Lint all code

format-backend: ## Format backend code
	cd backend && black app/

format: format-backend ## Format all code

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload

backup-db: ## Backup database
	./infra/scripts/backup-db.sh

healthcheck: ## Check health of all services
	./infra/monitoring/healthcheck.sh

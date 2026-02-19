#!/bin/bash

# Deployment script for PhD Timeline Intelligence Platform
# This script should be customized based on your deployment environment

set -e

echo "Starting deployment..."

COMPOSE_FILE="infra/docker-compose.prod.yml"

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build and deploy with Docker Compose
echo "Building Docker images..."
docker compose -f "$COMPOSE_FILE" build --pull

echo "Ensuring database is up..."
docker compose -f "$COMPOSE_FILE" up -d postgres

# Run database migrations before rotating app services
echo "Running database migrations..."
docker compose -f "$COMPOSE_FILE" run --rm backend alembic upgrade head

# Start/update application services with minimal disruption
echo "Starting/updating backend and frontend..."
docker compose -f "$COMPOSE_FILE" up -d backend frontend

# Health check
echo "Performing health check..."
for i in {1..20}; do
	if curl -fsS http://localhost:8000/health >/dev/null; then
		echo "Backend health check passed"
		break
	fi
	if [[ $i -eq 20 ]]; then
		echo "Backend health check failed"
		exit 1
	fi
	sleep 3
done

for i in {1..20}; do
	if curl -fsS http://localhost/ >/dev/null; then
		echo "Frontend health check passed"
		break
	fi
	if [[ $i -eq 20 ]]; then
		echo "Frontend health check failed"
		exit 1
	fi
	sleep 3
done

echo "Deployment completed successfully!"

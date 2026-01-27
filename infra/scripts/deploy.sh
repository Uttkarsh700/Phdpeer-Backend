#!/bin/bash

# Deployment script for PhD Timeline Intelligence Platform
# This script should be customized based on your deployment environment

set -e

echo "Starting deployment..."

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build and deploy with Docker Compose
echo "Building Docker images..."
docker-compose -f infra/docker-compose.prod.yml build

echo "Stopping existing containers..."
docker-compose -f infra/docker-compose.prod.yml down

echo "Starting new containers..."
docker-compose -f infra/docker-compose.prod.yml up -d

# Run database migrations
echo "Running database migrations..."
docker-compose -f infra/docker-compose.prod.yml exec -T backend alembic upgrade head

# Health check
echo "Performing health check..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment completed successfully!"

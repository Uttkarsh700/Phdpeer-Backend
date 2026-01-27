# Infrastructure Configuration

This folder contains infrastructure configuration files for the PhD Timeline Intelligence Platform.

## Contents

### 🐳 Docker
- Dockerfiles for all services
- Docker Compose configurations
- Container orchestration setup

### 🔧 Environment Templates
- Environment variable templates
- Configuration examples
- Secrets management guidelines

### 📦 Deployment
- Deployment scripts
- CI/CD configurations
- Production setup guides

## Quick Start

### Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Production Deployment

See [deployment guide](../resources/docs/deployment-guide.md) for production setup instructions.

## Services

### PostgreSQL Database
- **Port**: 5432
- **Image**: postgres:15-alpine
- **Volume**: postgres_data

### Backend API
- **Port**: 8000
- **Framework**: FastAPI
- **Auto-reload**: Enabled in development

### Frontend
- **Port**: 3000
- **Framework**: React + Vite
- **Hot-reload**: Enabled in development

## Environment Variables

See `.env.example` files in respective directories:
- `/backend/.env.example`
- `/frontend/.env.example`

## Health Checks

All services include health checks:
- Database: `pg_isready`
- Backend: `/health` endpoint
- Frontend: HTTP availability check

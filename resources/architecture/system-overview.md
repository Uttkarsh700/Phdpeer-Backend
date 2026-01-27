# System Architecture Overview

## Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Database**: PostgreSQL

## High-Level Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTPS
       │
┌──────▼──────────┐
│   Frontend      │
│  React + Vite   │
└──────┬──────────┘
       │
       │ REST API
       │
┌──────▼──────────┐
│    Backend      │
│    FastAPI      │
└──────┬──────────┘
       │
       │ SQL
       │
┌──────▼──────────┐
│   PostgreSQL    │
│    Database     │
└─────────────────┘
```

## API Design
- RESTful API
- JSON request/response format
- JWT authentication
- Versioned endpoints (/api/v1)

## Database Design
[To be defined]

---
*This document will be expanded as the architecture evolves.*

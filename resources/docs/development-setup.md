# Development Setup Guide

## Prerequisites

### Required Software
- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **PostgreSQL**: 15 or higher
- **Docker**: Latest version
- **Git**: Latest version

### Recommended Tools
- VS Code or your preferred IDE
- Postman or Insomnia for API testing
- pgAdmin or DBeaver for database management

## Setup Instructions

### 1. Clone Repository
```bash
git clone <repository-url>
cd Frensei-Engine
```

### 2. Environment Configuration
Create `.env` files in both frontend and backend directories using the `.env.example` templates.

### 3. Database Setup
```bash
# Using Docker
docker-compose up -d postgres

# Or install PostgreSQL locally and create database
createdb phd_timeline_db
```

### 4. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Verification

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Common Issues
[To be documented as they arise]

---
*Update this guide as the development process evolves.*

# PhD Timeline Backend

FastAPI backend for the PhD Timeline Intelligence Platform.

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **Python**: 3.11+
- **PostgreSQL**: 15+ database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and settings

## Project Structure

```
app/
├── config.py           # Application configuration
├── database.py         # Database connection & session
├── main.py            # FastAPI application entry point
├── models/            # SQLAlchemy database models
│   ├── __init__.py
│   ├── base.py        # Base model with common fields
│   ├── user.py
│   ├── document_artifact.py
│   ├── baseline.py
│   ├── draft_timeline.py
│   ├── committed_timeline.py
│   ├── timeline_stage.py
│   ├── timeline_milestone.py
│   ├── progress_event.py
│   └── journey_assessment.py
├── routes/            # API route definitions
│   └── __init__.py
├── schemas/           # Pydantic schemas for validation
│   ├── __init__.py
│   └── base.py        # Base schemas
├── services/          # Business logic & data access
│   ├── __init__.py
│   ├── base.py        # Base service with CRUD operations
│   └── document_service.py  # Document upload & text extraction
├── orchestrators/     # Complex workflow coordination
│   └── __init__.py
└── utils/             # Utility functions
    ├── __init__.py
    ├── file_utils.py      # File handling utilities
    └── text_extractor.py  # Text extraction from PDF/DOCX

alembic/               # Database migrations
tests/                 # Test files
```

## Architecture Patterns

### Models
SQLAlchemy ORM models representing database tables.
- Located in `app/models/`
- Inherit from `Base` (declarative_base)
- Define database schema

### Schemas
Pydantic models for request/response validation.
- Located in `app/schemas/`
- Define API contracts
- Provide validation and serialization

### Services
Business logic and data access layer.
- Located in `app/services/`
- Handle CRUD operations
- Implement business rules
- Single responsibility per service

### Orchestrators
Coordinate multiple services for complex workflows.
- Located in `app/orchestrators/`
- Handle multi-service operations
- Manage cross-cutting concerns
- Implement complex business processes

### Routes
API endpoint definitions.
- Located in `app/routes/`
- Define HTTP endpoints
- Handle request/response
- Thin layer that delegates to services/orchestrators

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- pip or poetry

### Installation

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `ALLOWED_ORIGINS`: CORS allowed origins

### Database Setup

Run database migrations:

```bash
alembic upgrade head
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs (Swagger)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

## Services

### DocumentService

Handles document uploads and text extraction.

**Supported File Types:**
- PDF (.pdf)
- DOCX (.docx)

**Features:**
- File validation
- Text extraction (deterministic, no analysis)
- File storage
- DocumentArtifact creation

**Usage:**
```python
from app.services import DocumentService
from app.database import get_db

db = next(get_db())
service = DocumentService(db)

# Upload document
document_id = service.upload_document(
    user_id=user.id,
    file_content=file.read(),
    filename="research_proposal.pdf",
    title="My Research Proposal",
    document_type="proposal"
)

# Get extracted text
text = service.get_extracted_text(document_id)
```

## Development Workflow

### Adding a New Feature

1. **Create Model** (if needed)
   ```python
   # app/models/feature.py
   from sqlalchemy import Column, String
   from app.database import Base
   from app.models.base import BaseModel
   
   class Feature(Base, BaseModel):
       __tablename__ = "features"
       name = Column(String, nullable=False)
   ```

2. **Create Schemas**
   ```python
   # app/schemas/feature.py
   from app.schemas.base import BaseSchema, TimestampSchema
   
   class FeatureBase(BaseSchema):
       name: str
   
   class FeatureCreate(FeatureBase):
       pass
   
   class FeatureResponse(FeatureBase, TimestampSchema):
       pass
   ```

3. **Create Service**
   ```python
   # app/services/feature.py
   from sqlalchemy.orm import Session
   from app.services.base import BaseService
   from app.models.feature import Feature
   
   class FeatureService(BaseService[Feature]):
       def __init__(self, db: Session):
           super().__init__(Feature, db)
   ```

4. **Create Routes**
   ```python
   # app/routes/feature.py
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.database import get_db
   from app.services.feature import FeatureService
   from app.schemas.feature import FeatureCreate, FeatureResponse
   
   router = APIRouter()
   
   @router.get("/", response_model=list[FeatureResponse])
   def list_features(db: Session = Depends(get_db)):
       service = FeatureService(db)
       return service.get_multi()
   ```

5. **Register Routes**
   ```python
   # app/routes/__init__.py
   from app.routes import feature
   api_router.include_router(feature.router, prefix="/features", tags=["features"])
   ```

6. **Create Migration**
   ```bash
   alembic revision --autogenerate -m "Add feature model"
   alembic upgrade head
   ```

### Code Quality

Format code:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```

Type check:
```bash
mypy app/
```

### Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | PhD Timeline Intelligence Platform |
| DEBUG | Debug mode | False |
| ENVIRONMENT | Environment (dev/staging/prod) | production |
| DATABASE_URL | PostgreSQL connection URL | Required |
| DATABASE_ECHO | Echo SQL queries | False |
| SECRET_KEY | JWT secret key | Required |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration | 30 |
| ALLOWED_ORIGINS | CORS allowed origins | http://localhost:3000 |
| API_V1_PREFIX | API version prefix | /api/v1 |

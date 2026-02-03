"""Database connection and session management."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# Create SQLAlchemy engine with conditional parameters
# SQLite doesn't support pool_size and max_overflow
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}  # SQLite-specific
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    # #region agent log
    import json
    with open(r'd:\Frensei-Engine\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"database.py:49","message":"Creating database session","data":{"database_url":settings.DATABASE_URL[:50] if hasattr(settings, 'DATABASE_URL') else 'NOT_SET'},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
    db = SessionLocal()
    try:
        # #region agent log
        with open(r'd:\Frensei-Engine\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"database.py:52","message":"Database session created successfully","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database.
    Creates all tables defined in models.
    
    Note: In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)

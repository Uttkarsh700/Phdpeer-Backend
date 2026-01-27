"""Base model with common fields for all models."""
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
import uuid


class BaseModel:
    """
    Base model mixin with common fields.
    
    Provides:
        - id: UUID primary key
        - created_at: Timestamp of creation
        - updated_at: Timestamp of last update
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

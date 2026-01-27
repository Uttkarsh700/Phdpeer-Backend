"""Base schemas with common fields."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    id: int
    created_at: datetime
    updated_at: datetime


class ResponseSchema(BaseSchema):
    """Generic API response schema."""
    
    success: bool = True
    message: str = "Success"
    data: dict | list | None = None


class PaginationSchema(BaseSchema):
    """Pagination metadata schema."""
    
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool

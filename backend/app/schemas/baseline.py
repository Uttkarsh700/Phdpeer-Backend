"""Pydantic schemas for Baseline model."""
from datetime import date
from typing import Optional
from uuid import UUID

from app.schemas.base import BaseSchema, TimestampSchema


class BaselineBase(BaseSchema):
    """Base baseline schema with common fields."""
    
    program_name: str
    institution: str
    field_of_study: str
    start_date: date
    expected_end_date: Optional[date] = None
    total_duration_months: Optional[int] = None
    requirements_summary: Optional[str] = None
    research_area: Optional[str] = None
    advisor_info: Optional[str] = None
    funding_status: Optional[str] = None
    notes: Optional[str] = None


class BaselineCreate(BaselineBase):
    """Schema for creating a baseline."""
    
    document_id: Optional[UUID] = None


class BaselineUpdate(BaseSchema):
    """
    Schema for baseline updates.
    
    Note: Baselines are immutable by design.
    This schema is provided for completeness but updates should be restricted.
    """
    
    notes: Optional[str] = None  # Only notes can be updated


class BaselineResponse(BaselineBase, TimestampSchema):
    """Schema for baseline responses."""
    
    user_id: UUID
    document_artifact_id: Optional[UUID] = None


class BaselineWithDocument(BaselineResponse):
    """Schema for baseline with document information."""
    
    document_title: Optional[str] = None
    document_type: Optional[str] = None

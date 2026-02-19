"""Generic scoring configuration model for versioned engine weights."""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base
from app.models.base import BaseModel


class ScoringConfig(Base, BaseModel):
    """Versioned, runtime-updatable scoring config per engine."""

    __tablename__ = "scoring_configs"

    engine_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    weights_json = Column(JSONB, nullable=False)
    thresholds_json = Column(JSONB, nullable=True)
    notes = Column(String, nullable=True)

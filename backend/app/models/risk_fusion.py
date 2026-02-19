"""Models for composite risk fusion configuration and snapshots."""
from sqlalchemy import Column, String, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class RiskWeightConfig(Base, BaseModel):
    """Versioned and configurable risk fusion weights/thresholds."""

    __tablename__ = "risk_weight_configs"

    version = Column(String(50), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    weights_json = Column(JSONB, nullable=False)
    thresholds_json = Column(JSONB, nullable=False)
    notes = Column(String, nullable=True)


class RiskAssessmentSnapshot(Base, BaseModel):
    """Persisted composite risk score output with full explainability snapshots."""

    __tablename__ = "risk_assessment_snapshots"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timeline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("committed_timelines.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    scoring_version = Column(String(50), nullable=False, index=True)
    config_version = Column(String(50), nullable=False, index=True)
    composite_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    contributing_signals = Column(JSONB, nullable=False)
    threshold_breaches = Column(JSONB, nullable=False)
    weight_snapshot = Column(JSONB, nullable=False)
    input_snapshot = Column(JSONB, nullable=False)

    user = relationship("User")
    timeline = relationship("CommittedTimeline")

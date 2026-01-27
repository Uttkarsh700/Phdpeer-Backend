"""DraftTimeline model."""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class DraftTimeline(Base, BaseModel):
    """
    DraftTimeline model representing a timeline in draft/planning state.
    
    Draft timelines can be edited, revised, and iterated upon before
    being committed to a final timeline.
    
    Attributes:
        user_id: Reference to the user
        baseline_id: Reference to the baseline this timeline is based on
        title: Timeline title
        description: Timeline description
        version_number: Version number for tracking iterations
        is_active: Whether this is the active draft
        notes: Additional notes
    """
    
    __tablename__ = "draft_timelines"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    baseline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("baselines.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="draft_timelines")
    baseline = relationship("Baseline", back_populates="draft_timelines")
    timeline_stages = relationship(
        "TimelineStage",
        back_populates="draft_timeline",
        cascade="all, delete-orphan",
        foreign_keys="TimelineStage.draft_timeline_id"
    )

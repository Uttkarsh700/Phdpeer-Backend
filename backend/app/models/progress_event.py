"""ProgressEvent model."""
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SqlEnum, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class ProgressEventType(str, Enum):
    """Allowed progress event types."""

    MILESTONE_COMPLETED = "milestone_completed"
    MILESTONE_DELAYED = "milestone_delayed"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    ACHIEVEMENT = "achievement"
    BLOCKER = "blocker"
    UPDATE = "update"


class ProgressEvent(Base, BaseModel):
    """
    ProgressEvent model for tracking progress activities and updates.
    
    Progress events capture updates, achievements, blockers, and other
    notable events in the PhD journey.
    
    Attributes:
        user_id: Reference to the user
        milestone_id: Reference to related milestone (optional)
        event_type: Type of event (achievement, blocker, update, etc.)
        title: Event title
        description: Event description
        event_date: DateTime of the event (timezone-aware)
        impact_level: Impact level (low, medium, high)
        tags: Tag array for categorization
        notes: Additional notes
    """
    
    __tablename__ = "progress_events"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    milestone_id = Column(
        UUID(as_uuid=True),
        ForeignKey("timeline_milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    event_type = Column(
        SqlEnum(ProgressEventType, name="progress_event_type"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    impact_level = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress_events")
    milestone = relationship("TimelineMilestone", back_populates="progress_events")

    __table_args__ = (
        Index("ix_progress_events_tags_gin", "tags", postgresql_using="gin"),
    )

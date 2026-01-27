"""ProgressEvent model."""
from sqlalchemy import Column, String, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


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
        event_date: Date of the event
        impact_level: Impact level (low, medium, high)
        tags: Comma-separated tags for categorization
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
    event_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)
    impact_level = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress_events")
    milestone = relationship("TimelineMilestone", back_populates="progress_events")

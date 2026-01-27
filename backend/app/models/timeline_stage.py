"""TimelineStage model."""
from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class TimelineStage(Base, BaseModel):
    """
    TimelineStage model representing major phases in a PhD timeline.
    
    Stages represent major phases like Literature Review, Research,
    Writing, Defense Preparation, etc.
    
    Attributes:
        draft_timeline_id: Reference to draft timeline (if in draft)
        committed_timeline_id: Reference to committed timeline (if committed)
        title: Stage title
        description: Stage description
        stage_order: Order of this stage in the timeline
        start_date: Planned start date
        end_date: Planned end date
        duration_months: Expected duration in months
        status: Current status (not_started, in_progress, completed)
        notes: Additional notes
    """
    
    __tablename__ = "timeline_stages"
    
    draft_timeline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("draft_timelines.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    committed_timeline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("committed_timelines.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    stage_order = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    duration_months = Column(Integer, nullable=True)
    status = Column(String, default="not_started", nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    draft_timeline = relationship(
        "DraftTimeline",
        back_populates="timeline_stages",
        foreign_keys=[draft_timeline_id]
    )
    committed_timeline = relationship(
        "CommittedTimeline",
        back_populates="timeline_stages",
        foreign_keys=[committed_timeline_id]
    )
    milestones = relationship(
        "TimelineMilestone",
        back_populates="timeline_stage",
        cascade="all, delete-orphan"
    )

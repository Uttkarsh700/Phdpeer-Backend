"""TimelineEditHistory model for tracking changes to draft timelines."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class TimelineEditHistory(Base, BaseModel):
    """
    TimelineEditHistory model for tracking all edits made to a draft timeline.
    
    Records every change made to a draft timeline before commitment,
    providing full audit trail and rollback capability.
    
    Attributes:
        draft_timeline_id: Reference to the draft timeline
        user_id: Reference to the user who made the edit
        edit_type: Type of edit (stage_added, stage_modified, milestone_added, etc.)
        entity_type: Type of entity edited (timeline, stage, milestone)
        entity_id: ID of the entity edited
        changes_json: JSON object with before/after values
        description: Human-readable description of the change
    """
    
    __tablename__ = "timeline_edit_history"
    
    draft_timeline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("draft_timelines.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    edit_type = Column(String, nullable=False)  # added, modified, deleted, reordered
    entity_type = Column(String, nullable=False)  # timeline, stage, milestone
    entity_id = Column(UUID(as_uuid=True), nullable=True)  # ID of edited entity
    changes_json = Column(JSONB, nullable=False)  # {"field": {"before": X, "after": Y}}
    description = Column(Text, nullable=True)  # Human-readable description
    
    # Relationships
    draft_timeline = relationship("DraftTimeline", backref="edit_history")
    user = relationship("User")
    
    def __repr__(self):
        return f"<TimelineEditHistory(type='{self.edit_type}', entity='{self.entity_type}:{self.entity_id}')>"

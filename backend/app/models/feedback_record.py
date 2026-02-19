"""FeedbackRecord model for dedicated feedback storage."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class FeedbackRecord(Base, BaseModel):
    """
    FeedbackRecord model for storing feedback on timeline predictions.

    Captures corrections made to LLM-generated timelines, enabling the system
    to learn from feedback and improve future predictions.

    Attributes:
        user_id: Reference to the user who received/made the correction
        feedback_type: Type of feedback (duration_correction, stage_correction, etc.)
        source: Who provided the feedback (supervisor, student, system)
        entity_type: Type of entity corrected (stage, milestone, timeline)
        entity_id: ID of the specific entity being corrected (nullable)
        original_value: What the system predicted (JSONB)
        corrected_value: What it was corrected to (JSONB)
        correction_delta: The difference/adjustment (JSONB)
        discipline: Field of study for pattern grouping (nullable)
        notes: Additional context or comments
    """

    __tablename__ = "feedback_records"

    # Valid feedback types
    FEEDBACK_TYPE_DURATION = "duration_correction"
    FEEDBACK_TYPE_STAGE = "stage_correction"
    FEEDBACK_TYPE_MILESTONE = "milestone_correction"
    FEEDBACK_TYPE_RESTRUCTURE = "timeline_restructure"
    FEEDBACK_TYPE_COMMENT = "supervisor_comment"

    VALID_FEEDBACK_TYPES = [
        FEEDBACK_TYPE_DURATION,
        FEEDBACK_TYPE_STAGE,
        FEEDBACK_TYPE_MILESTONE,
        FEEDBACK_TYPE_RESTRUCTURE,
        FEEDBACK_TYPE_COMMENT,
    ]

    # Valid sources
    SOURCE_SUPERVISOR = "supervisor"
    SOURCE_STUDENT = "student"
    SOURCE_SYSTEM = "system"

    VALID_SOURCES = [
        SOURCE_SUPERVISOR,
        SOURCE_STUDENT,
        SOURCE_SYSTEM,
    ]

    # Valid entity types
    ENTITY_TYPE_STAGE = "stage"
    ENTITY_TYPE_MILESTONE = "milestone"
    ENTITY_TYPE_TIMELINE = "timeline"

    VALID_ENTITY_TYPES = [
        ENTITY_TYPE_STAGE,
        ENTITY_TYPE_MILESTONE,
        ENTITY_TYPE_TIMELINE,
    ]

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    feedback_type = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    original_value = Column(JSONB, nullable=False)
    corrected_value = Column(JSONB, nullable=False)
    correction_delta = Column(JSONB, nullable=False)
    discipline = Column(String, nullable=True, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref="feedback_records")

    def __repr__(self):
        return f"<FeedbackRecord(type='{self.feedback_type}', entity='{self.entity_type}', source='{self.source}')>"

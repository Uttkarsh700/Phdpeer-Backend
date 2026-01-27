"""JourneyAssessment model."""
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class JourneyAssessment(Base, BaseModel):
    """
    JourneyAssessment model for periodic assessments of PhD progress.
    
    Assessments capture qualitative and quantitative evaluations of
    the PhD journey at various points in time.
    
    Attributes:
        user_id: Reference to the user
        assessment_date: Date of assessment
        assessment_type: Type of assessment (self, advisor, quarterly, etc.)
        overall_progress_rating: Overall progress rating (1-10)
        research_quality_rating: Research quality rating (1-10)
        timeline_adherence_rating: Timeline adherence rating (1-10)
        strengths: Identified strengths
        challenges: Identified challenges
        action_items: Action items from assessment
        advisor_feedback: Feedback from advisor
        notes: Additional notes
    """
    
    __tablename__ = "journey_assessments"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    assessment_date = Column(Date, nullable=False)
    assessment_type = Column(String, nullable=False)
    overall_progress_rating = Column(Integer, nullable=True)
    research_quality_rating = Column(Integer, nullable=True)
    timeline_adherence_rating = Column(Integer, nullable=True)
    strengths = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    advisor_feedback = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="journey_assessments")

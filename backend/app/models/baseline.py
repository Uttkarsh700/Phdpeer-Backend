"""Baseline model."""
from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class Baseline(Base, BaseModel):
    """
    Baseline model representing initial PhD program assessment.
    
    Captures the starting point of a PhD journey including program details,
    requirements, and initial timeline expectations.
    
    Attributes:
        user_id: Reference to the user
        document_artifact_id: Reference to the source document (optional)
        program_name: Name of the PhD program
        institution: Academic institution
        field_of_study: Research field
        start_date: Program start date
        expected_end_date: Expected completion date
        total_duration_months: Expected duration in months
        requirements_summary: Summary of program requirements
        research_area: Specific research area/topic
        advisor_info: Information about advisor(s)
        funding_status: Funding information
        notes: Additional notes
    """
    
    __tablename__ = "baselines"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    document_artifact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_artifacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    program_name = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    field_of_study = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    expected_end_date = Column(Date, nullable=True)
    total_duration_months = Column(Integer, nullable=True)
    requirements_summary = Column(Text, nullable=True)
    research_area = Column(Text, nullable=True)
    advisor_info = Column(Text, nullable=True)
    funding_status = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="baselines")
    document_artifact = relationship("DocumentArtifact", back_populates="baseline")
    draft_timelines = relationship(
        "DraftTimeline",
        back_populates="baseline",
        cascade="all, delete-orphan"
    )

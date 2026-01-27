"""QuestionnaireDraft model for saving incomplete questionnaire responses."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class QuestionnaireDraft(Base, BaseModel):
    """
    QuestionnaireDraft model for storing incomplete questionnaire responses.
    
    Allows users to save progress and resume later. Each draft is tied to
    a specific questionnaire version.
    
    Attributes:
        user_id: Reference to the user
        questionnaire_version_id: Reference to questionnaire version
        draft_name: Optional name for the draft
        responses_json: JSONB storing all responses (section-by-section)
        completed_sections: List of completed section IDs
        progress_percentage: Percentage of questions answered (0-100)
        is_submitted: Whether this draft has been submitted
        submission_id: Reference to JourneyAssessment if submitted
        last_section_edited: ID of last edited section
        metadata_json: Additional metadata (device, browser, etc.)
    """
    
    __tablename__ = "questionnaire_drafts"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    questionnaire_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questionnaire_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    draft_name = Column(String, nullable=True)
    responses_json = Column(JSONB, nullable=False, default={})
    completed_sections = Column(JSONB, nullable=False, default=[])
    progress_percentage = Column(Integer, nullable=False, default=0)
    is_submitted = Column(Boolean, nullable=False, default=False)
    submission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("journey_assessments.id", ondelete="SET NULL"),
        nullable=True
    )
    last_section_edited = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="questionnaire_drafts")
    questionnaire_version = relationship("QuestionnaireVersion", back_populates="drafts")
    submission = relationship("JourneyAssessment", backref="draft")
    
    def __repr__(self):
        return f"<QuestionnaireDraft(user_id='{self.user_id}', progress={self.progress_percentage}%)>"


class QuestionnaireVersion(Base, BaseModel):
    """
    QuestionnaireVersion model for versioning questionnaires.
    
    Tracks different versions of the questionnaire schema to ensure
    backwards compatibility and proper draft handling.
    
    Attributes:
        version_number: Version number (e.g., "1.0", "1.1", "2.0")
        title: Version title
        description: Description of changes in this version
        schema_json: Complete questionnaire schema (sections, questions, etc.)
        is_active: Whether this version is currently active
        is_deprecated: Whether this version is deprecated
        total_questions: Total number of questions
        total_sections: Total number of sections
        release_notes: Release notes for this version
    """
    
    __tablename__ = "questionnaire_versions"
    
    version_number = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    schema_json = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_deprecated = Column(Boolean, nullable=False, default=False)
    total_questions = Column(Integer, nullable=False, default=0)
    total_sections = Column(Integer, nullable=False, default=0)
    release_notes = Column(Text, nullable=True)
    
    # Relationships
    drafts = relationship(
        "QuestionnaireDraft",
        back_populates="questionnaire_version",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<QuestionnaireVersion(version='{self.version_number}', active={self.is_active})>"

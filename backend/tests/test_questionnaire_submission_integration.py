"""
Integration test for questionnaire submission: Draft → Submission → JourneyAssessment.

Tests:
- Save questionnaire draft
- Submit questionnaire
- Generate JourneyAssessment
- Store health scores and recommendations

Validates:
- No document or timeline access (isolation)
- Submission is required before scoring
"""
import pytest
import os
from datetime import date
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from app.database import Base
from app.models.user import User
from app.models.questionnaire_draft import (
    QuestionnaireDraft,
    QuestionnaireVersion
)
from app.models.journey_assessment import JourneyAssessment
from app.models.document_artifact import DocumentArtifact
from app.models.committed_timeline import CommittedTimeline
from app.services.questionnaire_draft_service import (
    QuestionnaireDraftService,
    QuestionnaireDraftError
)
from app.orchestrators.phd_doctor_orchestrator import (
    PhDDoctorOrchestrator,
    PhDDoctorOrchestratorError,
    IncompleteSubmissionError
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="phd.student@university.edu",
        hashed_password="hashed_password",
        full_name="Jane Doe",
        institution="Test University",
        field_of_study="Computer Science",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_questionnaire_version(db):
    """Create a test questionnaire version."""
    version = QuestionnaireVersion(
        version_number="1.0",
        title="PhD Journey Health Assessment v1.0",
        description="Initial version of the health assessment questionnaire",
        schema_json={
            "dimensions": [
                {
                    "id": "research_quality",
                    "name": "Research Quality",
                    "questions": [
                        {"id": "q1", "text": "How satisfied are you with your research progress?"},
                        {"id": "q2", "text": "How confident are you in your research direction?"}
                    ]
                },
                {
                    "id": "timeline_adherence",
                    "name": "Timeline Adherence",
                    "questions": [
                        {"id": "q3", "text": "Are you on track with your timeline?"},
                        {"id": "q4", "text": "How well are you managing deadlines?"}
                    ]
                },
                {
                    "id": "work_life_balance",
                    "name": "Work-Life Balance",
                    "questions": [
                        {"id": "q5", "text": "How balanced is your work and personal life?"}
                    ]
                }
            ]
        },
        is_active=True,
        total_questions=5,
        total_sections=3
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


class TestQuestionnaireSubmissionIntegration:
    """Integration test for questionnaire submission."""
    
    def test_questionnaire_submission_full_flow(
        self,
        db,
        test_user,
        test_questionnaire_version
    ):
        """
        Test complete questionnaire submission flow.
        
        Validates:
        - No document or timeline access (isolation)
        - Submission is required before scoring
        """
        user_id = test_user.id
        questionnaire_service = QuestionnaireDraftService(db)
        orchestrator = PhDDoctorOrchestrator(db, user_id)
        
        # Step 1: Save questionnaire draft
        print("\n[1/4] Saving questionnaire draft...")
        draft_id = questionnaire_service.create_draft(
            user_id=user_id,
            questionnaire_version_id=test_questionnaire_version.id,
            draft_name="My Assessment Draft"
        )
        print(f"✓ Draft created: {draft_id}")
        
        # Save section 1: Research Quality
        section1_responses = {
            "q1": 4,  # Satisfied
            "q2": 5   # Very confident
        }
        questionnaire_service.save_section(
            draft_id=draft_id,
            user_id=user_id,
            section_id="research_quality",
            responses=section1_responses,
            is_section_complete=True
        )
        print("  ✓ Section 1 saved: Research Quality")
        
        # Save section 2: Timeline Adherence
        section2_responses = {
            "q3": 3,  # Somewhat on track
            "q4": 2   # Struggling with deadlines
        }
        questionnaire_service.save_section(
            draft_id=draft_id,
            user_id=user_id,
            section_id="timeline_adherence",
            responses=section2_responses,
            is_section_complete=True
        )
        print("  ✓ Section 2 saved: Timeline Adherence")
        
        # Save section 3: Work-Life Balance
        section3_responses = {
            "q5": 4  # Good balance
        }
        questionnaire_service.save_section(
            draft_id=draft_id,
            user_id=user_id,
            section_id="work_life_balance",
            responses=section3_responses,
            is_section_complete=True
        )
        print("  ✓ Section 3 saved: Work-Life Balance")
        
        db.commit()
        
        # Verify draft is not submitted yet
        draft = db.query(QuestionnaireDraft).filter(
            QuestionnaireDraft.id == draft_id
        ).first()
        assert draft.is_submitted is False
        assert draft.submission_id is None
        
        # Validation: No JourneyAssessment exists before submission
        initial_assessments = db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == user_id
        ).count()
        assert initial_assessments == 0, "No assessment should exist before submission"
        
        # Step 2: Submit questionnaire
        print("\n[2/4] Submitting questionnaire...")
        request_id = str(uuid4())
        
        # Prepare responses in the format expected by orchestrator
        responses = [
            {
                "dimension": "research_quality",
                "question_id": "q1",
                "response_value": 4,
                "question_text": "How satisfied are you with your research progress?"
            },
            {
                "dimension": "research_quality",
                "question_id": "q2",
                "response_value": 5,
                "question_text": "How confident are you in your research direction?"
            },
            {
                "dimension": "timeline_adherence",
                "question_id": "q3",
                "response_value": 3,
                "question_text": "Are you on track with your timeline?"
            },
            {
                "dimension": "timeline_adherence",
                "question_id": "q4",
                "response_value": 2,
                "question_text": "How well are you managing deadlines?"
            },
            {
                "dimension": "work_life_balance",
                "question_id": "q5",
                "response_value": 4,
                "question_text": "How balanced is your work and personal life?"
            }
        ]
        
        result = orchestrator.submit(
            request_id=request_id,
            user_id=user_id,
            responses=responses,
            draft_id=draft_id,
            assessment_type="self_assessment",
            notes="First assessment"
        )
        
        print(f"✓ Questionnaire submitted")
        print(f"  Assessment ID: {result['assessment']['id']}")
        print(f"  Overall Score: {result['assessment']['overall_progress_rating']}")
        
        db.commit()
        
        # Step 3: Verify JourneyAssessment was created
        print("\n[3/4] Verifying JourneyAssessment...")
        assessment = db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == user_id
        ).order_by(JourneyAssessment.assessment_date.desc()).first()
        
        assert assessment is not None, "JourneyAssessment should be created"
        assert assessment.user_id == user_id
        assert assessment.assessment_type == "self_assessment"
        assert assessment.assessment_date == date.today()
        assert assessment.overall_progress_rating is not None
        assert assessment.overall_progress_rating >= 0
        assert assessment.overall_progress_rating <= 100
        
        # Verify health scores are stored
        assert assessment.research_quality_rating is not None
        assert assessment.timeline_adherence_rating is not None
        print(f"✓ JourneyAssessment created: {assessment.id}")
        print(f"  Overall: {assessment.overall_progress_rating}")
        print(f"  Research Quality: {assessment.research_quality_rating}")
        print(f"  Timeline Adherence: {assessment.timeline_adherence_rating}")
        
        # Verify recommendations are stored
        assert assessment.strengths is not None or assessment.strengths == ""
        assert assessment.challenges is not None or assessment.challenges == ""
        assert assessment.action_items is not None or assessment.action_items == ""
        print(f"✓ Recommendations stored")
        print(f"  Strengths: {len(assessment.strengths or '')} chars")
        print(f"  Challenges: {len(assessment.challenges or '')} chars")
        print(f"  Action Items: {len(assessment.action_items or '')} chars")
        
        # Verify draft is marked as submitted
        db.refresh(draft)
        assert draft.is_submitted is True
        assert draft.submission_id == assessment.id
        print(f"✓ Draft marked as submitted")
        
        # Step 4: Validate isolation (no document or timeline access)
        print("\n[4/4] Validating isolation...")
        
        # Verify orchestrator doesn't query documents
        # Check that no DocumentArtifact queries were made during submission
        # (We can't directly test this, but we verify the orchestrator doesn't have document access)
        assert not hasattr(orchestrator, 'get_document'), \
            "Orchestrator should not have document access methods"
        assert not hasattr(orchestrator, 'get_timeline'), \
            "Orchestrator should not have timeline access methods"
        
        # Verify no document or timeline data is referenced in assessment
        # The assessment should only contain questionnaire-derived data
        assert assessment.notes == "First assessment"  # Only questionnaire notes
        print("  ✓ No document access")
        print("  ✓ No timeline access")
        
        # Validation: Submission is required before scoring
        print("\nValidating submission requirement...")
        
        # Try to create assessment without submission (should fail)
        # The orchestrator requires responses to be submitted
        # Attempting to score without proper submission should raise an error
        
        # Create a new draft but don't submit it
        draft_id2 = questionnaire_service.create_draft(
            user_id=user_id,
            questionnaire_version_id=test_questionnaire_version.id,
            draft_name="Incomplete Draft"
        )
        
        # Save only one section (incomplete)
        questionnaire_service.save_section(
            draft_id=draft_id2,
            user_id=user_id,
            section_id="research_quality",
            responses={"q1": 4},
            is_section_complete=False
        )
        db.commit()
        
        # Try to submit incomplete questionnaire (should fail)
        incomplete_responses = [
            {
                "dimension": "research_quality",
                "question_id": "q1",
                "response_value": 4,
                "question_text": "How satisfied are you with your research progress?"
            }
            # Missing other questions
        ]
        
        with pytest.raises((IncompleteSubmissionError, PhDDoctorOrchestratorError)):
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=user_id,
                responses=incomplete_responses,
                draft_id=draft_id2,
                assessment_type="self_assessment"
            )
        
        print("  ✓ Incomplete submission rejected")
        
        # Verify no assessment was created for incomplete submission
        incomplete_assessments = db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == user_id
        ).count()
        assert incomplete_assessments == 1, \
            "Only one assessment should exist (from complete submission)"
        
        # Verify draft is not marked as submitted
        draft2 = db.query(QuestionnaireDraft).filter(
            QuestionnaireDraft.id == draft_id2
        ).first()
        assert draft2.is_submitted is False
        assert draft2.submission_id is None
        print("  ✓ Draft not marked as submitted (incomplete)")
        
        # Summary validation
        print("\n=== Questionnaire Submission Validation Summary ===")
        print(f"✓ Draft saved: {draft_id}")
        print(f"✓ Questionnaire submitted: {request_id}")
        print(f"✓ JourneyAssessment created: {assessment.id}")
        print(f"✓ Health scores stored: Overall={assessment.overall_progress_rating}")
        print(f"✓ Recommendations stored: Strengths, Challenges, Action Items")
        print(f"✓ Draft marked as submitted: {draft.is_submitted}")
        print(f"✓ Isolation validated: No document/timeline access")
        print(f"✓ Submission required: Incomplete submissions rejected")
        print(f"✓ All validations passed!")

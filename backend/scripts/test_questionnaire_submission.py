#!/usr/bin/env python3
"""
Standalone script to test questionnaire submission: Draft → Submission → JourneyAssessment.

Usage:
    python backend/scripts/test_questionnaire_submission.py

Note: This script requires PostgreSQL. Set DATABASE_URL environment variable:
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    python backend/scripts/test_questionnaire_submission.py

This script:
1. Saves questionnaire draft
2. Submits questionnaire
3. Generates JourneyAssessment
4. Stores health scores and recommendations

Validates:
- No document or timeline access (isolation)
- Submission is required before scoring
"""
import sys
import os
from datetime import date
from uuid import uuid4

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost/dbname")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.questionnaire_draft import (
    QuestionnaireDraft,
    QuestionnaireVersion
)
from app.models.journey_assessment import JourneyAssessment
from app.services.questionnaire_draft_service import (
    QuestionnaireDraftService,
    QuestionnaireDraftError
)
from app.orchestrators.phd_doctor_orchestrator import (
    PhDDoctorOrchestrator,
    PhDDoctorOrchestratorError,
    IncompleteSubmissionError
)


def create_test_database():
    """Create a test database (PostgreSQL required)."""
    # Use DATABASE_URL from environment, or default to PostgreSQL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or database_url == "postgresql://user:password@localhost/dbname":
        print("ERROR: DATABASE_URL environment variable not set or using default.")
        print("This script requires PostgreSQL. Set DATABASE_URL to a PostgreSQL connection string.")
        print("Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'")
        sys.exit(1)
    
    if not database_url.startswith("postgresql"):
        print("WARNING: This script is designed for PostgreSQL. SQLite may not work due to JSONB/ARRAY types.")
        print("Proceeding anyway...")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_test_user(db):
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


def create_test_questionnaire_version(db):
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


def main():
    """Run the questionnaire submission test."""
    print("=" * 60)
    print("Questionnaire Submission Integration Test")
    print("=" * 60)
    
    # Setup
    db = create_test_database()
    
    try:
        # Create test user
        print("\n[1/5] Creating test user...")
        user = create_test_user(db)
        user_id = user.id
        print(f"✓ User created: {user_id} ({user.email})")
        
        # Create questionnaire version
        print("\n[2/5] Creating questionnaire version...")
        version = create_test_questionnaire_version(db)
        print(f"✓ Questionnaire version created: {version.version_number}")
        
        # Save questionnaire draft
        print("\n[3/5] Saving questionnaire draft...")
        questionnaire_service = QuestionnaireDraftService(db)
        draft_id = questionnaire_service.create_draft(
            user_id=user_id,
            questionnaire_version_id=version.id,
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
        print(f"  ✓ No assessment exists before submission")
        
        # Submit questionnaire
        print("\n[4/5] Submitting questionnaire...")
        orchestrator = PhDDoctorOrchestrator(db, user_id)
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
        
        # Verify JourneyAssessment
        print("\n[5/5] Verifying JourneyAssessment...")
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
        
        # Validations
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        # Validation 1: No document or timeline access
        assert not hasattr(orchestrator, 'get_document'), \
            "Orchestrator should not have document access methods"
        assert not hasattr(orchestrator, 'get_timeline'), \
            "Orchestrator should not have timeline access methods"
        print("✓ Validation 1: No document or timeline access (isolation)")
        
        # Validation 2: Submission is required before scoring
        # Try to submit incomplete questionnaire (should fail)
        draft_id2 = questionnaire_service.create_draft(
            user_id=user_id,
            questionnaire_version_id=version.id,
            draft_name="Incomplete Draft"
        )
        
        questionnaire_service.save_section(
            draft_id=draft_id2,
            user_id=user_id,
            section_id="research_quality",
            responses={"q1": 4},
            is_section_complete=False
        )
        db.commit()
        
        incomplete_responses = [
            {
                "dimension": "research_quality",
                "question_id": "q1",
                "response_value": 4,
                "question_text": "How satisfied are you with your research progress?"
            }
            # Missing other questions
        ]
        
        try:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=user_id,
                responses=incomplete_responses,
                draft_id=draft_id2,
                assessment_type="self_assessment"
            )
            assert False, "Should have raised an error for incomplete submission"
        except (IncompleteSubmissionError, PhDDoctorOrchestratorError):
            print("✓ Validation 2: Incomplete submission rejected")
        
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
        print("✓ Validation 3: Draft not marked as submitted (incomplete)")
        
        print("\n" + "=" * 60)
        print("✓ ALL VALIDATIONS PASSED!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Draft ID: {draft_id}")
        print(f"  - Assessment ID: {assessment.id}")
        print(f"  - Overall Score: {assessment.overall_progress_rating}")
        print(f"  - Research Quality: {assessment.research_quality_rating}")
        print(f"  - Timeline Adherence: {assessment.timeline_adherence_rating}")
        print(f"  - Draft submitted: {draft.is_submitted}")
        print(f"  - Isolation validated: No document/timeline access")
        print(f"  - Submission required: Incomplete submissions rejected")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

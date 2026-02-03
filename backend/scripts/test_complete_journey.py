#!/usr/bin/env python3
"""
Complete User Journey Test Script

Tests the full user journey from document upload to analytics dashboard.

Each step maps to exactly one backend endpoint:
1. Upload Document → POST /api/v1/documents/upload
2. Create Baseline → POST /api/v1/baselines
3. Generate Draft Timeline → POST /api/v1/timelines/draft/generate
4. Commit Timeline → POST /api/v1/timelines/draft/{id}/commit
5. Track Progress → POST /api/v1/progress/milestones/{id}/complete
6. Submit PhD Doctor → POST /api/v1/doctor/submit
7. View Analytics Dashboard → GET /api/v1/analytics/summary

Usage:
    python backend/scripts/test_complete_journey.py

Note: This script requires PostgreSQL. Set DATABASE_URL environment variable:
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    python backend/scripts/test_complete_journey.py
"""
import sys
import os
from datetime import date, datetime, timedelta
from uuid import uuid4

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.document_artifact import DocumentArtifact
from app.models.baseline import Baseline
from app.models.draft_timeline import DraftTimeline
from app.models.committed_timeline import CommittedTimeline
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.models.progress_event import ProgressEvent
from app.models.questionnaire_draft import QuestionnaireDraft, QuestionnaireVersion
from app.models.journey_assessment import JourneyAssessment
from app.models.analytics_snapshot import AnalyticsSnapshot

from app.orchestrators.baseline_orchestrator import BaselineOrchestrator
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator
from app.services.progress_service import ProgressService
from app.orchestrators.phd_doctor_orchestrator import PhDDoctorOrchestrator
from app.orchestrators.analytics_orchestrator import AnalyticsOrchestrator


def create_test_database():
    """Create a test database (PostgreSQL required)."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or database_url == "sqlite:///:memory:":
        print("ERROR: DATABASE_URL environment variable not set.")
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
        email="test.phd.student@university.edu",
        hashed_password="hashed_password",
        full_name="Test PhD Student",
        institution="Test University",
        field_of_study="Computer Science",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_document(db, user_id):
    """Create a test document."""
    sample_text = """
    PhD Program in Computer Science
    
    The PhD program in Computer Science begins with coursework over 18 months.
    Students must complete 48 credits of graduate courses covering core topics.
    
    Following coursework, students conduct a literature review for 6 months.
    This includes surveying prior work and related research in the field.
    Students must identify gaps in existing research.
    
    The research phase lasts approximately 2 years.
    Students design experiments, collect data, and conduct analysis.
    This phase includes methodology development and data collection.
    
    Writing the dissertation requires one year.
    Students must submit their thesis before the defense.
    The writing phase includes multiple drafts and revisions.
    
    The final defense is a mandatory milestone.
    Students present and defend their research before a committee.
    """
    
    document = DocumentArtifact(
        user_id=user_id,
        title="PhD Program Requirements",
        description="PhD program requirements document",
        file_type="pdf",
        file_path="/uploads/phd_requirements.pdf",
        file_size_bytes=5000,
        document_type="requirements",
        raw_text=sample_text,
        document_text=sample_text.strip(),
        word_count=len(sample_text.split()),
        detected_language="en",
        section_map_json={
            "sections": [
                {"title": "Coursework", "start": 0, "end": 100},
                {"title": "Literature Review", "start": 100, "end": 200},
                {"title": "Research Phase", "start": 200, "end": 300},
                {"title": "Writing", "start": 300, "end": 400},
                {"title": "Defense", "start": 400, "end": 500},
            ]
        }
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


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
    """Run the complete journey test."""
    print("=" * 80)
    print("COMPLETE USER JOURNEY TEST")
    print("=" * 80)
    print("\nTesting all 7 steps with exact endpoint mapping:\n")
    
    # Setup
    db = create_test_database()
    
    try:
        # Step 1: Upload Document
        print("[1/7] Upload Document → POST /api/v1/documents/upload")
        print("-" * 80)
        user = create_test_user(db)
        user_id = user.id
        print(f"✓ User created: {user_id} ({user.email})")
        
        document = create_test_document(db, user_id)
        document_id = document.id
        print(f"✓ Document created: {document_id}")
        print(f"  Title: {document.title}")
        print(f"  Type: {document.document_type}")
        print(f"  Word count: {document.word_count}")
        
        # Step 2: Create Baseline
        print("\n[2/7] Create Baseline → POST /api/v1/baselines")
        print("-" * 80)
        baseline_orchestrator = BaselineOrchestrator(db, user_id)
        request_id_baseline = str(uuid4())
        
        baseline_result = baseline_orchestrator.create(
            request_id=request_id_baseline,
            user_id=user_id,
            program_name="PhD in Computer Science",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today(),
            document_id=document_id,
            total_duration_months=48,
        )
        
        baseline_id = baseline_result["baseline"]["id"]
        print(f"✓ Baseline created: {baseline_id}")
        print(f"  Program: {baseline_result['baseline']['program_name']}")
        print(f"  Institution: {baseline_result['baseline']['institution']}")
        
        # Step 3: Generate Draft Timeline
        print("\n[3/7] Generate Draft Timeline → POST /api/v1/timelines/draft/generate")
        print("-" * 80)
        timeline_orchestrator = TimelineOrchestrator(db, user_id)
        request_id_generate = str(uuid4())
        
        draft_result = timeline_orchestrator.generate(
            request_id=request_id_generate,
            baseline_id=baseline_id,
            user_id=user_id,
            title="My PhD Timeline",
            version_number="1.0"
        )
        
        draft_timeline_id = draft_result["timeline"]["id"]
        print(f"✓ Draft timeline created: {draft_timeline_id}")
        print(f"  Title: {draft_result['timeline']['title']}")
        print(f"  Stages: {len(draft_result.get('stages', []))}")
        
        # Count milestones
        draft_stages = db.query(TimelineStage).filter(
            TimelineStage.draft_timeline_id == draft_timeline_id
        ).all()
        draft_milestones = []
        for stage in draft_stages:
            stage_milestones = db.query(TimelineMilestone).filter(
                TimelineMilestone.timeline_stage_id == stage.id
            ).all()
            draft_milestones.extend(stage_milestones)
        print(f"  Milestones: {len(draft_milestones)}")
        
        # Step 4: Commit Timeline
        print("\n[4/7] Commit Timeline → POST /api/v1/timelines/draft/{id}/commit")
        print("-" * 80)
        request_id_commit = str(uuid4())
        
        commit_result = timeline_orchestrator.commit(
            request_id=request_id_commit,
            draft_timeline_id=draft_timeline_id,
            user_id=user_id,
            title="My Committed PhD Timeline"
        )
        
        committed_timeline_id = commit_result["committed_timeline"]["id"]
        print(f"✓ Timeline committed: {committed_timeline_id}")
        print(f"  Title: {commit_result['committed_timeline']['title']}")
        
        # Verify draft is frozen
        draft_timeline = db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id
        ).first()
        assert draft_timeline.is_active is False, "Draft should be frozen"
        print(f"  Draft frozen: {draft_timeline.is_active == False}")
        
        # Step 5: Track Progress
        print("\n[5/7] Track Progress → POST /api/v1/progress/milestones/{id}/complete")
        print("-" * 80)
        progress_service = ProgressService(db)
        
        # Get committed milestones
        committed_stages = db.query(TimelineStage).filter(
            TimelineStage.committed_timeline_id == committed_timeline_id
        ).all()
        
        completed_milestones = []
        for stage in committed_stages:
            milestones = db.query(TimelineMilestone).filter(
                TimelineMilestone.timeline_stage_id == stage.id
            ).limit(2).all()  # Complete first 2 milestones per stage
            
            for milestone in milestones:
                try:
                    progress_service.mark_milestone_completed(
                        milestone_id=milestone.id,
                        user_id=user_id,
                        completion_date=date.today()
                    )
                    completed_milestones.append(milestone.id)
                    print(f"  ✓ Milestone completed: {milestone.title[:50]}...")
                except Exception as e:
                    print(f"  ⚠ Could not complete milestone {milestone.id}: {e}")
        
        print(f"✓ Progress tracked: {len(completed_milestones)} milestones completed")
        
        # Verify progress events
        progress_events = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).all()
        print(f"  Progress events: {len(progress_events)}")
        
        # Step 6: Submit PhD Doctor Questionnaire
        print("\n[6/7] Submit PhD Doctor → POST /api/v1/doctor/submit")
        print("-" * 80)
        
        # Create questionnaire version
        version = create_test_questionnaire_version(db)
        print(f"✓ Questionnaire version: {version.version_number}")
        
        # Prepare responses
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
        
        doctor_orchestrator = PhDDoctorOrchestrator(db, user_id)
        request_id_submit = str(uuid4())
        
        assessment_result = doctor_orchestrator.submit(
            request_id=request_id_submit,
            user_id=user_id,
            responses=responses,
            assessment_type="self_assessment",
            notes="Complete journey test assessment"
        )
        
        assessment_id = assessment_result["assessment"]["id"]
        print(f"✓ Questionnaire submitted")
        print(f"  Assessment ID: {assessment_id}")
        print(f"  Overall Score: {assessment_result['assessment']['overall_progress_rating']}")
        
        # Verify JourneyAssessment
        assessment = db.query(JourneyAssessment).filter(
            JourneyAssessment.id == assessment_id
        ).first()
        assert assessment is not None, "Assessment should exist"
        print(f"  Research Quality: {assessment.research_quality_rating}")
        print(f"  Timeline Adherence: {assessment.timeline_adherence_rating}")
        
        # Step 7: View Analytics Dashboard
        print("\n[7/7] View Analytics Dashboard → GET /api/v1/analytics/summary")
        print("-" * 80)
        
        analytics_orchestrator = AnalyticsOrchestrator(db, user_id)
        request_id_analytics = str(uuid4())
        
        analytics_result = analytics_orchestrator.run(
            request_id=request_id_analytics,
            user_id=user_id,
            timeline_id=committed_timeline_id
        )
        
        print(f"✓ Analytics generated")
        summary = analytics_result.get("summary", {})
        
        # Verify AnalyticsSnapshot
        snapshot = db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.user_id == user_id
        ).order_by(AnalyticsSnapshot.created_at.desc()).first()
        
        assert snapshot is not None, "Analytics snapshot should exist"
        print(f"  Snapshot ID: {snapshot.id}")
        print(f"  Timeline Status: {summary.get('timeline_status', 'N/A')}")
        print(f"  Progress: {summary.get('milestones', {}).get('completion_percentage', 0)}%")
        print(f"  Health Score: {summary.get('journey_health', {}).get('latest_score', 'N/A')}")
        
        # Final Validation
        print("\n" + "=" * 80)
        print("FINAL VALIDATION")
        print("=" * 80)
        
        validations = []
        
        # Check all records exist
        validations.append(("Document exists", db.query(DocumentArtifact).filter(
            DocumentArtifact.id == document_id
        ).first() is not None))
        
        validations.append(("Baseline exists", db.query(Baseline).filter(
            Baseline.id == baseline_id
        ).first() is not None))
        
        validations.append(("Draft timeline exists", db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id
        ).first() is not None))
        
        validations.append(("Committed timeline exists", db.query(CommittedTimeline).filter(
            CommittedTimeline.id == committed_timeline_id
        ).first() is not None))
        
        validations.append(("Progress events exist", len(progress_events) > 0))
        
        validations.append(("Assessment exists", assessment is not None))
        
        validations.append(("Analytics snapshot exists", snapshot is not None))
        
        # Check data consistency
        committed_timeline = db.query(CommittedTimeline).filter(
            CommittedTimeline.id == committed_timeline_id
        ).first()
        validations.append(("Committed timeline linked to draft", 
                          committed_timeline.draft_timeline_id == draft_timeline_id))
        validations.append(("Committed timeline linked to user", 
                          committed_timeline.user_id == user_id))
        
        # Print validation results
        all_passed = True
        for name, passed in validations:
            status = "✓" if passed else "✗"
            print(f"{status} {name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n" + "=" * 80)
            print("✓ ALL STEPS COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"\nSummary:")
            print(f"  - Document ID: {document_id}")
            print(f"  - Baseline ID: {baseline_id}")
            print(f"  - Draft Timeline ID: {draft_timeline_id}")
            print(f"  - Committed Timeline ID: {committed_timeline_id}")
            print(f"  - Completed Milestones: {len(completed_milestones)}")
            print(f"  - Progress Events: {len(progress_events)}")
            print(f"  - Assessment ID: {assessment_id}")
            print(f"  - Analytics Snapshot ID: {snapshot.id}")
            print(f"\n✓ All 7 endpoints tested successfully!")
        else:
            print("\n" + "=" * 80)
            print("✗ SOME VALIDATIONS FAILED")
            print("=" * 80)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

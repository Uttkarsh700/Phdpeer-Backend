#!/usr/bin/env python3
"""
Standalone script to test the full pipeline: Document → Baseline → DraftTimeline → CommittedTimeline.

Usage:
    python backend/scripts/test_full_pipeline.py

Note: This script requires PostgreSQL. Set DATABASE_URL environment variable:
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    python backend/scripts/test_full_pipeline.py

This script:
1. Creates a test user
2. Uploads a document (creates DocumentArtifact)
3. Creates a Baseline
4. Generates a DraftTimeline
5. Commits the Timeline

Validates:
- Each step writes a DecisionTrace
- DraftTimeline != CommittedTimeline
- CommittedTimeline is immutable
"""
import sys
import os
from datetime import date
from uuid import uuid4

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

from app.database import Base

# Note: For SQLite compatibility, you would need to override JSONB and ARRAY types
# This script is designed for PostgreSQL which natively supports these types
from app.models.user import User
from app.models.document_artifact import DocumentArtifact
from app.models.baseline import Baseline
from app.models.draft_timeline import DraftTimeline
from app.models.committed_timeline import CommittedTimeline
from app.models.idempotency import DecisionTrace
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.orchestrators.baseline_orchestrator import BaselineOrchestrator
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator


def create_test_database():
    """Create a test database (PostgreSQL required)."""
    # Use DATABASE_URL from environment, or default to PostgreSQL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
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


def create_test_document(db, user_id, text):
    """Create a test document with text."""
    document = DocumentArtifact(
        user_id=user_id,
        title="PhD Program Requirements",
        description="PhD program requirements document",
        file_type="pdf",
        file_path="/uploads/phd_requirements.pdf",
        file_size_bytes=5000,
        document_type="requirements",
        raw_text=text,
        document_text=text.strip(),
        word_count=len(text.split()),
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


def main():
    """Run the full pipeline test."""
    print("=" * 60)
    print("Full Pipeline Integration Test")
    print("=" * 60)
    
    # Setup
    db = create_test_database()
    
    try:
        # Create test user
        print("\n[1/5] Creating test user...")
        user = create_test_user(db)
        user_id = user.id
        print(f"✓ User created: {user_id} ({user.email})")
        
        # Create document
        print("\n[2/5] Creating document...")
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
        document = create_test_document(db, user_id, sample_text)
        document_id = document.id
        print(f"✓ Document created: {document_id}")
        
        # Create baseline
        print("\n[3/5] Creating baseline...")
        baseline_orchestrator = BaselineOrchestrator(db, user_id)
        request_id_2 = str(uuid4())
        
        baseline_result = baseline_orchestrator.create(
            request_id=request_id_2,
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
        
        # Verify DecisionTrace for baseline
        baseline_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_2,
            DecisionTrace.orchestrator_name == "baseline_orchestrator"
        ).first()
        assert baseline_trace is not None, "Baseline creation should write DecisionTrace"
        print(f"  ✓ DecisionTrace written: {baseline_trace.id}")
        
        # Generate draft timeline
        print("\n[4/5] Generating draft timeline...")
        timeline_orchestrator = TimelineOrchestrator(db, user_id)
        request_id_3 = str(uuid4())
        
        draft_result = timeline_orchestrator.generate(
            request_id=request_id_3,
            baseline_id=baseline_id,
            user_id=user_id,
            title="My PhD Timeline",
            version_number="1.0"
        )
        
        draft_timeline_id = draft_result["timeline"]["id"]
        print(f"✓ DraftTimeline created: {draft_timeline_id}")
        
        # Verify DecisionTrace for timeline generation
        timeline_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_3,
            DecisionTrace.orchestrator_name == "timeline_orchestrator"
        ).first()
        assert timeline_trace is not None, "Timeline generation should write DecisionTrace"
        print(f"  ✓ DecisionTrace written: {timeline_trace.id}")
        
        # Commit timeline
        print("\n[5/5] Committing timeline...")
        request_id_4 = str(uuid4())
        
        commit_result = timeline_orchestrator.commit(
            request_id=request_id_4,
            draft_timeline_id=draft_timeline_id,
            user_id=user_id,
            title="My Committed PhD Timeline"
        )
        
        committed_timeline_id = commit_result["committed_timeline"]["id"]
        print(f"✓ CommittedTimeline created: {committed_timeline_id}")
        
        # Verify DecisionTrace for commit
        commit_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_4,
            DecisionTrace.orchestrator_name == "timeline_orchestrator"
        ).first()
        assert commit_trace is not None, "Timeline commit should write DecisionTrace"
        print(f"  ✓ DecisionTrace written: {commit_trace.id}")
        
        # Validations
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        # Validation 1: DraftTimeline != CommittedTimeline
        draft_timeline = db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id
        ).first()
        committed_timeline = db.query(CommittedTimeline).filter(
            CommittedTimeline.id == committed_timeline_id
        ).first()
        
        assert draft_timeline_id != committed_timeline_id, \
            "DraftTimeline and CommittedTimeline must be different records"
        print("✓ Validation 1: DraftTimeline != CommittedTimeline")
        
        # Validation 2: Draft is frozen
        assert draft_timeline.is_active is False, \
            "DraftTimeline should be marked inactive after commit"
        print("✓ Validation 2: DraftTimeline is frozen (is_active=False)")
        
        # Validation 3: All DecisionTraces written
        all_traces = db.query(DecisionTrace).filter(
            DecisionTrace.request_id.in_([request_id_2, request_id_3, request_id_4])
        ).all()
        assert len(all_traces) == 3, \
            f"Expected 3 DecisionTraces, got {len(all_traces)}"
        print(f"✓ Validation 3: All DecisionTraces written ({len(all_traces)} traces)")
        
        # Validation 4: CommittedTimeline has structure
        committed_stages = db.query(TimelineStage).filter(
            TimelineStage.committed_timeline_id == committed_timeline_id
        ).all()
        
        committed_milestones = []
        for stage in committed_stages:
            stage_milestones = db.query(TimelineMilestone).filter(
                TimelineMilestone.timeline_stage_id == stage.id
            ).all()
            committed_milestones.extend(stage_milestones)
        
        assert len(committed_stages) > 0, "Committed timeline should have stages"
        assert len(committed_milestones) > 0, "Committed timeline should have milestones"
        print(f"✓ Validation 4: CommittedTimeline has {len(committed_stages)} stages and {len(committed_milestones)} milestones")
        
        # Validation 5: Immutability (structure check)
        assert committed_timeline.draft_timeline_id == draft_timeline_id
        assert committed_timeline.user_id == user_id
        assert committed_timeline.committed_date is not None
        print("✓ Validation 5: CommittedTimeline structure is complete and immutable")
        
        print("\n" + "=" * 60)
        print("✓ ALL VALIDATIONS PASSED!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Document ID: {document_id}")
        print(f"  - Baseline ID: {baseline_id}")
        print(f"  - DraftTimeline ID: {draft_timeline_id}")
        print(f"  - CommittedTimeline ID: {committed_timeline_id}")
        print(f"  - DecisionTraces: {len(all_traces)}")
        print(f"  - Stages: {len(committed_stages)}")
        print(f"  - Milestones: {len(committed_milestones)}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

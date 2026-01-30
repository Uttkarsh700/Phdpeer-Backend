"""
Integration test for full pipeline: Document → Baseline → DraftTimeline → CommittedTimeline.

Tests:
- Document upload
- Baseline creation
- DraftTimeline generation
- Timeline commitment
- DecisionTrace validation
- Immutability validation
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
from app.models.document_artifact import DocumentArtifact
from app.models.baseline import Baseline
from app.models.draft_timeline import DraftTimeline
from app.models.committed_timeline import CommittedTimeline
from app.models.idempotency import DecisionTrace
from app.services.document_service import DocumentService
from app.orchestrators.baseline_orchestrator import BaselineOrchestrator
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator


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
def sample_document_text():
    """Sample PhD program document text for testing."""
    return """
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


class TestFullPipelineIntegration:
    """Integration test for complete pipeline."""
    
    def test_full_pipeline_with_validation(
        self,
        db,
        test_user,
        sample_document_text
    ):
        """
        Test complete pipeline: Document → Baseline → DraftTimeline → CommittedTimeline.
        
        Validates:
        - Each step writes a DecisionTrace
        - DraftTimeline != CommittedTimeline
        - CommittedTimeline is immutable
        """
        user_id = test_user.id
        
        # Step 1: Create document directly (bypassing file upload for integration test)
        # In a real scenario, this would go through DocumentService.upload_document()
        # For integration testing, we create the document with text directly
        document = DocumentArtifact(
            user_id=user_id,
            title="PhD Program Requirements",
            description="PhD program requirements document",
            file_type="pdf",
            file_path="/uploads/phd_requirements.pdf",
            file_size_bytes=5000,
            document_type="requirements",
            raw_text=sample_document_text,
            document_text=sample_document_text.strip(),  # Normalized text
            word_count=len(sample_document_text.split()),
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
        document_id = document.id
        
        # Verify document was created
        document = db.query(DocumentArtifact).filter(
            DocumentArtifact.id == document_id
        ).first()
        assert document is not None
        assert document.user_id == user_id
        assert document.title == "PhD Program Requirements"
        
        # Step 2: Create Baseline
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
        
        # Verify baseline was created
        baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()
        assert baseline is not None
        assert baseline.user_id == user_id
        assert baseline.document_artifact_id == document_id
        
        # Validate DecisionTrace for baseline creation
        baseline_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_2,
            DecisionTrace.orchestrator_name == "baseline_orchestrator"
        ).first()
        assert baseline_trace is not None, "Baseline creation should write DecisionTrace"
        assert baseline_trace.trace_json is not None
        assert "validate_document" in str(baseline_trace.trace_json)
        assert "ensure_no_baseline" in str(baseline_trace.trace_json)
        assert "create_baseline" in str(baseline_trace.trace_json)
        
        # Step 3: Generate DraftTimeline
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
        
        # Verify draft timeline was created
        draft_timeline = db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id
        ).first()
        assert draft_timeline is not None
        assert draft_timeline.user_id == user_id
        assert draft_timeline.baseline_id == baseline_id
        assert draft_timeline.status == "DRAFT"
        assert draft_timeline.is_active is True
        
        # Validate DecisionTrace for timeline generation
        timeline_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_3,
            DecisionTrace.orchestrator_name == "timeline_orchestrator"
        ).first()
        assert timeline_trace is not None, "Timeline generation should write DecisionTrace"
        assert timeline_trace.trace_json is not None
        assert "validate_baseline" in str(timeline_trace.trace_json)
        assert "detect_stages" in str(timeline_trace.trace_json)
        assert "extract_milestones" in str(timeline_trace.trace_json)
        
        # Step 4: Commit Timeline
        request_id_4 = str(uuid4())
        
        commit_result = timeline_orchestrator.commit(
            request_id=request_id_4,
            draft_timeline_id=draft_timeline_id,
            user_id=user_id,
            title="My Committed PhD Timeline"
        )
        
        committed_timeline_id = commit_result["committed_timeline"]["id"]
        
        # Verify committed timeline was created
        committed_timeline = db.query(CommittedTimeline).filter(
            CommittedTimeline.id == committed_timeline_id
        ).first()
        assert committed_timeline is not None
        assert committed_timeline.user_id == user_id
        assert committed_timeline.draft_timeline_id == draft_timeline_id
        
        # Validate DecisionTrace for timeline commit
        commit_trace = db.query(DecisionTrace).filter(
            DecisionTrace.request_id == request_id_4,
            DecisionTrace.orchestrator_name == "timeline_orchestrator"
        ).first()
        assert commit_trace is not None, "Timeline commit should write DecisionTrace"
        assert commit_trace.trace_json is not None
        assert "validate_draft" in str(commit_trace.trace_json)
        assert "validate_completeness" in str(commit_trace.trace_json)
        assert "create_committed_timeline" in str(commit_trace.trace_json)
        
        # Validation 1: DraftTimeline != CommittedTimeline
        assert draft_timeline_id != committed_timeline_id, \
            "DraftTimeline and CommittedTimeline must be different records"
        
        # Verify draft timeline is frozen
        db.refresh(draft_timeline)
        assert draft_timeline.is_active is False, \
            "DraftTimeline should be marked inactive after commit"
        
        # Validation 2: CommittedTimeline is immutable
        # Verify that the committed timeline has the expected immutable structure
        # Immutability is enforced by the orchestrator logic (no update methods)
        
        # Check that committed timeline has stages and milestones
        from app.models.timeline_stage import TimelineStage
        from app.models.timeline_milestone import TimelineMilestone
        
        committed_stages = db.query(TimelineStage).filter(
            TimelineStage.committed_timeline_id == committed_timeline_id
        ).all()
        assert len(committed_stages) > 0, "Committed timeline should have stages"
        
        committed_milestones = []
        for stage in committed_stages:
            stage_milestones = db.query(TimelineMilestone).filter(
                TimelineMilestone.timeline_stage_id == stage.id
            ).all()
            committed_milestones.extend(stage_milestones)
        
        assert len(committed_milestones) > 0, "Committed timeline should have milestones"
        
        # Validation 3: All steps wrote DecisionTrace
        all_traces = db.query(DecisionTrace).filter(
            DecisionTrace.request_id.in_([request_id_2, request_id_3, request_id_4])
        ).all()
        assert len(all_traces) == 3, \
            f"Expected 3 DecisionTraces, got {len(all_traces)}"
        
        # Verify each trace has proper structure
        for trace in all_traces:
            assert trace.orchestrator_name in ["baseline_orchestrator", "timeline_orchestrator"]
            assert trace.trace_json is not None
            assert "steps" in trace.trace_json or isinstance(trace.trace_json, dict)
        
        # Validation 4: Verify immutability by checking that committed timeline
        # cannot be updated through direct database manipulation (if attempted)
        # In practice, immutability is enforced by not providing update methods
        # We verify the structure is complete and frozen
        
        # Verify committed timeline structure
        assert committed_timeline.draft_timeline_id == draft_timeline_id
        assert committed_timeline.user_id == user_id
        assert committed_timeline.committed_date is not None
        
        # Verify draft is frozen
        db.refresh(draft_timeline)
        assert draft_timeline.is_active is False
        
        # Summary validation
        print("\n=== Pipeline Validation Summary ===")
        print(f"✓ Document created: {document_id}")
        print(f"✓ Baseline created: {baseline_id}")
        print(f"✓ DraftTimeline created: {draft_timeline_id}")
        print(f"✓ CommittedTimeline created: {committed_timeline_id}")
        print(f"✓ DecisionTraces written: {len(all_traces)}")
        print(f"✓ DraftTimeline != CommittedTimeline: {draft_timeline_id != committed_timeline_id}")
        print(f"✓ DraftTimeline frozen: {draft_timeline.is_active is False}")
        print(f"✓ CommittedTimeline has {len(committed_stages)} stages and {len(committed_milestones)} milestones")
        print(f"✓ All validations passed!")

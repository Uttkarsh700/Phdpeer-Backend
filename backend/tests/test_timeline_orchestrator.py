"""Tests for TimelineOrchestrator."""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.document_artifact import DocumentArtifact
from app.models.baseline import Baseline
from app.orchestrators.timeline_orchestrator import (
    TimelineOrchestrator,
    TimelineOrchestratorError,
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
def test_document_with_text(db, test_user):
    """Create a test document with PhD program text."""
    phd_text = """
    The PhD program in Computer Science begins with coursework over 18 months.
    Students must complete 48 credits of graduate courses.
    
    Following coursework, students conduct a literature review for 6 months.
    This includes surveying prior work and related research in the field.
    
    The research phase lasts approximately 2 years.
    Students design experiments, collect data, and conduct analysis.
    
    Writing the dissertation requires one year.
    Students must submit their thesis before the defense.
    
    The final defense is a mandatory milestone.
    Students present and defend their research before a committee.
    """
    
    document = DocumentArtifact(
        user_id=test_user.id,
        title="PhD Program Requirements",
        file_type="pdf",
        file_path="/uploads/phd_requirements.pdf",
        file_size_bytes=5000,
        metadata=phd_text,  # Store extracted text here
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@pytest.fixture
def test_baseline(db, test_user, test_document_with_text):
    """Create a test baseline."""
    baseline = Baseline(
        user_id=test_user.id,
        document_artifact_id=test_document_with_text.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
        total_duration_months=48,
    )
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    return baseline


def test_create_draft_timeline_success(db, test_user, test_baseline):
    """Test creating a draft timeline successfully."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id,
        title="My PhD Timeline",
        description="Draft timeline for my PhD program"
    )
    
    assert draft_timeline_id is not None
    
    # Verify timeline was created
    draft_timeline = orchestrator.get_draft_timeline(draft_timeline_id)
    assert draft_timeline is not None
    assert draft_timeline.user_id == test_user.id
    assert draft_timeline.baseline_id == test_baseline.id
    assert draft_timeline.title == "My PhD Timeline"
    assert draft_timeline.is_active is True
    assert "DRAFT" in draft_timeline.notes


def test_create_draft_timeline_with_stages(db, test_user, test_baseline):
    """Test that stages are created."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    # Get timeline with details
    details = orchestrator.get_draft_timeline_with_details(draft_timeline_id)
    
    assert details is not None
    assert details["total_stages"] > 0
    assert len(details["stages"]) > 0
    
    # Verify stages have proper ordering
    stage_orders = [s["stage"].stage_order for s in details["stages"]]
    assert stage_orders == sorted(stage_orders)


def test_create_draft_timeline_with_milestones(db, test_user, test_baseline):
    """Test that milestones are created."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    # Get timeline with details
    details = orchestrator.get_draft_timeline_with_details(draft_timeline_id)
    
    assert details is not None
    assert details["total_milestones"] > 0
    
    # Check that milestones are assigned to stages
    stages_with_milestones = [
        s for s in details["stages"] if len(s["milestones"]) > 0
    ]
    assert len(stages_with_milestones) > 0


def test_create_draft_timeline_default_title(db, test_user, test_baseline):
    """Test default title generation."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    draft_timeline = orchestrator.get_draft_timeline(draft_timeline_id)
    
    # Should include program name in title
    assert test_baseline.program_name in draft_timeline.title


def test_create_draft_timeline_invalid_user(db, test_baseline):
    """Test with non-existent user."""
    orchestrator = TimelineOrchestrator(db)
    
    from uuid import uuid4
    
    with pytest.raises(TimelineOrchestratorError) as exc_info:
        orchestrator.create_draft_timeline(
            baseline_id=test_baseline.id,
            user_id=uuid4()
        )
    
    assert "User" in str(exc_info.value)
    assert "not found" in str(exc_info.value)


def test_create_draft_timeline_invalid_baseline(db, test_user):
    """Test with non-existent baseline."""
    orchestrator = TimelineOrchestrator(db)
    
    from uuid import uuid4
    
    with pytest.raises(TimelineOrchestratorError) as exc_info:
        orchestrator.create_draft_timeline(
            baseline_id=uuid4(),
            user_id=test_user.id
        )
    
    assert "Baseline" in str(exc_info.value)


def test_create_draft_timeline_wrong_owner(db, test_user, test_baseline):
    """Test that users can't create timelines for others' baselines."""
    orchestrator = TimelineOrchestrator(db)
    
    # Create another user
    other_user = User(
        email="other@university.edu",
        hashed_password="hashed_password",
        full_name="John Smith",
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    with pytest.raises(TimelineOrchestratorError) as exc_info:
        orchestrator.create_draft_timeline(
            baseline_id=test_baseline.id,
            user_id=other_user.id
        )
    
    assert "does not belong to user" in str(exc_info.value)


def test_create_draft_timeline_no_document(db, test_user):
    """Test creating timeline without document."""
    orchestrator = TimelineOrchestrator(db)
    
    # Create baseline without document
    baseline = Baseline(
        user_id=test_user.id,
        program_name="PhD Program",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    
    with pytest.raises(TimelineOrchestratorError) as exc_info:
        orchestrator.create_draft_timeline(
            baseline_id=baseline.id,
            user_id=test_user.id
        )
    
    assert "No document text" in str(exc_info.value)


def test_get_user_draft_timelines(db, test_user, test_baseline):
    """Test getting user's draft timelines."""
    orchestrator = TimelineOrchestrator(db)
    
    # Create multiple timelines
    id1 = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id,
        title="Timeline 1"
    )
    
    id2 = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id,
        title="Timeline 2"
    )
    
    # Get all timelines
    timelines = orchestrator.get_user_draft_timelines(test_user.id)
    
    assert len(timelines) == 2
    assert id1 in [t.id for t in timelines]
    assert id2 in [t.id for t in timelines]


def test_get_user_draft_timelines_filtered(db, test_user, test_baseline):
    """Test filtered timeline retrieval."""
    orchestrator = TimelineOrchestrator(db)
    
    # Create timeline
    orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    # Filter by baseline
    timelines = orchestrator.get_user_draft_timelines(
        test_user.id,
        baseline_id=test_baseline.id
    )
    
    assert len(timelines) == 1
    assert timelines[0].baseline_id == test_baseline.id


def test_stage_durations_assigned(db, test_user, test_baseline):
    """Test that stages have durations assigned."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    details = orchestrator.get_draft_timeline_with_details(draft_timeline_id)
    
    # All stages should have durations
    for stage_info in details["stages"]:
        stage = stage_info["stage"]
        assert stage.duration_months is not None
        assert stage.duration_months > 0


def test_critical_milestones_marked(db, test_user, test_baseline):
    """Test that critical milestones are identified."""
    orchestrator = TimelineOrchestrator(db)
    
    draft_timeline_id = orchestrator.create_draft_timeline(
        baseline_id=test_baseline.id,
        user_id=test_user.id
    )
    
    details = orchestrator.get_draft_timeline_with_details(draft_timeline_id)
    
    # Collect all milestones
    all_milestones = []
    for stage_info in details["stages"]:
        all_milestones.extend(stage_info["milestones"])
    
    # Should have at least one critical milestone (defense)
    critical_milestones = [m for m in all_milestones if m.is_critical]
    assert len(critical_milestones) > 0

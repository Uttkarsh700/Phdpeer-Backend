"""Tests for ProgressService."""
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.baseline import Baseline
from app.models.committed_timeline import CommittedTimeline
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.services.progress_service import ProgressService, ProgressServiceError


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
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_timeline(db, test_user):
    """Create a test committed timeline with stages and milestones."""
    # Create baseline
    baseline = Baseline(
        user_id=test_user.id,
        program_name="PhD Program",
        institution="Test University",
        field_of_study="CS",
        start_date=date.today(),
    )
    db.add(baseline)
    db.flush()
    
    # Create committed timeline
    timeline = CommittedTimeline(
        user_id=test_user.id,
        baseline_id=baseline.id,
        title="Test Timeline",
        committed_date=date.today() - timedelta(days=30),
        target_completion_date=date.today() + timedelta(days=300),
    )
    db.add(timeline)
    db.flush()
    
    # Create stages
    stage1 = TimelineStage(
        committed_timeline_id=timeline.id,
        title="Stage 1",
        stage_order=1,
        status="in_progress",
    )
    stage2 = TimelineStage(
        committed_timeline_id=timeline.id,
        title="Stage 2",
        stage_order=2,
        status="not_started",
    )
    db.add_all([stage1, stage2])
    db.flush()
    
    # Create milestones
    milestone1 = TimelineMilestone(
        timeline_stage_id=stage1.id,
        title="Milestone 1",
        milestone_order=1,
        target_date=date.today() - timedelta(days=5),
        is_critical=True,
        is_completed=False,
    )
    milestone2 = TimelineMilestone(
        timeline_stage_id=stage1.id,
        title="Milestone 2",
        milestone_order=2,
        target_date=date.today() + timedelta(days=10),
        is_critical=False,
        is_completed=False,
    )
    milestone3 = TimelineMilestone(
        timeline_stage_id=stage2.id,
        title="Milestone 3",
        milestone_order=1,
        target_date=date.today() + timedelta(days=30),
        is_critical=False,
        is_completed=False,
    )
    db.add_all([milestone1, milestone2, milestone3])
    db.commit()
    
    return {
        "timeline": timeline,
        "stages": [stage1, stage2],
        "milestones": [milestone1, milestone2, milestone3],
    }


def test_mark_milestone_completed(db, test_user, test_timeline):
    """Test marking a milestone as completed."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][0]
    
    event_id = service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id,
        notes="Test completion"
    )
    
    assert event_id is not None
    
    # Verify milestone is marked completed
    db.refresh(milestone)
    assert milestone.is_completed is True
    assert milestone.actual_completion_date == date.today()


def test_mark_milestone_completed_with_date(db, test_user, test_timeline):
    """Test marking milestone with specific completion date."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][0]
    completion_date = date.today() - timedelta(days=2)
    
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id,
        completion_date=completion_date
    )
    
    db.refresh(milestone)
    assert milestone.actual_completion_date == completion_date


def test_mark_milestone_completed_already_completed(db, test_user, test_timeline):
    """Test error when marking already completed milestone."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][0]
    
    # Complete it once
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id
    )
    
    # Try to complete again
    with pytest.raises(ProgressServiceError) as exc_info:
        service.mark_milestone_completed(
            milestone_id=milestone.id,
            user_id=test_user.id
        )
    
    assert "already marked as completed" in str(exc_info.value)


def test_log_progress_event(db, test_user):
    """Test logging a progress event."""
    service = ProgressService(db)
    
    event_id = service.log_progress_event(
        user_id=test_user.id,
        event_type="achievement",
        title="Test Achievement",
        description="Test description",
        impact_level="high",
        tags="test,milestone"
    )
    
    assert event_id is not None


def test_calculate_milestone_delay_overdue(db, test_user, test_timeline):
    """Test calculating delay for overdue milestone."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][0]  # Target date is 5 days ago
    
    delay_info = service.calculate_milestone_delay(milestone.id)
    
    assert delay_info is not None
    assert delay_info["delay_days"] == 5  # 5 days overdue
    assert delay_info["status"] == "overdue"
    assert delay_info["is_completed"] is False


def test_calculate_milestone_delay_on_track(db, test_user, test_timeline):
    """Test calculating delay for on-track milestone."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][1]  # Target date is 10 days from now
    
    delay_info = service.calculate_milestone_delay(milestone.id)
    
    assert delay_info is not None
    assert delay_info["delay_days"] < 0  # Still has time
    assert delay_info["status"] == "on_track"


def test_calculate_milestone_delay_completed_early(db, test_user, test_timeline):
    """Test delay calculation for early completion."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][1]
    
    # Complete it early
    early_date = milestone.target_date - timedelta(days=3)
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id,
        completion_date=early_date
    )
    
    delay_info = service.calculate_milestone_delay(milestone.id)
    
    assert delay_info["delay_days"] == -3  # 3 days early
    assert delay_info["status"] == "completed_on_time"


def test_calculate_milestone_delay_completed_late(db, test_user, test_timeline):
    """Test delay calculation for late completion."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][1]
    
    # Complete it late
    late_date = milestone.target_date + timedelta(days=5)
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id,
        completion_date=late_date
    )
    
    delay_info = service.calculate_milestone_delay(milestone.id)
    
    assert delay_info["delay_days"] == 5  # 5 days late
    assert delay_info["status"] == "completed_delayed"


def test_get_stage_progress(db, test_user, test_timeline):
    """Test getting stage progress."""
    service = ProgressService(db)
    stage = test_timeline["stages"][0]
    
    # Complete one of two milestones in stage
    milestone = test_timeline["milestones"][0]
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id
    )
    
    progress = service.get_stage_progress(stage.id)
    
    assert progress is not None
    assert progress["total_milestones"] == 2
    assert progress["completed_milestones"] == 1
    assert progress["completion_percentage"] == 50.0


def test_get_stage_progress_overdue_count(db, test_user, test_timeline):
    """Test counting overdue milestones in stage."""
    service = ProgressService(db)
    stage = test_timeline["stages"][0]
    
    progress = service.get_stage_progress(stage.id)
    
    # One milestone is overdue (target date 5 days ago)
    assert progress["overdue_milestones"] == 1


def test_get_timeline_progress(db, test_user, test_timeline):
    """Test getting overall timeline progress."""
    service = ProgressService(db)
    timeline = test_timeline["timeline"]
    
    # Complete one milestone
    milestone = test_timeline["milestones"][0]
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id
    )
    
    progress = service.get_timeline_progress(timeline.id)
    
    assert progress is not None
    assert progress["total_stages"] == 2
    assert progress["total_milestones"] == 3
    assert progress["completed_milestones"] == 1
    assert progress["completion_percentage"] > 0


def test_get_timeline_progress_critical_milestones(db, test_user, test_timeline):
    """Test critical milestone tracking in timeline progress."""
    service = ProgressService(db)
    timeline = test_timeline["timeline"]
    
    progress = service.get_timeline_progress(timeline.id)
    
    assert progress["critical_milestones"] == 1  # One critical milestone
    assert progress["completed_critical_milestones"] == 0
    
    # Complete the critical milestone
    critical_milestone = test_timeline["milestones"][0]
    service.mark_milestone_completed(
        milestone_id=critical_milestone.id,
        user_id=test_user.id
    )
    
    progress = service.get_timeline_progress(timeline.id)
    assert progress["completed_critical_milestones"] == 1


def test_get_timeline_progress_overdue_critical(db, test_user, test_timeline):
    """Test tracking overdue critical milestones."""
    service = ProgressService(db)
    timeline = test_timeline["timeline"]
    
    progress = service.get_timeline_progress(timeline.id)
    
    # One critical milestone is overdue
    assert progress["overdue_critical_milestones"] == 1


def test_get_user_progress_events(db, test_user, test_timeline):
    """Test getting user's progress events."""
    service = ProgressService(db)
    
    # Create some events
    service.log_progress_event(
        user_id=test_user.id,
        event_type="achievement",
        title="Event 1",
        description="Description 1"
    )
    service.log_progress_event(
        user_id=test_user.id,
        event_type="update",
        title="Event 2",
        description="Description 2"
    )
    
    events = service.get_user_progress_events(test_user.id)
    
    assert len(events) >= 2


def test_get_user_progress_events_filtered(db, test_user, test_timeline):
    """Test filtered progress event retrieval."""
    service = ProgressService(db)
    milestone = test_timeline["milestones"][0]
    
    # Complete milestone (creates event)
    service.mark_milestone_completed(
        milestone_id=milestone.id,
        user_id=test_user.id
    )
    
    # Get events filtered by milestone
    events = service.get_user_progress_events(
        test_user.id,
        milestone_id=milestone.id
    )
    
    assert len(events) >= 1
    assert all(e.milestone_id == milestone.id for e in events)


def test_duration_progress_calculation(db, test_user, test_timeline):
    """Test timeline duration progress calculation."""
    service = ProgressService(db)
    timeline = test_timeline["timeline"]
    
    progress = service.get_timeline_progress(timeline.id)
    
    # Timeline started 30 days ago, ends in 300 days
    # So we're about 9% through
    assert progress["duration_progress_percentage"] is not None
    assert progress["duration_progress_percentage"] > 0
    assert progress["duration_progress_percentage"] < 100

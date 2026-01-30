"""
Integration test for progress tracking: CommittedTimeline → ProgressEvents → Delay Flags.

Tests:
- Load CommittedTimeline
- Mark multiple milestones as completed
- Create ProgressEvents (append-only)
- Compute delay flags
- Validate timeline status updates
"""
import pytest
import os
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from app.database import Base
from app.models.user import User
from app.models.baseline import Baseline
from app.models.committed_timeline import CommittedTimeline
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.models.progress_event import ProgressEvent
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
def test_committed_timeline(db, test_user):
    """Create a test committed timeline with stages and milestones."""
    # Create baseline
    baseline = Baseline(
        user_id=test_user.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today() - timedelta(days=60),
        total_duration_months=48,
    )
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    
    # Create committed timeline
    timeline = CommittedTimeline(
        user_id=test_user.id,
        baseline_id=baseline.id,
        title="My PhD Timeline",
        committed_date=date.today() - timedelta(days=30),
        target_completion_date=date.today() + timedelta(days=300),
    )
    db.add(timeline)
    db.commit()
    db.refresh(timeline)
    
    # Create stages
    stage1 = TimelineStage(
        committed_timeline_id=timeline.id,
        title="Literature Review",
        stage_order=1,
        status="in_progress",
    )
    stage2 = TimelineStage(
        committed_timeline_id=timeline.id,
        title="Research Phase",
        stage_order=2,
        status="not_started",
    )
    stage3 = TimelineStage(
        committed_timeline_id=timeline.id,
        title="Writing",
        stage_order=3,
        status="not_started",
    )
    db.add_all([stage1, stage2, stage3])
    db.commit()
    db.refresh(stage1)
    db.refresh(stage2)
    db.refresh(stage3)
    
    # Create milestones with different target dates
    today = date.today()
    milestone1 = TimelineMilestone(
        timeline_stage_id=stage1.id,
        title="Complete initial literature review",
        milestone_order=1,
        target_date=today - timedelta(days=10),  # Overdue
        is_critical=True,
        is_completed=False,
    )
    milestone2 = TimelineMilestone(
        timeline_stage_id=stage1.id,
        title="Identify research gaps",
        milestone_order=2,
        target_date=today - timedelta(days=5),  # Overdue
        is_critical=False,
        is_completed=False,
    )
    milestone3 = TimelineMilestone(
        timeline_stage_id=stage2.id,
        title="Design experiments",
        milestone_order=1,
        target_date=today + timedelta(days=10),  # Future
        is_critical=True,
        is_completed=False,
    )
    milestone4 = TimelineMilestone(
        timeline_stage_id=stage2.id,
        title="Collect initial data",
        milestone_order=2,
        target_date=today + timedelta(days=30),  # Future
        is_critical=False,
        is_completed=False,
    )
    milestone5 = TimelineMilestone(
        timeline_stage_id=stage3.id,
        title="Write first draft",
        milestone_order=1,
        target_date=today + timedelta(days=60),  # Future
        is_critical=True,
        is_completed=False,
    )
    
    db.add_all([milestone1, milestone2, milestone3, milestone4, milestone5])
    db.commit()
    db.refresh(milestone1)
    db.refresh(milestone2)
    db.refresh(milestone3)
    db.refresh(milestone4)
    db.refresh(milestone5)
    
    return {
        "timeline": timeline,
        "milestones": [milestone1, milestone2, milestone3, milestone4, milestone5],
        "stages": [stage1, stage2, stage3]
    }


class TestProgressTrackingIntegration:
    """Integration test for progress tracking."""
    
    def test_progress_tracking_full_flow(
        self,
        db,
        test_user,
        test_committed_timeline
    ):
        """
        Test complete progress tracking flow.
        
        Validates:
        - ProgressEvents are append-only
        - Timeline status updates correctly
        - Delay flags are computed correctly
        """
        timeline = test_committed_timeline["timeline"]
        milestones = test_committed_timeline["milestones"]
        user_id = test_user.id
        
        progress_service = ProgressService(db)
        
        # Step 1: Load CommittedTimeline
        loaded_timeline = db.query(CommittedTimeline).filter(
            CommittedTimeline.id == timeline.id
        ).first()
        assert loaded_timeline is not None
        assert loaded_timeline.user_id == user_id
        
        # Get initial milestone count
        initial_events_count = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).count()
        assert initial_events_count == 0, "Should start with no progress events"
        
        # Step 2: Mark multiple milestones as completed
        # Milestone 1: Completed on time (target was 10 days ago, complete 10 days ago)
        milestone1 = milestones[0]
        completion_date1 = milestone1.target_date  # On time
        event_id1 = progress_service.mark_milestone_completed(
            milestone_id=milestone1.id,
            user_id=user_id,
            completion_date=completion_date1,
            notes="Completed literature review"
        )
        assert event_id1 is not None
        
        # Milestone 2: Completed late (target was 5 days ago, complete today)
        milestone2 = milestones[1]
        completion_date2 = date.today()  # 5 days late
        event_id2 = progress_service.mark_milestone_completed(
            milestone_id=milestone2.id,
            user_id=user_id,
            completion_date=completion_date2,
            notes="Identified research gaps"
        )
        assert event_id2 is not None
        
        # Milestone 3: Completed early (target is 10 days in future, complete today)
        milestone3 = milestones[2]
        completion_date3 = date.today()  # 10 days early
        event_id3 = progress_service.mark_milestone_completed(
            milestone_id=milestone3.id,
            user_id=user_id,
            completion_date=completion_date3,
            notes="Designed experiments early"
        )
        assert event_id3 is not None
        
        db.commit()
        
        # Step 3: Verify ProgressEvents were created
        all_events = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).order_by(ProgressEvent.event_date).all()
        
        assert len(all_events) == 3, f"Expected 3 progress events, got {len(all_events)}"
        
        # Verify event details
        event1 = db.query(ProgressEvent).filter(ProgressEvent.id == event_id1).first()
        assert event1 is not None
        assert event1.event_type == "milestone_completed"
        assert event1.milestone_id == milestone1.id
        assert "on time" in event1.description.lower() or "delayed by 0" in event1.description.lower()
        
        event2 = db.query(ProgressEvent).filter(ProgressEvent.id == event_id2).first()
        assert event2 is not None
        assert event2.event_type == "milestone_completed"
        assert event2.milestone_id == milestone2.id
        assert "delayed" in event2.description.lower()
        
        event3 = db.query(ProgressEvent).filter(ProgressEvent.id == event_id3).first()
        assert event3 is not None
        assert event3.event_type == "milestone_completed"
        assert event3.milestone_id == milestone3.id
        assert "early" in event3.description.lower()
        
        # Step 4: Validate ProgressEvents are append-only
        # Try to modify an event (should not be possible through service)
        original_description = event1.description
        original_event_date = event1.event_date
        
        # Direct database modification attempt (to test immutability)
        # In practice, this would be prevented by application logic
        # We verify that the service doesn't provide update methods
        assert not hasattr(progress_service, 'update_progress_event'), \
            "ProgressService should not have update method (append-only)"
        assert not hasattr(progress_service, 'delete_progress_event'), \
            "ProgressService should not have delete method (append-only)"
        
        # Verify events are immutable by checking they can't be re-created
        # (milestone already completed)
        with pytest.raises(ProgressServiceError, match="already marked as completed"):
            progress_service.mark_milestone_completed(
                milestone_id=milestone1.id,
                user_id=user_id,
                completion_date=date.today()
            )
        
        # Verify event count didn't increase (append-only means no updates)
        final_events_count = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).count()
        assert final_events_count == 3, "Event count should remain 3 (append-only)"
        
        # Step 5: Compute delay flags for all milestones
        delay_flags1 = progress_service.compute_delay_flags(milestone1.id)
        assert delay_flags1 is not None
        assert delay_flags1["is_completed"] is True
        assert delay_flags1["is_on_time"] is True
        assert delay_flags1["is_delayed"] is False
        assert delay_flags1["delay_days"] == 0
        assert delay_flags1["status"] == "completed_on_time"
        
        delay_flags2 = progress_service.compute_delay_flags(milestone2.id)
        assert delay_flags2 is not None
        assert delay_flags2["is_completed"] is True
        assert delay_flags2["is_delayed"] is True
        assert delay_flags2["is_on_time"] is False
        assert delay_flags2["delay_days"] == 5  # 5 days late
        assert delay_flags2["status"] == "completed_delayed"
        
        delay_flags3 = progress_service.compute_delay_flags(milestone3.id)
        assert delay_flags3 is not None
        assert delay_flags3["is_completed"] is True
        assert delay_flags3["is_early"] is True
        assert delay_flags3["is_delayed"] is False
        assert delay_flags3["delay_days"] == -10  # 10 days early
        assert delay_flags3["status"] in ["completed_on_time", "on_track"]  # Early completion
        
        # Check incomplete milestones
        milestone4 = milestones[3]
        delay_flags4 = progress_service.compute_delay_flags(milestone4.id)
        assert delay_flags4 is not None
        assert delay_flags4["is_completed"] is False
        assert delay_flags4["has_target_date"] is True
        
        # Step 6: Validate timeline status updates correctly
        # Get timeline progress summary
        timeline_progress = progress_service.get_timeline_progress(timeline.id)
        assert timeline_progress is not None
        assert timeline_progress["has_data"] is True
        assert timeline_progress["total_milestones"] == 5
        assert timeline_progress["completed_milestones"] == 3
        assert timeline_progress["completion_percentage"] == 60.0  # 3/5 = 60%
        
        # Verify milestone statuses
        db.refresh(milestone1)
        db.refresh(milestone2)
        db.refresh(milestone3)
        db.refresh(milestone4)
        
        assert milestone1.is_completed is True
        assert milestone1.actual_completion_date == completion_date1
        assert milestone2.is_completed is True
        assert milestone2.actual_completion_date == completion_date2
        assert milestone3.is_completed is True
        assert milestone3.actual_completion_date == completion_date3
        assert milestone4.is_completed is False
        
        # Summary validation
        print("\n=== Progress Tracking Validation Summary ===")
        print(f"✓ CommittedTimeline loaded: {timeline.id}")
        print(f"✓ Milestones completed: 3/5")
        print(f"✓ ProgressEvents created: {len(all_events)}")
        print(f"✓ ProgressEvents are append-only: No update/delete methods")
        print(f"✓ Delay flags computed: On-time=1, Delayed=1, Early=1")
        print(f"✓ Timeline completion: {timeline_progress['completion_percentage']}%")
        print(f"✓ All validations passed!")

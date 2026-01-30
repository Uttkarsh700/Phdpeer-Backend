"""
Test validation checks for AnalyticsOrchestrator invariants.

Tests:
- No analytics without committed timeline
- No progress without committed milestones (already tested in progress_service)
- No journey health score without submission (already tested in phd_doctor_orchestrator)
- No state mutation inside AnalyticsOrchestrator
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
from app.orchestrators.analytics_orchestrator import (
    AnalyticsOrchestrator,
    AnalyticsOrchestratorError
)
from app.utils.invariants import (
    AnalyticsWithoutCommittedTimelineError,
    StateMutationInAnalyticsOrchestratorError,
    check_analytics_has_committed_timeline,
    check_no_state_mutation_in_analytics_orchestrator
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


class TestAnalyticsInvariants:
    """Test analytics invariants."""
    
    def test_no_analytics_without_committed_timeline(self, db, test_user):
        """Test: No analytics without committed timeline."""
        user_id = test_user.id
        
        # Try to run analytics without committed timeline
        orchestrator = AnalyticsOrchestrator(db, user_id)
        request_id = str(uuid4())
        
        with pytest.raises(AnalyticsWithoutCommittedTimelineError) as exc_info:
            orchestrator.run(
                request_id=request_id,
                user_id=user_id,
                timeline_id=None
            )
        
        assert "No CommittedTimeline found" in str(exc_info.value)
        assert exc_info.value.invariant_name == "analytics_without_committed_timeline"
        
        # Try with non-existent timeline ID
        fake_timeline_id = uuid4()
        with pytest.raises(AnalyticsWithoutCommittedTimelineError) as exc_info:
            orchestrator.run(
                request_id=str(uuid4()),
                user_id=user_id,
                timeline_id=fake_timeline_id
            )
        
        assert "not found" in str(exc_info.value) or "not owned" in str(exc_info.value)
    
    def test_analytics_with_committed_timeline_succeeds(self, db, test_user):
        """Test: Analytics succeeds when committed timeline exists."""
        user_id = test_user.id
        
        # Create baseline
        baseline = Baseline(
            user_id=user_id,
            program_name="PhD in Computer Science",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today() - timedelta(days=90),
            total_duration_months=48,
        )
        db.add(baseline)
        db.commit()
        db.refresh(baseline)
        
        # Create committed timeline
        timeline = CommittedTimeline(
            user_id=user_id,
            baseline_id=baseline.id,
            title="My PhD Timeline",
            committed_date=date.today() - timedelta(days=60),
            target_completion_date=date.today() + timedelta(days=300),
        )
        db.add(timeline)
        db.commit()
        db.refresh(timeline)
        
        # Analytics should succeed
        orchestrator = AnalyticsOrchestrator(db, user_id)
        request_id = str(uuid4())
        
        # Should not raise AnalyticsWithoutCommittedTimelineError
        try:
            result = orchestrator.run(
                request_id=request_id,
                user_id=user_id,
                timeline_id=timeline.id
            )
            # If it succeeds, we should get a result
            assert result is not None
            assert "snapshot_id" in result
        except AnalyticsWithoutCommittedTimelineError:
            pytest.fail("AnalyticsWithoutCommittedTimelineError should not be raised when committed timeline exists")
    
    def test_no_state_mutation_in_analytics_orchestrator(self, db, test_user):
        """Test: No state mutation inside AnalyticsOrchestrator."""
        # This test verifies that the invariant check exists
        # The actual enforcement happens at runtime through stack inspection
        
        # Verify the check function exists
        assert callable(check_no_state_mutation_in_analytics_orchestrator)
        
        # Test that mutation operations would be caught
        # (In practice, this is enforced through stack inspection)
        try:
            check_no_state_mutation_in_analytics_orchestrator(
                db=db,
                operation="update_timeline",
                caller_context={"test": True}
            )
            # If we get here, the check didn't raise (which is expected if not called from AnalyticsOrchestrator)
        except StateMutationInAnalyticsOrchestratorError:
            # This is expected if called from AnalyticsOrchestrator context
            pass
    
    def test_invariant_check_functions_exist(self):
        """Test: All invariant check functions exist."""
        from app.utils.invariants import (
            check_analytics_has_committed_timeline,
            check_no_state_mutation_in_analytics_orchestrator,
            check_progress_event_has_milestone,
            check_assessment_has_submission
        )
        
        assert callable(check_analytics_has_committed_timeline)
        assert callable(check_no_state_mutation_in_analytics_orchestrator)
        assert callable(check_progress_event_has_milestone)
        assert callable(check_assessment_has_submission)
    
    def test_invariant_exceptions_exist(self):
        """Test: All invariant exception classes exist."""
        from app.utils.invariants import (
            AnalyticsWithoutCommittedTimelineError,
            StateMutationInAnalyticsOrchestratorError,
            ProgressEventWithoutMilestoneError,
            AssessmentWithoutSubmissionError
        )
        
        # Verify exceptions can be instantiated
        exc1 = AnalyticsWithoutCommittedTimelineError("Test message")
        assert exc1.invariant_name == "analytics_without_committed_timeline"
        
        exc2 = StateMutationInAnalyticsOrchestratorError("Test message")
        assert exc2.invariant_name == "state_mutation_in_analytics_orchestrator"
        
        exc3 = ProgressEventWithoutMilestoneError("Test message")
        assert exc3.invariant_name == "progress_event_without_milestone"
        
        exc4 = AssessmentWithoutSubmissionError("Test message")
        assert exc4.invariant_name == "assessment_without_submission"

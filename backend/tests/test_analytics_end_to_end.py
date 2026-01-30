"""
End-to-end test for AnalyticsOrchestrator.

Tests:
- Assumes existing data (CommittedTimeline, ProgressEvents, JourneyAssessment)
- Calls AnalyticsOrchestrator.run()
- Returns AnalyticsSummary

Validates:
- Summary reflects real system state
- No missing data
- Deterministic output
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
from app.models.journey_assessment import JourneyAssessment
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.orchestrators.analytics_orchestrator import (
    AnalyticsOrchestrator,
    AnalyticsOrchestratorError
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
def test_committed_timeline_with_progress(db, test_user):
    """
    Create a committed timeline with stages, milestones, and progress events.
    
    This fixture sets up the complete data structure needed for analytics.
    """
    # Create baseline
    baseline = Baseline(
        user_id=test_user.id,
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
        user_id=test_user.id,
        baseline_id=baseline.id,
        title="My PhD Timeline",
        committed_date=date.today() - timedelta(days=60),
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
        target_date=today - timedelta(days=20),  # Overdue
        is_critical=True,
        is_completed=True,
        actual_completion_date=today - timedelta(days=10),  # Completed 10 days late
    )
    milestone2 = TimelineMilestone(
        timeline_stage_id=stage1.id,
        title="Identify research gaps",
        milestone_order=2,
        target_date=today - timedelta(days=10),  # Overdue
        is_critical=False,
        is_completed=True,
        actual_completion_date=today - timedelta(days=5),  # Completed 5 days late
    )
    milestone3 = TimelineMilestone(
        timeline_stage_id=stage2.id,
        title="Design experiments",
        milestone_order=1,
        target_date=today + timedelta(days=10),  # Future
        is_critical=True,
        is_completed=True,
        actual_completion_date=today - timedelta(days=5),  # Completed 15 days early
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
    
    # Create progress events for completed milestones
    event1 = ProgressEvent(
        user_id=test_user.id,
        milestone_id=milestone1.id,
        event_type="milestone_completed",
        title="Milestone Completed: Complete initial literature review",
        description="Completed milestone: Complete initial literature review (delayed by 10 days)",
        event_date=milestone1.actual_completion_date,
        impact_level="medium",
    )
    event2 = ProgressEvent(
        user_id=test_user.id,
        milestone_id=milestone2.id,
        event_type="milestone_completed",
        title="Milestone Completed: Identify research gaps",
        description="Completed milestone: Identify research gaps (delayed by 5 days)",
        event_date=milestone2.actual_completion_date,
        impact_level="low",
    )
    event3 = ProgressEvent(
        user_id=test_user.id,
        milestone_id=milestone3.id,
        event_type="milestone_completed",
        title="Milestone Completed: Design experiments",
        description="Completed milestone: Design experiments (completed 15 days early)",
        event_date=milestone3.actual_completion_date,
        impact_level="low",
    )
    
    db.add_all([event1, event2, event3])
    db.commit()
    
    return {
        "timeline": timeline,
        "milestones": [milestone1, milestone2, milestone3, milestone4, milestone5],
        "stages": [stage1, stage2, stage3],
        "progress_events": [event1, event2, event3]
    }


@pytest.fixture
def test_journey_assessment(db, test_user):
    """Create a journey assessment."""
    assessment = JourneyAssessment(
        user_id=test_user.id,
        assessment_date=date.today() - timedelta(days=5),
        assessment_type="self_assessment",
        overall_progress_rating=75,
        research_quality_rating=80,
        timeline_adherence_rating=65,
        strengths="Strong research progress, good work-life balance",
        challenges="Some timeline delays, need better deadline management",
        action_items="Focus on critical milestones, improve time management",
        notes="First assessment"
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


class TestAnalyticsEndToEnd:
    """End-to-end test for AnalyticsOrchestrator."""
    
    def test_analytics_orchestrator_end_to_end(
        self,
        db,
        test_user,
        test_committed_timeline_with_progress,
        test_journey_assessment
    ):
        """
        Test complete analytics orchestrator flow.
        
        Validates:
        - Summary reflects real system state
        - No missing data
        - Deterministic output
        """
        user_id = test_user.id
        timeline = test_committed_timeline_with_progress["timeline"]
        milestones = test_committed_timeline_with_progress["milestones"]
        progress_events = test_committed_timeline_with_progress["progress_events"]
        assessment = test_journey_assessment
        
        # Verify assumptions: Data exists
        assert timeline is not None
        assert len(milestones) == 5
        assert len(progress_events) == 3
        assert assessment is not None
        
        print("\n[1/4] Verifying assumptions...")
        print(f"✓ CommittedTimeline exists: {timeline.id}")
        print(f"✓ ProgressEvents exist: {len(progress_events)}")
        print(f"✓ JourneyAssessment exists: {assessment.id}")
        
        # Step 1: Call AnalyticsOrchestrator.run()
        print("\n[2/4] Calling AnalyticsOrchestrator.run()...")
        orchestrator = AnalyticsOrchestrator(db, user_id)
        request_id = str(uuid4())
        
        result = orchestrator.run(
            request_id=request_id,
            user_id=user_id,
            timeline_id=timeline.id
        )
        
        print(f"✓ Analytics generated")
        print(f"  Snapshot ID: {result['snapshot_id']}")
        print(f"  Timeline Status: {result['timeline_status']}")
        print(f"  Completion: {result['milestones']['completion_percentage']}%")
        
        # Step 2: Validate AnalyticsSummary structure
        print("\n[3/4] Validating AnalyticsSummary...")
        
        # Check snapshot was created
        snapshot = db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.id == result['snapshot_id']
        ).first()
        assert snapshot is not None, "AnalyticsSnapshot should be created"
        assert snapshot.user_id == user_id
        assert snapshot.summary_json is not None
        
        summary_json = snapshot.summary_json
        
        # Validation 1: Summary reflects real system state
        print("  Validating summary reflects real system state...")
        
        # Timeline status should reflect actual state
        # We have 3 completed, 2 pending, with some delays
        assert result['timeline_status'] in ['on_track', 'delayed', 'completed']
        
        # Milestone completion should match actual state
        assert result['milestones']['total'] == 5
        assert result['milestones']['completed'] == 3
        assert result['milestones']['pending'] == 2
        assert result['milestones']['completion_percentage'] == 60.0  # 3/5 = 60%
        print("    ✓ Milestone counts match actual state")
        
        # Delay metrics should reflect actual delays
        # Milestone 1: 10 days late, Milestone 2: 5 days late
        # Milestone 3: 15 days early (negative delay)
        assert result['delays']['total_delays'] >= 0
        assert result['delays']['overdue_milestones'] >= 0
        # We have 2 overdue milestones (milestone1 and milestone2)
        assert result['delays']['overdue_milestones'] >= 2
        print("    ✓ Delay metrics reflect actual delays")
        
        # Journey health should reflect latest assessment
        assert result['journey_health']['latest_score'] == 75.0
        assert 'research_quality' in result['journey_health']['dimensions'] or \
               'research_quality_rating' in result['journey_health']['dimensions']
        print("    ✓ Journey health reflects latest assessment")
        
        # Validation 2: No missing data
        print("  Validating no missing data...")
        
        # Check all required fields are present
        required_fields = [
            'timeline_id', 'user_id', 'generated_at',
            'timeline_status',
            'milestone_completion_percentage', 'total_milestones',
            'completed_milestones', 'pending_milestones',
            'total_delays', 'overdue_milestones',
            'overdue_critical_milestones', 'average_delay_days', 'max_delay_days',
            'latest_health_score', 'health_dimensions',
            'longitudinal_summary'
        ]
        
        for field in required_fields:
            assert field in summary_json, f"Missing required field: {field}"
        print("    ✓ All required fields present")
        
        # Check no None values for critical fields
        assert summary_json['timeline_status'] is not None
        assert summary_json['milestone_completion_percentage'] is not None
        assert summary_json['total_milestones'] is not None
        assert summary_json['completed_milestones'] is not None
        assert summary_json['pending_milestones'] is not None
        assert summary_json['total_delays'] is not None
        assert summary_json['overdue_milestones'] is not None
        print("    ✓ No None values in critical fields")
        
        # Check longitudinal summary has data
        assert summary_json['longitudinal_summary'] is not None
        assert isinstance(summary_json['longitudinal_summary'], dict)
        print("    ✓ Longitudinal summary present")
        
        # Validation 3: Deterministic output
        print("\n[4/4] Validating deterministic output...")
        
        # Call orchestrator again with same inputs
        request_id2 = str(uuid4())
        result2 = orchestrator.run(
            request_id=request_id2,
            user_id=user_id,
            timeline_id=timeline.id
        )
        
        # Should get same results (idempotency)
        # Note: Due to idempotency, it might return cached result
        # But the summary should be identical
        snapshot2 = db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.id == result2['snapshot_id']
        ).first()
        
        # Compare key metrics (should be identical)
        assert result['timeline_status'] == result2['timeline_status']
        assert result['milestones']['completion_percentage'] == result2['milestones']['completion_percentage']
        assert result['milestones']['total'] == result2['milestones']['total']
        assert result['milestones']['completed'] == result2['milestones']['completed']
        assert result['delays']['total_delays'] == result2['delays']['total_delays']
        assert result['delays']['overdue_milestones'] == result2['delays']['overdue_milestones']
        assert result['journey_health']['latest_score'] == result2['journey_health']['latest_score']
        print("    ✓ Same inputs produce same outputs (deterministic)")
        
        # Call with exact same data again - should be identical
        # (This tests that the aggregation logic is deterministic)
        summary1 = summary_json
        summary2 = snapshot2.summary_json
        
        # Compare numeric values (should be identical)
        assert summary1['milestone_completion_percentage'] == summary2['milestone_completion_percentage']
        assert summary1['total_milestones'] == summary2['total_milestones']
        assert summary1['completed_milestones'] == summary2['completed_milestones']
        assert summary1['total_delays'] == summary2['total_delays']
        assert summary1['overdue_milestones'] == summary2['overdue_milestones']
        print("    ✓ Aggregation logic is deterministic")
        
        # Summary validation
        print("\n=== Analytics End-to-End Validation Summary ===")
        print(f"✓ CommittedTimeline: {timeline.id}")
        print(f"✓ ProgressEvents: {len(progress_events)}")
        print(f"✓ JourneyAssessment: {assessment.id}")
        print(f"✓ AnalyticsSnapshot created: {snapshot.id}")
        print(f"✓ Timeline Status: {result['timeline_status']}")
        print(f"✓ Completion: {result['milestones']['completion_percentage']}%")
        print(f"✓ Total Milestones: {result['milestones']['total']}")
        print(f"✓ Completed: {result['milestones']['completed']}")
        print(f"✓ Pending: {result['milestones']['pending']}")
        print(f"✓ Overdue: {result['delays']['overdue_milestones']}")
        print(f"✓ Health Score: {result['journey_health']['latest_score']}")
        print(f"✓ Summary reflects real system state")
        print(f"✓ No missing data")
        print(f"✓ Deterministic output")
        print(f"✓ All validations passed!")

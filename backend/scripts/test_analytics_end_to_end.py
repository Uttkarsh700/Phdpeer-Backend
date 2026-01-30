#!/usr/bin/env python3
"""
End-to-end test script for AnalyticsOrchestrator.

Usage:
    python backend/scripts/test_analytics_end_to_end.py

Note: This script requires PostgreSQL. Set DATABASE_URL environment variable:
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    python backend/scripts/test_analytics_end_to_end.py

This script:
1. Assumes existing data (CommittedTimeline, ProgressEvents, JourneyAssessment)
2. Calls AnalyticsOrchestrator.run()
3. Returns AnalyticsSummary

Validates:
- Summary reflects real system state
- No missing data
- Deterministic output
"""
import sys
import os
from datetime import date, timedelta
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


def create_test_data(db, user_id):
    """Create test data: CommittedTimeline, ProgressEvents, JourneyAssessment."""
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
    
    # Create milestones
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
    
    # Create progress events
    event1 = ProgressEvent(
        user_id=user_id,
        milestone_id=milestone1.id,
        event_type="milestone_completed",
        title="Milestone Completed: Complete initial literature review",
        description="Completed milestone: Complete initial literature review (delayed by 10 days)",
        event_date=milestone1.actual_completion_date,
        impact_level="medium",
    )
    event2 = ProgressEvent(
        user_id=user_id,
        milestone_id=milestone2.id,
        event_type="milestone_completed",
        title="Milestone Completed: Identify research gaps",
        description="Completed milestone: Identify research gaps (delayed by 5 days)",
        event_date=milestone2.actual_completion_date,
        impact_level="low",
    )
    event3 = ProgressEvent(
        user_id=user_id,
        milestone_id=milestone3.id,
        event_type="milestone_completed",
        title="Milestone Completed: Design experiments",
        description="Completed milestone: Design experiments (completed 15 days early)",
        event_date=milestone3.actual_completion_date,
        impact_level="low",
    )
    
    db.add_all([event1, event2, event3])
    db.commit()
    
    # Create journey assessment
    assessment = JourneyAssessment(
        user_id=user_id,
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
    
    return {
        "timeline": timeline,
        "milestones": [milestone1, milestone2, milestone3, milestone4, milestone5],
        "progress_events": [event1, event2, event3],
        "assessment": assessment
    }


def main():
    """Run the analytics end-to-end test."""
    print("=" * 60)
    print("Analytics End-to-End Test")
    print("=" * 60)
    
    # Setup
    db = create_test_database()
    
    try:
        # Create test user
        print("\n[1/5] Creating test user...")
        user = create_test_user(db)
        user_id = user.id
        print(f"✓ User created: {user_id} ({user.email})")
        
        # Create test data
        print("\n[2/5] Creating test data...")
        test_data = create_test_data(db, user_id)
        timeline = test_data["timeline"]
        milestones = test_data["milestones"]
        progress_events = test_data["progress_events"]
        assessment = test_data["assessment"]
        
        print(f"✓ CommittedTimeline created: {timeline.id}")
        print(f"✓ Milestones created: {len(milestones)}")
        print(f"✓ ProgressEvents created: {len(progress_events)}")
        print(f"✓ JourneyAssessment created: {assessment.id}")
        
        # Verify assumptions
        print("\n[3/5] Verifying assumptions...")
        assert timeline is not None
        assert len(milestones) == 5
        assert len(progress_events) == 3
        assert assessment is not None
        print("✓ All assumptions met")
        
        # Call AnalyticsOrchestrator.run()
        print("\n[4/5] Calling AnalyticsOrchestrator.run()...")
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
        
        # Get snapshot
        snapshot = db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.id == result['snapshot_id']
        ).first()
        assert snapshot is not None
        summary_json = snapshot.summary_json
        
        # Validations
        print("\n[5/5] Validating results...")
        
        # Validation 1: Summary reflects real system state
        print("  Validating summary reflects real system state...")
        assert result['milestones']['total'] == 5
        assert result['milestones']['completed'] == 3
        assert result['milestones']['pending'] == 2
        assert result['milestones']['completion_percentage'] == 60.0
        assert result['delays']['overdue_milestones'] >= 2
        assert result['journey_health']['latest_score'] == 75.0
        print("    ✓ Summary reflects real system state")
        
        # Validation 2: No missing data
        print("  Validating no missing data...")
        required_fields = [
            'timeline_id', 'user_id', 'generated_at',
            'timeline_status', 'milestone_completion_percentage',
            'total_milestones', 'completed_milestones', 'pending_milestones',
            'total_delays', 'overdue_milestones',
            'overdue_critical_milestones', 'average_delay_days', 'max_delay_days',
            'latest_health_score', 'health_dimensions', 'longitudinal_summary'
        ]
        
        for field in required_fields:
            assert field in summary_json, f"Missing field: {field}"
        print("    ✓ All required fields present")
        
        # Validation 3: Deterministic output
        print("  Validating deterministic output...")
        request_id2 = str(uuid4())
        result2 = orchestrator.run(
            request_id=request_id2,
            user_id=user_id,
            timeline_id=timeline.id
        )
        
        # Compare key metrics
        assert result['timeline_status'] == result2['timeline_status']
        assert result['milestones']['completion_percentage'] == result2['milestones']['completion_percentage']
        assert result['milestones']['total'] == result2['milestones']['total']
        assert result['delays']['total_delays'] == result2['delays']['total_delays']
        assert result['journey_health']['latest_score'] == result2['journey_health']['latest_score']
        print("    ✓ Same inputs produce same outputs (deterministic)")
        
        print("\n" + "=" * 60)
        print("✓ ALL VALIDATIONS PASSED!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Timeline ID: {timeline.id}")
        print(f"  - Timeline Status: {result['timeline_status']}")
        print(f"  - Completion: {result['milestones']['completion_percentage']}%")
        print(f"  - Total Milestones: {result['milestones']['total']}")
        print(f"  - Completed: {result['milestones']['completed']}")
        print(f"  - Pending: {result['milestones']['pending']}")
        print(f"  - Overdue: {result['delays']['overdue_milestones']}")
        print(f"  - Health Score: {result['journey_health']['latest_score']}")
        print(f"  - Snapshot ID: {snapshot.id}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

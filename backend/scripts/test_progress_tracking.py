#!/usr/bin/env python3
"""
Standalone script to test progress tracking: CommittedTimeline → ProgressEvents → Delay Flags.

Usage:
    python backend/scripts/test_progress_tracking.py

Note: This script requires PostgreSQL. Set DATABASE_URL environment variable:
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    python backend/scripts/test_progress_tracking.py

This script:
1. Loads a CommittedTimeline
2. Marks multiple milestones as completed
3. Creates ProgressEvents (append-only)
4. Computes delay flags
5. Validates timeline status updates

Validates:
- ProgressEvents are append-only
- Timeline status updates correctly
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
from app.services.progress_service import ProgressService, ProgressServiceError


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


def create_test_timeline(db, user_id):
    """Create a test committed timeline with stages and milestones."""
    # Create baseline
    baseline = Baseline(
        user_id=user_id,
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
        user_id=user_id,
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


def main():
    """Run the progress tracking test."""
    print("=" * 60)
    print("Progress Tracking Integration Test")
    print("=" * 60)
    
    # Setup
    db = create_test_database()
    
    try:
        # Create test user
        print("\n[1/6] Creating test user...")
        user = create_test_user(db)
        user_id = user.id
        print(f"✓ User created: {user_id} ({user.email})")
        
        # Create test timeline
        print("\n[2/6] Creating committed timeline with milestones...")
        test_data = create_test_timeline(db, user_id)
        timeline = test_data["timeline"]
        milestones = test_data["milestones"]
        print(f"✓ Timeline created: {timeline.id}")
        print(f"✓ Milestones created: {len(milestones)}")
        
        # Load CommittedTimeline
        print("\n[3/6] Loading CommittedTimeline...")
        loaded_timeline = db.query(CommittedTimeline).filter(
            CommittedTimeline.id == timeline.id
        ).first()
        assert loaded_timeline is not None
        print(f"✓ Timeline loaded: {loaded_timeline.title}")
        
        # Get initial state
        initial_events_count = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).count()
        print(f"  Initial ProgressEvents: {initial_events_count}")
        
        # Mark milestones as completed
        print("\n[4/6] Marking milestones as completed...")
        progress_service = ProgressService(db)
        
        # Milestone 1: Completed on time
        milestone1 = milestones[0]
        completion_date1 = milestone1.target_date  # On time
        print(f"  Completing milestone 1: {milestone1.title} (on time)")
        event_id1 = progress_service.mark_milestone_completed(
            milestone_id=milestone1.id,
            user_id=user_id,
            completion_date=completion_date1,
            notes="Completed literature review"
        )
        print(f"    ✓ ProgressEvent created: {event_id1}")
        
        # Milestone 2: Completed late
        milestone2 = milestones[1]
        completion_date2 = date.today()  # 5 days late
        print(f"  Completing milestone 2: {milestone2.title} (5 days late)")
        event_id2 = progress_service.mark_milestone_completed(
            milestone_id=milestone2.id,
            user_id=user_id,
            completion_date=completion_date2,
            notes="Identified research gaps"
        )
        print(f"    ✓ ProgressEvent created: {event_id2}")
        
        # Milestone 3: Completed early
        milestone3 = milestones[2]
        completion_date3 = date.today()  # 10 days early
        print(f"  Completing milestone 3: {milestone3.title} (10 days early)")
        event_id3 = progress_service.mark_milestone_completed(
            milestone_id=milestone3.id,
            user_id=user_id,
            completion_date=completion_date3,
            notes="Designed experiments early"
        )
        print(f"    ✓ ProgressEvent created: {event_id3}")
        
        db.commit()
        
        # Verify ProgressEvents
        print("\n[5/6] Verifying ProgressEvents...")
        all_events = db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).order_by(ProgressEvent.event_date).all()
        
        assert len(all_events) == 3, f"Expected 3 progress events, got {len(all_events)}"
        print(f"✓ Total ProgressEvents: {len(all_events)}")
        
        # Validate append-only nature
        print("  Validating append-only property...")
        assert not hasattr(progress_service, 'update_progress_event'), \
            "ProgressService should not have update method"
        assert not hasattr(progress_service, 'delete_progress_event'), \
            "ProgressService should not have delete method"
        print("  ✓ No update/delete methods (append-only enforced)")
        
        # Try to mark already-completed milestone (should fail)
        try:
            progress_service.mark_milestone_completed(
                milestone_id=milestone1.id,
                user_id=user_id,
                completion_date=date.today()
            )
            assert False, "Should have raised an error"
        except ProgressServiceError as e:
            assert "already marked as completed" in str(e)
            print("  ✓ Duplicate completion prevented (append-only)")
        
        # Compute delay flags
        print("\n[6/6] Computing delay flags...")
        delay_flags1 = progress_service.compute_delay_flags(milestone1.id)
        print(f"  Milestone 1 delay flags:")
        print(f"    - Status: {delay_flags1['status']}")
        print(f"    - Delay days: {delay_flags1['delay_days']}")
        print(f"    - On time: {delay_flags1['is_on_time']}")
        
        delay_flags2 = progress_service.compute_delay_flags(milestone2.id)
        print(f"  Milestone 2 delay flags:")
        print(f"    - Status: {delay_flags2['status']}")
        print(f"    - Delay days: {delay_flags2['delay_days']}")
        print(f"    - Delayed: {delay_flags2['is_delayed']}")
        
        delay_flags3 = progress_service.compute_delay_flags(milestone3.id)
        print(f"  Milestone 3 delay flags:")
        print(f"    - Status: {delay_flags3['status']}")
        print(f"    - Delay days: {delay_flags3['delay_days']}")
        print(f"    - Early: {delay_flags3['is_early']}")
        
        # Get timeline progress
        timeline_progress = progress_service.get_timeline_progress(timeline.id)
        print(f"\n  Timeline progress:")
        print(f"    - Total milestones: {timeline_progress['total_milestones']}")
        print(f"    - Completed: {timeline_progress['completed_milestones']}")
        print(f"    - Completion: {timeline_progress['completion_percentage']}%")
        print(f"    - Overdue: {timeline_progress.get('overdue_milestones', 0)}")
        
        # Validations
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        # Validation 1: ProgressEvents are append-only
        assert len(all_events) == 3, "Should have exactly 3 events"
        assert not hasattr(progress_service, 'update_progress_event'), "No update method"
        assert not hasattr(progress_service, 'delete_progress_event'), "No delete method"
        print("✓ Validation 1: ProgressEvents are append-only")
        
        # Validation 2: Timeline status updates correctly
        assert timeline_progress["total_milestones"] == 5
        assert timeline_progress["completed_milestones"] == 3
        assert timeline_progress["completion_percentage"] == 60.0
        print("✓ Validation 2: Timeline status updates correctly (60% completion)")
        
        # Validation 3: Delay flags computed correctly
        assert delay_flags1["is_on_time"] is True
        assert delay_flags1["delay_days"] == 0
        assert delay_flags2["is_delayed"] is True
        assert delay_flags2["delay_days"] == 5
        assert delay_flags3["is_early"] is True
        assert delay_flags3["delay_days"] == -10
        print("✓ Validation 3: Delay flags computed correctly")
        
        # Validation 4: Milestones marked as completed
        db.refresh(milestone1)
        db.refresh(milestone2)
        db.refresh(milestone3)
        assert milestone1.is_completed is True
        assert milestone2.is_completed is True
        assert milestone3.is_completed is True
        print("✓ Validation 4: Milestones correctly marked as completed")
        
        print("\n" + "=" * 60)
        print("✓ ALL VALIDATIONS PASSED!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Timeline ID: {timeline.id}")
        print(f"  - Milestones completed: 3/5 (60%)")
        print(f"  - ProgressEvents created: {len(all_events)}")
        print(f"  - On-time completions: 1")
        print(f"  - Delayed completions: 1")
        print(f"  - Early completions: 1")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

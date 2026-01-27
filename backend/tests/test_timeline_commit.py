"""
Comprehensive tests for TimelineOrchestrator.commit() and apply_edits()

Tests:
- Draft validation
- Edit tracking
- Commit with edits
- Immutability enforcement
- Re-commit prevention
- Version increment
- Idempotency
- Edit history storage
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.baseline import Baseline
from app.models.document_artifact import DocumentArtifact
from app.models.draft_timeline import DraftTimeline
from app.models.committed_timeline import CommittedTimeline
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.models.timeline_edit_history import TimelineEditHistory
from app.orchestrators.timeline_orchestrator import (
    TimelineOrchestrator,
    TimelineOrchestratorError,
    TimelineAlreadyCommittedError,
    TimelineImmutableError
)


class TestTimelineCommit:
    """Test suite for timeline commit functionality."""
    
    @pytest.fixture
    def user(self, db: Session) -> User:
        """Create test user."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @pytest.fixture
    def document(self, db: Session, user: User) -> DocumentArtifact:
        """Create test document."""
        doc = DocumentArtifact(
            user_id=user.id,
            title="PhD Proposal",
            file_type="pdf",
            file_path="/test/proposal.pdf",
            document_text="Research proposal about machine learning.",
            word_count=500
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    
    @pytest.fixture
    def baseline(self, db: Session, user: User, document: DocumentArtifact) -> Baseline:
        """Create test baseline."""
        baseline = Baseline(
            user_id=user.id,
            document_artifact_id=document.id,
            program_type="PhD",
            duration_years=4,
            research_area="Machine Learning"
        )
        db.add(baseline)
        db.commit()
        db.refresh(baseline)
        return baseline
    
    @pytest.fixture
    def draft_timeline(self, db: Session, user: User, baseline: Baseline) -> DraftTimeline:
        """Create test draft timeline."""
        draft = DraftTimeline(
            user_id=user.id,
            baseline_id=baseline.id,
            title="PhD Timeline",
            description="4-year research plan",
            version_number="1.0",
            is_active=True
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        return draft
    
    @pytest.fixture
    def stage_with_milestones(
        self,
        db: Session,
        draft_timeline: DraftTimeline
    ) -> TimelineStage:
        """Create test stage with milestones."""
        stage = TimelineStage(
            draft_timeline_id=draft_timeline.id,
            title="Literature Review",
            description="Comprehensive literature review",
            stage_order=1,
            duration_months=6,
            status="not_started"
        )
        db.add(stage)
        db.flush()
        
        # Add milestones
        for i in range(3):
            milestone = TimelineMilestone(
                timeline_stage_id=stage.id,
                title=f"Milestone {i+1}",
                description=f"Description {i+1}",
                milestone_order=i+1,
                is_critical=(i == 0),
                deliverable_type="deliverable"
            )
            db.add(milestone)
        
        db.commit()
        db.refresh(stage)
        return stage
    
    @pytest.fixture
    def orchestrator(self, db: Session, user: User) -> TimelineOrchestrator:
        """Create timeline orchestrator."""
        return TimelineOrchestrator(db, user_id=user.id)
    
    # ===========================
    # Test: Draft Validation
    # ===========================
    
    def test_commit_nonexistent_draft(self, orchestrator: TimelineOrchestrator):
        """Test committing non-existent draft fails."""
        fake_id = uuid4()
        
        with pytest.raises(TimelineOrchestratorError) as exc:
            orchestrator.commit(
                request_id=str(uuid4()),
                draft_timeline_id=fake_id,
                user_id=orchestrator.user_id
            )
        
        assert "not found" in str(exc.value).lower()
    
    def test_commit_empty_timeline(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline
    ):
        """Test committing timeline with no stages fails."""
        with pytest.raises(TimelineOrchestratorError) as exc:
            orchestrator.commit(
                request_id=str(uuid4()),
                draft_timeline_id=draft_timeline.id,
                user_id=orchestrator.user_id
            )
        
        assert "empty" in str(exc.value).lower()
    
    def test_commit_wrong_user(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test committing another user's draft fails."""
        other_user_id = uuid4()
        
        with pytest.raises(TimelineOrchestratorError) as exc:
            orchestrator.commit(
                request_id=str(uuid4()),
                draft_timeline_id=draft_timeline.id,
                user_id=other_user_id
            )
        
        assert "not belong" in str(exc.value).lower()
    
    # ===========================
    # Test: Basic Commit
    # ===========================
    
    def test_commit_success(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test successful timeline commit."""
        request_id = str(uuid4())
        
        response = orchestrator.commit(
            request_id=request_id,
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Verify response structure
        assert "committed_timeline" in response
        assert "draft_timeline" in response
        assert "stages" in response
        assert "edit_history" in response
        assert "metadata" in response
        
        # Verify committed timeline
        committed = response["committed_timeline"]
        assert committed["status"] == "COMMITTED"
        assert committed["is_immutable"] is True
        assert UUID(committed["id"])
        
        # Verify draft frozen
        draft = response["draft_timeline"]
        assert draft["frozen"] is True
        assert draft["is_active"] is False
        
        # Verify stages copied
        assert len(response["stages"]) == 1
        assert response["stages"][0]["title"] == "Literature Review"
        assert len(response["stages"][0]["milestones"]) == 3
        
        # Verify metadata
        assert response["metadata"]["total_stages"] == 1
        assert response["metadata"]["total_milestones"] == 3
    
    def test_commit_with_title_override(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test commit with custom title."""
        new_title = "Final PhD Timeline"
        
        response = orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            title=new_title
        )
        
        assert response["committed_timeline"]["title"] == new_title
    
    # ===========================
    # Test: Version Increment
    # ===========================
    
    def test_version_increment(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test version number increments on commit."""
        draft_timeline.version_number = "1.0"
        db.commit()
        
        response = orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Check committed timeline has incremented version
        committed_id = UUID(response["committed_timeline"]["id"])
        committed = db.query(CommittedTimeline).get(committed_id)
        
        # Version should be incremented
        assert committed.version_number == "2.0"
    
    # ===========================
    # Test: Immutability
    # ===========================
    
    def test_draft_frozen_after_commit(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test draft is frozen after commit."""
        response = orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Refresh draft from DB
        db.refresh(draft_timeline)
        
        assert draft_timeline.is_active is False
        assert "COMMITTED" in draft_timeline.notes
    
    def test_cannot_edit_frozen_draft(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test editing frozen draft fails."""
        # Commit first
        orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Try to apply edits
        edits = [
            {
                "operation": "update",
                "entity_type": "timeline",
                "data": {"title": "Should Fail"}
            }
        ]
        
        with pytest.raises(TimelineImmutableError):
            orchestrator.apply_edits(
                draft_timeline_id=draft_timeline.id,
                user_id=orchestrator.user_id,
                edits=edits
            )
    
    def test_prevent_double_commit(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test committing same draft twice fails."""
        # First commit
        orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Second commit attempt (different request_id)
        with pytest.raises(TimelineAlreadyCommittedError):
            orchestrator.commit(
                request_id=str(uuid4()),  # Different ID
                draft_timeline_id=draft_timeline.id,
                user_id=orchestrator.user_id
            )
    
    # ===========================
    # Test: Idempotency
    # ===========================
    
    def test_commit_idempotency(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test same request_id returns cached response."""
        request_id = str(uuid4())
        
        # First commit
        response1 = orchestrator.commit(
            request_id=request_id,
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Second commit with same request_id
        response2 = orchestrator.commit(
            request_id=request_id,
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Should return same response
        assert response1["committed_timeline"]["id"] == response2["committed_timeline"]["id"]
        
        # Should only create one committed timeline
        count = db.query(CommittedTimeline).filter(
            CommittedTimeline.draft_timeline_id == draft_timeline.id
        ).count()
        assert count == 1
    
    # ===========================
    # Test: Apply Edits
    # ===========================
    
    def test_apply_timeline_edits(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline
    ):
        """Test editing timeline metadata."""
        edits = [
            {
                "operation": "update",
                "entity_type": "timeline",
                "data": {
                    "title": "Updated Title",
                    "description": "Updated Description"
                }
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify changes
        db.refresh(draft_timeline)
        assert draft_timeline.title == "Updated Title"
        assert draft_timeline.description == "Updated Description"
        
        # Verify edit history
        history = db.query(TimelineEditHistory).filter(
            TimelineEditHistory.draft_timeline_id == draft_timeline.id
        ).all()
        
        assert len(history) == 1
        assert history[0].edit_type == "modified"
        assert history[0].entity_type == "timeline"
        assert "title" in history[0].changes_json
    
    def test_apply_stage_edits(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test editing stage."""
        edits = [
            {
                "operation": "update",
                "entity_type": "stage",
                "entity_id": str(stage_with_milestones.id),
                "data": {
                    "duration_months": 9,
                    "status": "in_progress"
                }
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify changes
        db.refresh(stage_with_milestones)
        assert stage_with_milestones.duration_months == 9
        assert stage_with_milestones.status == "in_progress"
    
    def test_add_stage(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline
    ):
        """Test adding new stage."""
        edits = [
            {
                "operation": "add",
                "entity_type": "stage",
                "data": {
                    "title": "New Stage",
                    "description": "Additional phase",
                    "duration_months": 12
                }
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify stage created
        stages = db.query(TimelineStage).filter(
            TimelineStage.draft_timeline_id == draft_timeline.id
        ).all()
        
        assert len(stages) == 1
        assert stages[0].title == "New Stage"
    
    def test_delete_stage(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test deleting stage."""
        stage_id = stage_with_milestones.id
        
        edits = [
            {
                "operation": "delete",
                "entity_type": "stage",
                "entity_id": str(stage_id)
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify stage deleted
        stage = db.query(TimelineStage).get(stage_id)
        assert stage is None
    
    def test_add_milestone(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test adding milestone to stage."""
        edits = [
            {
                "operation": "add",
                "entity_type": "milestone",
                "data": {
                    "timeline_stage_id": str(stage_with_milestones.id),
                    "title": "New Milestone",
                    "description": "New deliverable",
                    "is_critical": True
                }
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify milestone created
        milestones = db.query(TimelineMilestone).filter(
            TimelineMilestone.timeline_stage_id == stage_with_milestones.id
        ).all()
        
        assert len(milestones) == 4  # 3 original + 1 new
        new_milestone = [m for m in milestones if m.title == "New Milestone"][0]
        assert new_milestone.is_critical is True
    
    def test_update_milestone(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test updating milestone."""
        milestone = db.query(TimelineMilestone).filter(
            TimelineMilestone.timeline_stage_id == stage_with_milestones.id
        ).first()
        
        edits = [
            {
                "operation": "update",
                "entity_type": "milestone",
                "entity_id": str(milestone.id),
                "data": {
                    "title": "Updated Milestone",
                    "is_critical": True,
                    "is_completed": True
                }
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify changes
        db.refresh(milestone)
        assert milestone.title == "Updated Milestone"
        assert milestone.is_critical is True
        assert milestone.is_completed is True
    
    def test_delete_milestone(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test deleting milestone."""
        milestone = db.query(TimelineMilestone).filter(
            TimelineMilestone.timeline_stage_id == stage_with_milestones.id
        ).first()
        milestone_id = milestone.id
        
        edits = [
            {
                "operation": "delete",
                "entity_type": "milestone",
                "entity_id": str(milestone_id)
            }
        ]
        
        result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert result["edits_applied"] == 1
        
        # Verify milestone deleted
        milestone = db.query(TimelineMilestone).get(milestone_id)
        assert milestone is None
    
    # ===========================
    # Test: Edit History
    # ===========================
    
    def test_edit_history_recording(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test all edits are recorded in history."""
        edits = [
            {
                "operation": "update",
                "entity_type": "timeline",
                "data": {"title": "New Title"}
            },
            {
                "operation": "update",
                "entity_type": "stage",
                "entity_id": str(stage_with_milestones.id),
                "data": {"duration_months": 12}
            },
            {
                "operation": "add",
                "entity_type": "milestone",
                "data": {
                    "timeline_stage_id": str(stage_with_milestones.id),
                    "title": "Added Milestone"
                }
            }
        ]
        
        orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        # Verify all edits recorded
        history = db.query(TimelineEditHistory).filter(
            TimelineEditHistory.draft_timeline_id == draft_timeline.id
        ).order_by(TimelineEditHistory.created_at).all()
        
        assert len(history) == 3
        assert history[0].entity_type == "timeline"
        assert history[1].entity_type == "stage"
        assert history[2].entity_type == "milestone"
        assert history[2].edit_type == "added"
    
    def test_edit_history_changes_json(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test changes_json captures before/after values."""
        edits = [
            {
                "operation": "update",
                "entity_type": "stage",
                "entity_id": str(stage_with_milestones.id),
                "data": {
                    "title": "Updated Stage Title",
                    "duration_months": 18
                }
            }
        ]
        
        orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        # Check changes_json
        history = db.query(TimelineEditHistory).filter(
            TimelineEditHistory.draft_timeline_id == draft_timeline.id
        ).first()
        
        changes = history.changes_json
        assert "title" in changes
        assert changes["title"]["before"] == "Literature Review"
        assert changes["title"]["after"] == "Updated Stage Title"
        assert "duration_months" in changes
        assert changes["duration_months"]["before"] == 6
        assert changes["duration_months"]["after"] == 18
    
    # ===========================
    # Test: Complete Workflow
    # ===========================
    
    def test_complete_edit_commit_workflow(
        self,
        db: Session,
        orchestrator: TimelineOrchestrator,
        draft_timeline: DraftTimeline,
        stage_with_milestones: TimelineStage
    ):
        """Test complete workflow: create → edit → commit."""
        # Step 1: Apply edits
        edits = [
            {
                "operation": "update",
                "entity_type": "timeline",
                "data": {"title": "Final Timeline"}
            },
            {
                "operation": "update",
                "entity_type": "stage",
                "entity_id": str(stage_with_milestones.id),
                "data": {"duration_months": 9}
            },
            {
                "operation": "add",
                "entity_type": "milestone",
                "data": {
                    "timeline_stage_id": str(stage_with_milestones.id),
                    "title": "Extra Milestone",
                    "is_critical": True
                }
            }
        ]
        
        edit_result = orchestrator.apply_edits(
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id,
            edits=edits
        )
        
        assert edit_result["edits_applied"] == 3
        
        # Step 2: Commit
        commit_response = orchestrator.commit(
            request_id=str(uuid4()),
            draft_timeline_id=draft_timeline.id,
            user_id=orchestrator.user_id
        )
        
        # Verify commit includes edit history
        assert commit_response["edit_history"]["total_edits"] == 3
        assert commit_response["edit_history"]["edit_types"]["added"] == 1
        assert commit_response["edit_history"]["edit_types"]["modified"] == 2
        
        # Verify draft frozen
        db.refresh(draft_timeline)
        assert draft_timeline.is_active is False
        
        # Verify committed timeline exists
        committed_id = UUID(commit_response["committed_timeline"]["id"])
        committed = db.query(CommittedTimeline).get(committed_id)
        assert committed is not None
        assert committed.title == "Final Timeline"
        
        # Verify stages/milestones copied
        committed_stages = db.query(TimelineStage).filter(
            TimelineStage.committed_timeline_id == committed_id
        ).all()
        assert len(committed_stages) == 1
        
        committed_milestones = db.query(TimelineMilestone).filter(
            TimelineMilestone.timeline_stage_id == committed_stages[0].id
        ).all()
        assert len(committed_milestones) == 4  # 3 original + 1 added
        
        # Verify edit history preserved
        history = db.query(TimelineEditHistory).filter(
            TimelineEditHistory.draft_timeline_id == draft_timeline.id
        ).all()
        assert len(history) == 3

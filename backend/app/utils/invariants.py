"""
System invariants and validation utilities.

Enforces critical system constraints:
1. No committed timeline without draft
2. No PhD Doctor score without submission
3. No progress event without committed milestone
4. No duplicate idempotent actions

Fail fast with clear errors.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime


class InvariantViolationError(Exception):
    """Base exception for invariant violations."""
    
    def __init__(self, invariant_name: str, message: str, details: dict = None):
        self.invariant_name = invariant_name
        self.details = details or {}
        super().__init__(f"[INVARIANT VIOLATION: {invariant_name}] {message}")


class CommittedTimelineWithoutDraftError(InvariantViolationError):
    """Raised when attempting to create CommittedTimeline without DraftTimeline."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("committed_timeline_without_draft", message, details)


class AssessmentWithoutSubmissionError(InvariantViolationError):
    """Raised when JourneyAssessment created without proper submission."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("assessment_without_submission", message, details)


class ProgressEventWithoutMilestoneError(InvariantViolationError):
    """Raised when ProgressEvent references non-existent milestone."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("progress_event_without_milestone", message, details)


class DuplicateIdempotentActionError(InvariantViolationError):
    """Raised when attempting duplicate idempotent action."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__("duplicate_idempotent_action", message, details)


class InvariantChecker:
    """
    Central invariant checker for system-wide validation.
    
    Usage:
        checker = InvariantChecker(db)
        checker.check_all(operation="commit_timeline", context={...})
    """
    
    def __init__(self, db: Session):
        """
        Initialize invariant checker.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def check_committed_timeline_has_draft(
        self,
        draft_timeline_id: Optional[UUID],
        user_id: UUID
    ) -> None:
        """
        Invariant: No committed timeline without draft.
        
        Every CommittedTimeline must originate from a DraftTimeline.
        This ensures proper workflow and auditability.
        
        Args:
            draft_timeline_id: Draft timeline ID
            user_id: User ID
            
        Raises:
            CommittedTimelineWithoutDraftError: If draft doesn't exist
        """
        if draft_timeline_id is None:
            raise CommittedTimelineWithoutDraftError(
                "Cannot commit timeline: no draft_timeline_id provided",
                details={
                    "user_id": str(user_id),
                    "draft_timeline_id": None
                }
            )
        
        from app.models.draft_timeline import DraftTimeline
        
        draft = self.db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id,
            DraftTimeline.user_id == user_id
        ).first()
        
        if not draft:
            raise CommittedTimelineWithoutDraftError(
                f"Cannot commit timeline: DraftTimeline {draft_timeline_id} not found or not owned by user {user_id}",
                details={
                    "user_id": str(user_id),
                    "draft_timeline_id": str(draft_timeline_id),
                    "exists": False
                }
            )
        
        # Check if draft is already committed
        from app.models.committed_timeline import CommittedTimeline
        
        existing_commit = self.db.query(CommittedTimeline).filter(
            CommittedTimeline.draft_timeline_id == draft_timeline_id
        ).first()
        
        if existing_commit:
            raise CommittedTimelineWithoutDraftError(
                f"Cannot commit timeline: DraftTimeline {draft_timeline_id} already committed as {existing_commit.id}",
                details={
                    "user_id": str(user_id),
                    "draft_timeline_id": str(draft_timeline_id),
                    "existing_committed_id": str(existing_commit.id),
                    "already_committed": True
                }
            )
    
    def check_assessment_has_submission(
        self,
        user_id: UUID,
        responses_count: int,
        is_explicit_submission: bool = True
    ) -> None:
        """
        Invariant: No PhD Doctor score without submission.
        
        JourneyAssessment records must only be created through explicit
        submission (via PhDDoctorOrchestrator.submit()), not directly.
        
        Args:
            user_id: User ID
            responses_count: Number of responses
            is_explicit_submission: Whether this is an explicit submission
            
        Raises:
            AssessmentWithoutSubmissionError: If not explicit submission
        """
        if not is_explicit_submission:
            raise AssessmentWithoutSubmissionError(
                "Cannot create JourneyAssessment: must use PhDDoctorOrchestrator.submit()",
                details={
                    "user_id": str(user_id),
                    "is_explicit_submission": False,
                    "hint": "Use PhDDoctorOrchestrator.submit() instead of creating JourneyAssessment directly"
                }
            )
        
        # Check minimum responses
        if responses_count < 5:
            raise AssessmentWithoutSubmissionError(
                f"Cannot create JourneyAssessment: insufficient responses (got {responses_count}, need at least 5)",
                details={
                    "user_id": str(user_id),
                    "responses_count": responses_count,
                    "minimum_required": 5
                }
            )
    
    def check_progress_event_has_milestone(
        self,
        milestone_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Invariant: No progress event without committed milestone.
        
        Every ProgressEvent must reference a valid milestone in a
        CommittedTimeline. This ensures progress tracking integrity.
        
        Args:
            milestone_id: Milestone ID
            user_id: User ID
            
        Raises:
            ProgressEventWithoutMilestoneError: If milestone doesn't exist
        """
        from app.models.timeline_milestone import TimelineMilestone
        from app.models.timeline_stage import TimelineStage
        from app.models.committed_timeline import CommittedTimeline
        
        # Check milestone exists
        milestone = self.db.query(TimelineMilestone).filter(
            TimelineMilestone.id == milestone_id
        ).first()
        
        if not milestone:
            raise ProgressEventWithoutMilestoneError(
                f"Cannot create ProgressEvent: TimelineMilestone {milestone_id} not found",
                details={
                    "user_id": str(user_id),
                    "milestone_id": str(milestone_id),
                    "exists": False
                }
            )
        
        # Check milestone belongs to a stage
        stage = self.db.query(TimelineStage).filter(
            TimelineStage.id == milestone.stage_id
        ).first()
        
        if not stage:
            raise ProgressEventWithoutMilestoneError(
                f"Cannot create ProgressEvent: Milestone {milestone_id} has no associated stage",
                details={
                    "user_id": str(user_id),
                    "milestone_id": str(milestone_id),
                    "stage_id": milestone.stage_id,
                    "stage_exists": False
                }
            )
        
        # Check stage belongs to a committed timeline
        if stage.committed_timeline_id:
            timeline = self.db.query(CommittedTimeline).filter(
                CommittedTimeline.id == stage.committed_timeline_id
            ).first()
        else:
            timeline = None
        
        if not timeline:
            raise ProgressEventWithoutMilestoneError(
                f"Cannot create ProgressEvent: Milestone {milestone_id} not in CommittedTimeline",
                details={
                    "user_id": str(user_id),
                    "milestone_id": str(milestone_id),
                    "stage_id": milestone.stage_id,
                    "committed_timeline_id": stage.committed_timeline_id,
                    "hint": "Progress can only be tracked on committed timelines"
                }
            )
        
        # Verify timeline belongs to user
        if timeline.user_id != user_id:
            raise ProgressEventWithoutMilestoneError(
                f"Cannot create ProgressEvent: Timeline {timeline.id} does not belong to user {user_id}",
                details={
                    "user_id": str(user_id),
                    "milestone_id": str(milestone_id),
                    "timeline_user_id": str(timeline.user_id),
                    "ownership_mismatch": True
                }
            )
    
    def check_idempotency_key_unique(
        self,
        key: str,
        orchestrator_name: str,
        allow_completed: bool = True
    ) -> Optional[dict]:
        """
        Invariant: No duplicate idempotent actions.
        
        Idempotency keys must be unique per orchestrator to prevent
        duplicate execution. Returns existing result if key exists and completed.
        
        Args:
            key: Idempotency key
            orchestrator_name: Orchestrator name
            allow_completed: If True, return cached result for completed operations
            
        Returns:
            Cached result if key exists and completed, None otherwise
            
        Raises:
            DuplicateIdempotentActionError: If key exists but not completed
        """
        from app.models.idempotency import IdempotencyKey
        
        existing = self.db.query(IdempotencyKey).filter(
            IdempotencyKey.key == key,
            IdempotencyKey.orchestrator_name == orchestrator_name
        ).first()
        
        if not existing:
            return None
        
        # If completed and allowed, return cached result
        if existing.status == "COMPLETED" and allow_completed:
            return existing.result_data
        
        # If in progress, fail
        if existing.status == "IN_PROGRESS":
            raise DuplicateIdempotentActionError(
                f"Operation with key '{key}' is already in progress",
                details={
                    "key": key,
                    "orchestrator_name": orchestrator_name,
                    "status": existing.status,
                    "started_at": existing.created_at.isoformat() if existing.created_at else None,
                    "hint": "Wait for operation to complete or use a different request_id"
                }
            )
        
        # If failed, allow retry with same key
        if existing.status == "FAILED":
            # Delete failed attempt to allow retry
            self.db.delete(existing)
            self.db.flush()
            return None
        
        # Other statuses - treat as error
        raise DuplicateIdempotentActionError(
            f"Operation with key '{key}' exists with unexpected status: {existing.status}",
            details={
                "key": key,
                "orchestrator_name": orchestrator_name,
                "status": existing.status
            }
        )
    
    def check_all(
        self,
        operation: str,
        context: dict
    ) -> None:
        """
        Check all relevant invariants for an operation.
        
        Args:
            operation: Operation name (e.g., "commit_timeline", "create_assessment")
            context: Operation context with required fields
            
        Raises:
            InvariantViolationError: If any invariant is violated
        """
        if operation == "commit_timeline":
            self.check_committed_timeline_has_draft(
                draft_timeline_id=context.get("draft_timeline_id"),
                user_id=context["user_id"]
            )
        
        elif operation == "create_assessment":
            self.check_assessment_has_submission(
                user_id=context["user_id"],
                responses_count=context.get("responses_count", 0),
                is_explicit_submission=context.get("is_explicit_submission", False)
            )
        
        elif operation == "create_progress_event":
            self.check_progress_event_has_milestone(
                milestone_id=context["milestone_id"],
                user_id=context["user_id"]
            )
        
        elif operation == "check_idempotency":
            result = self.check_idempotency_key_unique(
                key=context["key"],
                orchestrator_name=context["orchestrator_name"],
                allow_completed=context.get("allow_completed", True)
            )
            return result
        
        else:
            # Unknown operation - no checks
            pass


# Convenience functions for direct usage

def check_committed_timeline_has_draft(
    db: Session,
    draft_timeline_id: Optional[UUID],
    user_id: UUID
) -> None:
    """Check committed timeline has draft invariant."""
    checker = InvariantChecker(db)
    checker.check_committed_timeline_has_draft(draft_timeline_id, user_id)


def check_assessment_has_submission(
    db: Session,
    user_id: UUID,
    responses_count: int,
    is_explicit_submission: bool = True
) -> None:
    """Check assessment has submission invariant."""
    checker = InvariantChecker(db)
    checker.check_assessment_has_submission(user_id, responses_count, is_explicit_submission)


def check_progress_event_has_milestone(
    db: Session,
    milestone_id: UUID,
    user_id: UUID
) -> None:
    """Check progress event has milestone invariant."""
    checker = InvariantChecker(db)
    checker.check_progress_event_has_milestone(milestone_id, user_id)


def check_idempotency_key_unique(
    db: Session,
    key: str,
    orchestrator_name: str,
    allow_completed: bool = True
) -> Optional[dict]:
    """Check idempotency key unique invariant."""
    checker = InvariantChecker(db)
    return checker.check_idempotency_key_unique(key, orchestrator_name, allow_completed)

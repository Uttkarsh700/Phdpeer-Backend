"""Timeline repository."""
from uuid import UUID

from app.models.baseline import Baseline
from app.models.committed_timeline import CommittedTimeline
from app.models.document_artifact import DocumentArtifact
from app.models.draft_timeline import DraftTimeline
from app.models.timeline_milestone import TimelineMilestone
from app.models.timeline_stage import TimelineStage
from app.repositories.base import BaseRepository


class TimelineRepository(BaseRepository):
    """Data access for timeline aggregates."""

    def get_baseline_for_user(self, baseline_id: UUID, user_id: UUID) -> Baseline | None:
        return self.db.query(Baseline).filter(
            Baseline.id == baseline_id,
            Baseline.user_id == user_id,
        ).first()

    def get_document_artifact(self, document_artifact_id: UUID) -> DocumentArtifact | None:
        return self.db.query(DocumentArtifact).filter(
            DocumentArtifact.id == document_artifact_id,
        ).first()

    def get_committed_timeline_for_user(
        self,
        timeline_id: UUID,
        user_id: UUID,
    ) -> CommittedTimeline | None:
        return self.db.query(CommittedTimeline).filter(
            CommittedTimeline.id == timeline_id,
            CommittedTimeline.user_id == user_id,
        ).first()

    def get_latest_committed_timeline_for_user(self, user_id: UUID) -> CommittedTimeline | None:
        return self.db.query(CommittedTimeline).filter(
            CommittedTimeline.user_id == user_id,
        ).order_by(CommittedTimeline.committed_date.desc()).first()

    def get_draft_timeline_by_id(self, draft_timeline_id: UUID) -> DraftTimeline | None:
        return self.db.query(DraftTimeline).filter(
            DraftTimeline.id == draft_timeline_id,
        ).first()

    def create_draft_timeline(
        self,
        user_id: UUID,
        baseline_id: UUID,
        title: str,
        description: str,
        version_number: str,
        notes: str,
    ) -> DraftTimeline:
        draft = DraftTimeline(
            user_id=user_id,
            baseline_id=baseline_id,
            title=title,
            description=description,
            version_number=version_number,
            is_active=True,
            notes=notes,
        )
        self.add(draft)
        self.flush()
        return draft

    def create_stage(
        self,
        draft_timeline_id: UUID,
        title: str,
        description: str,
        stage_order: int,
        duration_months: int,
        status: str,
        notes: str,
    ) -> TimelineStage:
        stage = TimelineStage(
            draft_timeline_id=draft_timeline_id,
            title=title,
            description=description,
            stage_order=stage_order,
            duration_months=duration_months,
            status=status,
            notes=notes,
        )
        self.add(stage)
        self.flush()
        return stage

    def create_milestone(
        self,
        timeline_stage_id: UUID,
        title: str,
        description: str,
        milestone_order: int,
        is_critical: bool,
        deliverable_type: str,
        notes: str,
    ) -> TimelineMilestone:
        milestone = TimelineMilestone(
            timeline_stage_id=timeline_stage_id,
            title=title,
            description=description,
            milestone_order=milestone_order,
            is_critical=is_critical,
            is_completed=False,
            deliverable_type=deliverable_type,
            notes=notes,
        )
        self.add(milestone)
        self.flush()
        return milestone

    def list_stages_for_draft_timeline(self, draft_timeline_id: UUID) -> list[TimelineStage]:
        return self.db.query(TimelineStage).filter(
            TimelineStage.draft_timeline_id == draft_timeline_id,
        ).order_by(TimelineStage.stage_order.asc()).all()

    def get_stages_for_committed_timeline(self, committed_timeline_id: UUID) -> list[TimelineStage]:
        return self.db.query(TimelineStage).filter(
            TimelineStage.committed_timeline_id == committed_timeline_id,
        ).order_by(TimelineStage.stage_order.asc()).all()

    def get_milestones_for_stage_ids(
        self,
        stage_ids: list[UUID],
        only_incomplete: bool = False,
        limit: int | None = None,
    ) -> list[TimelineMilestone]:
        if not stage_ids:
            return []

        query = self.db.query(TimelineMilestone).filter(
            TimelineMilestone.timeline_stage_id.in_(stage_ids),
        )

        if only_incomplete:
            query = query.filter(TimelineMilestone.is_completed.is_(False))

        query = query.order_by(
            TimelineMilestone.target_date.asc(),
            TimelineMilestone.milestone_order.asc(),
        )

        if limit:
            query = query.limit(limit)

        return query.all()

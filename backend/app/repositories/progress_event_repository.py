"""Progress event repository."""
from uuid import UUID

from app.models.progress_event import ProgressEvent
from app.repositories.base import BaseRepository


class ProgressEventRepository(BaseRepository):
    """Data access for ProgressEvent entities."""

    def list_by_user_and_milestone_ids(
        self,
        user_id: UUID,
        milestone_ids: list[UUID],
    ) -> list[ProgressEvent]:
        if not milestone_ids:
            return []
        return self.db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id,
            ProgressEvent.milestone_id.in_(milestone_ids),
        ).order_by(ProgressEvent.event_date.asc()).all()

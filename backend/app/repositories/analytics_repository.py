"""Analytics repository."""
from uuid import UUID

from app.models.analytics_snapshot import AnalyticsSnapshot
from app.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository):
    """Data access for analytics snapshots."""

    def get_latest_snapshot_for_user_and_version(
        self,
        user_id: UUID,
        timeline_version: str,
    ) -> AnalyticsSnapshot | None:
        return self.db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.user_id == user_id,
            AnalyticsSnapshot.timeline_version == timeline_version,
        ).order_by(AnalyticsSnapshot.created_at.desc()).first()

    def create_snapshot(
        self,
        user_id: UUID,
        timeline_version: str,
        summary_json: dict,
    ) -> AnalyticsSnapshot:
        snapshot = AnalyticsSnapshot(
            user_id=user_id,
            timeline_version=timeline_version,
            summary_json=summary_json,
        )
        self.add(snapshot)
        self.flush()
        self.refresh(snapshot)
        return snapshot

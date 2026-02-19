"""Opportunity repository."""
from datetime import date
from typing import Any
from uuid import UUID

from app.models.opportunity import (
    OpportunityCatalog,
    OpportunityFeedSnapshot,
    OpportunityFeedItem,
)
from app.repositories.base import BaseRepository


class OpportunityRepository(BaseRepository):
    """Data access for opportunity catalog and feed artifacts."""

    def get_catalog_by_opportunity_id(self, opportunity_id: str) -> OpportunityCatalog | None:
        return self.db.query(OpportunityCatalog).filter(
            OpportunityCatalog.opportunity_id == opportunity_id,
        ).first()

    def create_catalog_entry(self, catalog_entry_data: dict[str, Any]) -> OpportunityCatalog:
        catalog_entry = OpportunityCatalog(
            opportunity_id=catalog_entry_data["opportunity_id"],
            title=catalog_entry_data["title"],
            opportunity_type=catalog_entry_data["opportunity_type"],
            disciplines=catalog_entry_data["disciplines"],
            eligible_stages=catalog_entry_data["eligible_stages"],
            deadline=catalog_entry_data["deadline"],
            description=catalog_entry_data.get("description"),
            keywords=catalog_entry_data.get("keywords", []),
            funding_amount=catalog_entry_data.get("funding_amount"),
            prestige_level=catalog_entry_data.get("prestige_level"),
            geographic_scope=catalog_entry_data.get("geographic_scope"),
            source_url=catalog_entry_data.get("source_url"),
            organization=catalog_entry_data.get("organization"),
            is_active=True,
            requires_subscription=catalog_entry_data.get("requires_subscription", False),
            subscription_tier=catalog_entry_data.get("subscription_tier"),
        )
        self.add(catalog_entry)
        self.flush()
        return catalog_entry

    def create_feed_snapshot(
        self,
        user_id: UUID,
        user_profile_snapshot: dict[str, Any],
        timeline_context_snapshot: dict[str, Any] | None,
        total_opportunities_scored: int,
        feed_type: str,
        subscription_tier: str | None,
    ) -> OpportunityFeedSnapshot:
        snapshot = OpportunityFeedSnapshot(
            user_id=user_id,
            snapshot_date=date.today(),
            user_profile_snapshot=user_profile_snapshot,
            timeline_context_snapshot=timeline_context_snapshot,
            total_opportunities_scored=total_opportunities_scored,
            feed_type=feed_type,
            subscription_tier=subscription_tier,
        )
        self.add(snapshot)
        self.flush()
        return snapshot

    def add_feed_item(
        self,
        feed_snapshot_id: UUID,
        opportunity_catalog_id: UUID,
        rank: int,
        score: Any,
    ) -> OpportunityFeedItem:
        feed_item = OpportunityFeedItem(
            feed_snapshot_id=feed_snapshot_id,
            opportunity_id=opportunity_catalog_id,
            rank=rank,
            overall_score=score.overall_score,
            discipline_score=score.discipline_score,
            stage_score=score.stage_score,
            timeline_score=score.timeline_score,
            deadline_score=score.deadline_score,
            reason_tags=[tag.value for tag in score.reason_tags],
            explanation=score.explanation,
            urgency_level=score.urgency_level,
            recommended_action=score.recommended_action,
        )
        self.add(feed_item)
        return feed_item

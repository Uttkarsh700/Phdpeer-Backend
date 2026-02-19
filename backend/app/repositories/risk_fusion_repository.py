"""Repository for risk fusion config and persisted assessments."""
from uuid import UUID

from app.models.risk_fusion import RiskAssessmentSnapshot, RiskWeightConfig
from app.repositories.base import BaseRepository


class RiskFusionRepository(BaseRepository):
    """Data access for risk fusion configuration and score snapshots."""

    def get_active_config(self) -> RiskWeightConfig | None:
        return self.db.query(RiskWeightConfig).filter(
            RiskWeightConfig.is_active.is_(True)
        ).order_by(RiskWeightConfig.created_at.desc()).first()

    def create_risk_assessment(
        self,
        user_id: UUID,
        timeline_id: UUID | None,
        scoring_version: str,
        config_version: str,
        composite_score: float,
        risk_level: str,
        contributing_signals: list[dict],
        threshold_breaches: list[dict],
        weight_snapshot: dict,
        input_snapshot: dict,
    ) -> RiskAssessmentSnapshot:
        snapshot = RiskAssessmentSnapshot(
            user_id=user_id,
            timeline_id=timeline_id,
            scoring_version=scoring_version,
            config_version=config_version,
            composite_score=composite_score,
            risk_level=risk_level,
            contributing_signals=contributing_signals,
            threshold_breaches=threshold_breaches,
            weight_snapshot=weight_snapshot,
            input_snapshot=input_snapshot,
        )
        self.add(snapshot)
        self.flush()
        self.refresh(snapshot)
        return snapshot

"""Runtime scoring configuration resolver."""
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.scoring_config_repository import ScoringConfigRepository


@dataclass
class ResolvedScoringConfig:
    """Resolved config payload used by scoring engines."""

    version: str
    weights: dict[str, float]
    thresholds: dict[str, float]


class ScoringConfigService:
    """Resolve active scoring config from DB with default fallback."""

    def __init__(self, db: Session):
        self.repository = ScoringConfigRepository(db)

    def resolve(
        self,
        engine_name: str,
        default_version: str,
        default_weights: dict[str, float],
        default_thresholds: dict[str, float] | None = None,
    ) -> ResolvedScoringConfig:
        default_thresholds = default_thresholds or {}
        active = self.repository.get_active_config(engine_name)
        if not active:
            return ResolvedScoringConfig(
                version=default_version,
                weights=dict(default_weights),
                thresholds=dict(default_thresholds),
            )

        weights = dict(default_weights)
        thresholds = dict(default_thresholds)

        if isinstance(active.weights_json, dict):
            weights.update({k: float(v) for k, v in active.weights_json.items()})
        if isinstance(active.thresholds_json, dict):
            thresholds.update({k: float(v) for k, v in active.thresholds_json.items()})

        return ResolvedScoringConfig(
            version=active.version,
            weights=weights,
            thresholds=thresholds,
        )

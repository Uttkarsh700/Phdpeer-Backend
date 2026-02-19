"""Composite risk fusion engine with configurable/versioned weights."""
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.risk_fusion_repository import RiskFusionRepository


@dataclass
class RiskInput:
    """Structured inputs used by the risk fusion model."""

    timeline_status: str
    health_score: float
    overdue_ratio: float
    supervision_latency: float


@dataclass
class RiskOutput:
    """Composite risk output with explainability artifacts."""

    scoring_version: str
    composite_score: float
    risk_level: str
    contributing_signals: list[dict[str, Any]]
    threshold_breaches: list[dict[str, Any]]
    weight_snapshot: dict[str, Any]


@dataclass
class RiskConfigSnapshot:
    """Active risk weight + threshold configuration snapshot."""

    version: str
    weights: dict[str, float]
    thresholds: dict[str, float]


class RiskFusionEngine:
    """Deterministic risk fusion model for dropout/continuity risk scoring."""

    DEFAULT_VERSION = "risk_fusion_v1"
    DEFAULT_WEIGHTS = {
        "timeline_status": 0.35,
        "health_score": 0.30,
        "overdue_ratio": 0.20,
        "supervision_latency": 0.15,
    }
    DEFAULT_THRESHOLDS = {
        "overdue_ratio_delayed": 0.20,
        "health_low": 50.0,
        "supervision_latency_high": 30.0,
        "risk_level_medium": 45.0,
        "risk_level_high": 70.0,
        "supervision_latency_max": 60.0,
    }
    STATUS_RISK_SCORE = {
        "completed": 5.0,
        "on_track": 20.0,
        "delayed": 75.0,
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = RiskFusionRepository(db)

    @classmethod
    def get_overdue_ratio_delayed_threshold(cls, db: Session) -> float:
        """Central threshold accessor used across services to avoid duplication."""
        repository = RiskFusionRepository(db)
        active = repository.get_active_config()
        if active and isinstance(active.thresholds_json, dict):
            return float(
                active.thresholds_json.get(
                    "overdue_ratio_delayed", cls.DEFAULT_THRESHOLDS["overdue_ratio_delayed"]
                )
            )
        return cls.DEFAULT_THRESHOLDS["overdue_ratio_delayed"]

    def compute(self, risk_input: RiskInput) -> RiskOutput:
        """Compute composite risk using active versioned config."""
        config = self._get_active_config()

        normalized = {
            "timeline_status": self._score_timeline_status(risk_input.timeline_status),
            "health_score": self._score_health(risk_input.health_score),
            "overdue_ratio": self._score_overdue_ratio(risk_input.overdue_ratio),
            "supervision_latency": self._score_supervision_latency(
                risk_input.supervision_latency,
                max_latency_days=config.thresholds.get(
                    "supervision_latency_max",
                    self.DEFAULT_THRESHOLDS["supervision_latency_max"],
                ),
            ),
        }

        composite_score = 0.0
        contributions: list[dict[str, Any]] = []
        for signal, signal_score in normalized.items():
            weight = float(config.weights.get(signal, 0.0))
            weighted_component = signal_score * weight
            composite_score += weighted_component
            contributions.append(
                {
                    "signal": signal,
                    "raw_score": round(signal_score, 2),
                    "weight": weight,
                    "weighted_contribution": round(weighted_component, 2),
                }
            )

        composite_score = max(0.0, min(100.0, round(composite_score, 2)))
        risk_level = self._derive_risk_level(composite_score, config.thresholds)
        threshold_breaches = self._compute_threshold_breaches(risk_input, config.thresholds)

        return RiskOutput(
            scoring_version=config.version,
            composite_score=composite_score,
            risk_level=risk_level,
            contributing_signals=sorted(
                contributions,
                key=lambda x: x["weighted_contribution"],
                reverse=True,
            ),
            threshold_breaches=threshold_breaches,
            weight_snapshot={
                "version": config.version,
                "weights": config.weights,
                "thresholds": config.thresholds,
            },
        )

    def persist(
        self,
        user_id: UUID,
        timeline_id: UUID | None,
        risk_input: RiskInput,
        risk_output: RiskOutput,
    ) -> UUID:
        """Persist risk output and return snapshot id."""
        snapshot = self.repository.create_risk_assessment(
            user_id=user_id,
            timeline_id=timeline_id,
            scoring_version=risk_output.scoring_version,
            config_version=str(risk_output.weight_snapshot.get("version", self.DEFAULT_VERSION)),
            composite_score=risk_output.composite_score,
            risk_level=risk_output.risk_level,
            contributing_signals=risk_output.contributing_signals,
            threshold_breaches=risk_output.threshold_breaches,
            weight_snapshot=risk_output.weight_snapshot,
            input_snapshot=asdict(risk_input),
        )
        return snapshot.id

    def _get_active_config(self) -> RiskConfigSnapshot:
        active = self.repository.get_active_config()
        if not active:
            return RiskConfigSnapshot(
                version=self.DEFAULT_VERSION,
                weights=dict(self.DEFAULT_WEIGHTS),
                thresholds=dict(self.DEFAULT_THRESHOLDS),
            )

        weights = dict(self.DEFAULT_WEIGHTS)
        thresholds = dict(self.DEFAULT_THRESHOLDS)

        if isinstance(active.weights_json, dict):
            weights.update({k: float(v) for k, v in active.weights_json.items()})
        if isinstance(active.thresholds_json, dict):
            thresholds.update({k: float(v) for k, v in active.thresholds_json.items()})

        return RiskConfigSnapshot(
            version=active.version,
            weights=weights,
            thresholds=thresholds,
        )

    def _derive_risk_level(self, composite_score: float, thresholds: dict[str, float]) -> str:
        high = thresholds.get("risk_level_high", self.DEFAULT_THRESHOLDS["risk_level_high"])
        medium = thresholds.get("risk_level_medium", self.DEFAULT_THRESHOLDS["risk_level_medium"])
        if composite_score >= high:
            return "high"
        if composite_score >= medium:
            return "medium"
        return "low"

    def _compute_threshold_breaches(
        self,
        risk_input: RiskInput,
        thresholds: dict[str, float],
    ) -> list[dict[str, Any]]:
        overdue_threshold = thresholds.get(
            "overdue_ratio_delayed", self.DEFAULT_THRESHOLDS["overdue_ratio_delayed"]
        )
        health_threshold = thresholds.get("health_low", self.DEFAULT_THRESHOLDS["health_low"])
        supervision_threshold = thresholds.get(
            "supervision_latency_high", self.DEFAULT_THRESHOLDS["supervision_latency_high"]
        )

        return [
            {
                "name": "timeline_delayed",
                "breached": risk_input.timeline_status == "delayed",
                "value": risk_input.timeline_status,
            },
            {
                "name": "overdue_ratio_delayed",
                "breached": risk_input.overdue_ratio > overdue_threshold,
                "value": risk_input.overdue_ratio,
                "threshold": overdue_threshold,
            },
            {
                "name": "health_low",
                "breached": risk_input.health_score < health_threshold,
                "value": risk_input.health_score,
                "threshold": health_threshold,
            },
            {
                "name": "supervision_latency_high",
                "breached": risk_input.supervision_latency > supervision_threshold,
                "value": risk_input.supervision_latency,
                "threshold": supervision_threshold,
            },
        ]

    def _score_timeline_status(self, timeline_status: str) -> float:
        return float(self.STATUS_RISK_SCORE.get(timeline_status, 35.0))

    def _score_health(self, health_score: float) -> float:
        bounded = max(0.0, min(100.0, float(health_score)))
        return 100.0 - bounded

    def _score_overdue_ratio(self, overdue_ratio: float) -> float:
        bounded = max(0.0, min(1.0, float(overdue_ratio)))
        return bounded * 100.0

    def _score_supervision_latency(self, latency_days: float, max_latency_days: float) -> float:
        safe_max = max(1.0, float(max_latency_days))
        bounded = max(0.0, min(float(latency_days), safe_max))
        return (bounded / safe_max) * 100.0

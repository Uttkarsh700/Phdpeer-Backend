"""Repository for generic scoring configuration retrieval."""
from app.models.scoring_config import ScoringConfig
from app.repositories.base import BaseRepository


class ScoringConfigRepository(BaseRepository):
    """Data access for runtime scoring configuration."""

    def get_active_config(self, engine_name: str) -> ScoringConfig | None:
        return self.db.query(ScoringConfig).filter(
            ScoringConfig.engine_name == engine_name,
            ScoringConfig.is_active.is_(True),
        ).order_by(ScoringConfig.created_at.desc()).first()

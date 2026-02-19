"""Assessment repository."""
from uuid import UUID

from app.models.journey_assessment import JourneyAssessment
from app.repositories.base import BaseRepository


class AssessmentRepository(BaseRepository):
    """Data access for JourneyAssessment entities."""

    def get_latest_for_user(self, user_id: UUID) -> JourneyAssessment | None:
        return self.db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == user_id,
        ).order_by(JourneyAssessment.assessment_date.desc()).first()

"""Privacy Engine for data isolation, anonymization, and GDPR compliance.

This module provides tenant isolation, data anonymization, consent handling,
and GDPR-compliant data portability and deletion.
"""
import hashlib
import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document_artifact import DocumentArtifact
from app.models.draft_timeline import DraftTimeline
from app.models.committed_timeline import CommittedTimeline
from app.models.timeline_stage import TimelineStage
from app.models.timeline_milestone import TimelineMilestone
from app.models.progress_event import ProgressEvent
from app.models.journey_assessment import JourneyAssessment
from app.models.feedback_record import FeedbackRecord
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.questionnaire_draft import QuestionnaireDraft
from app.services.audit_logger import AuditLogger


logger = logging.getLogger(__name__)


class PrivacyEngineError(Exception):
    """Base exception for privacy engine errors."""
    pass


class TenantIsolationError(PrivacyEngineError):
    """Raised when tenant isolation is violated."""
    pass


class PrivacyEngine:
    """
    Engine for privacy controls and data isolation.

    Capabilities:
    - Tenant isolation enforcement
    - Data anonymization for aggregation
    - Consent revocation handling
    - GDPR data deletion
    - GDPR data export (portability)
    - Role-based field filtering

    Roles:
    - student: Can access only their own data
    - supervisor: Can access their students' progress (not health details)
    - admin: Can access anonymized aggregate data
    - institution: Can access only aggregate statistics
    """

    # Role hierarchy
    ROLE_STUDENT = "student"
    ROLE_SUPERVISOR = "supervisor"
    ROLE_ADMIN = "admin"
    ROLE_INSTITUTION = "institution"
    ROLE_SYSTEM = "system"

    VALID_ROLES = [
        ROLE_STUDENT,
        ROLE_SUPERVISOR,
        ROLE_ADMIN,
        ROLE_INSTITUTION,
        ROLE_SYSTEM,
    ]

    # Default fields to anonymize
    DEFAULT_ANONYMIZE_FIELDS = [
        "user_id",
        "email",
        "full_name",
        "supervisor_name",
        "supervisor_names",
        "institution",
        "institution_name",
        "advisor_feedback",
        "ip_address",
    ]

    # Sensitive fields by role
    SENSITIVE_FIELDS_BY_ROLE = {
        ROLE_STUDENT: set(),  # Students can see all their own data
        ROLE_SUPERVISOR: {
            "hashed_password",
            "ip_address",
            "user_agent",
            # Health details supervisors shouldn't see
            "mental_health_score",
            "stress_level",
            "personal_notes",
        },
        ROLE_ADMIN: {
            "hashed_password",
            "email",
            "full_name",
            "ip_address",
            "user_agent",
            "advisor_feedback",
            "personal_notes",
        },
        ROLE_INSTITUTION: {
            "hashed_password",
            "email",
            "full_name",
            "user_id",
            "ip_address",
            "user_agent",
            "advisor_feedback",
            "personal_notes",
            "strengths",
            "challenges",
            "action_items",
            "notes",
        },
    }

    def __init__(self, db: Session):
        """
        Initialize privacy engine.

        Args:
            db: Database session
        """
        self.db = db
        self.audit_logger = AuditLogger(db)

    def enforce_tenant_isolation(
        self,
        user_id: UUID,
        resource_user_id: UUID,
        role: str = ROLE_STUDENT,
        resource_type: str = "data",
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Check if a user has permission to access another user's data.

        Returns True if:
        - Same user (user_id == resource_user_id)
        - Requester is a supervisor/admin linked to that user
        - Requester is system role

        Args:
            user_id: ID of the requesting user
            resource_user_id: ID of the user whose data is being accessed
            role: Role of the requesting user
            resource_type: Type of resource being accessed
            ip_address: IP address for audit logging

        Returns:
            True if access is permitted

        Raises:
            TenantIsolationError: If access is not permitted
        """
        # System role has full access
        if role == self.ROLE_SYSTEM:
            return True

        # Same user always has access to their own data
        if user_id == resource_user_id:
            return True

        # Check if requester is a valid supervisor/admin
        if role == self.ROLE_SUPERVISOR:
            if self._is_supervisor_of(user_id, resource_user_id):
                # Log the access
                self.audit_logger.log_access(
                    user_id=user_id,
                    resource_type=resource_type,
                    action="access",
                    target_user_id=resource_user_id,
                    ip_address=ip_address,
                    reason=f"Supervisor access to student data",
                )
                return True

        if role == self.ROLE_ADMIN:
            # Admins can access user data for support/management
            # but only if they are superusers
            admin = self.db.query(User).filter(User.id == user_id).first()
            if admin and admin.is_superuser:
                self.audit_logger.log_access(
                    user_id=user_id,
                    resource_type=resource_type,
                    action="access",
                    target_user_id=resource_user_id,
                    ip_address=ip_address,
                    reason="Admin access to user data",
                )
                return True

        # Access denied - log and raise
        self.audit_logger.log_permission_denied(
            user_id=user_id,
            resource_type=resource_type,
            target_user_id=resource_user_id,
            ip_address=ip_address,
            reason=f"User {user_id} with role {role} denied access to user {resource_user_id}",
        )

        raise TenantIsolationError(
            f"User {user_id} does not have permission to access data for user {resource_user_id}"
        )

    def anonymize_for_aggregation(
        self,
        data: Dict[str, Any],
        fields_to_anonymize: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Strip PII from data before institution-level aggregation.

        Replaces identifiable information with anonymous identifiers.

        Args:
            data: Dictionary containing data to anonymize
            fields_to_anonymize: List of field names to anonymize.
                                 Defaults to DEFAULT_ANONYMIZE_FIELDS.

        Returns:
            Anonymized copy of the data
        """
        if fields_to_anonymize is None:
            fields_to_anonymize = self.DEFAULT_ANONYMIZE_FIELDS

        result = deepcopy(data)
        self._anonymize_dict(result, set(fields_to_anonymize))
        return result

    def handle_consent_revocation(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handle consent revocation by anonymizing/deleting user data.

        Does NOT delete the user account itself - only their associated data.

        Args:
            user_id: ID of user revoking consent
            ip_address: IP address for audit logging

        Returns:
            Summary of what was deleted/anonymized
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise PrivacyEngineError(f"User {user_id} not found")

        summary = {
            "user_id": str(user_id),
            "action": "consent_revocation",
            "deleted": {},
            "anonymized": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Delete FeedbackRecords
            feedback_count = self.db.query(FeedbackRecord).filter(
                FeedbackRecord.user_id == user_id
            ).delete()
            summary["deleted"]["feedback_records"] = feedback_count

            # Delete ProgressEvents
            progress_count = self.db.query(ProgressEvent).filter(
                ProgressEvent.user_id == user_id
            ).delete()
            summary["deleted"]["progress_events"] = progress_count

            # Delete AnalyticsSnapshots
            analytics_count = self.db.query(AnalyticsSnapshot).filter(
                AnalyticsSnapshot.user_id == user_id
            ).delete()
            summary["deleted"]["analytics_snapshots"] = analytics_count

            # Anonymize JourneyAssessments (keep for research, remove PII)
            assessments = self.db.query(JourneyAssessment).filter(
                JourneyAssessment.user_id == user_id
            ).all()
            for assessment in assessments:
                assessment.strengths = "[REDACTED]"
                assessment.challenges = "[REDACTED]"
                assessment.action_items = "[REDACTED]"
                assessment.advisor_feedback = "[REDACTED]"
                assessment.notes = "[REDACTED]"
                self.db.add(assessment)
            summary["anonymized"]["journey_assessments"] = len(assessments)

            # Mark DocumentArtifacts for deletion (don't delete immediately)
            docs = self.db.query(DocumentArtifact).filter(
                DocumentArtifact.user_id == user_id
            ).all()
            for doc in docs:
                doc.raw_text = "[CONSENT_REVOKED]"
                doc.document_text = "[CONSENT_REVOKED]"
                doc.document_metadata = {"consent_revoked": True}
                self.db.add(doc)
            summary["anonymized"]["document_artifacts"] = len(docs)

            # Delete QuestionnaireDrafts
            draft_count = self.db.query(QuestionnaireDraft).filter(
                QuestionnaireDraft.user_id == user_id
            ).delete()
            summary["deleted"]["questionnaire_drafts"] = draft_count

            self.db.commit()

            # Log the consent revocation
            self.audit_logger.log_consent_revocation(
                user_id=user_id,
                ip_address=ip_address,
                changes=summary,
            )

            logger.info(f"Consent revocation completed for user {user_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Consent revocation failed for user {user_id}: {e}")
            raise PrivacyEngineError(f"Consent revocation failed: {e}") from e

        return summary

    def handle_data_deletion_request(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        requesting_user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        GDPR-style full data deletion.

        Removes all user data across all tables and returns a deletion receipt.

        Args:
            user_id: ID of user whose data should be deleted
            ip_address: IP address for audit logging
            requesting_user_id: Who requested the deletion (for admin deletions)

        Returns:
            Deletion receipt with counts of deleted records per table
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise PrivacyEngineError(f"User {user_id} not found")

        receipt = {
            "user_id": str(user_id),
            "action": "data_deletion",
            "deleted_counts": {},
            "timestamp": datetime.utcnow().isoformat(),
            "retention_note": "Audit logs are retained for compliance",
        }

        try:
            # Delete in order respecting foreign key constraints
            # (or rely on CASCADE if configured)

            # Delete FeedbackRecords
            feedback_count = self.db.query(FeedbackRecord).filter(
                FeedbackRecord.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["feedback_records"] = feedback_count

            # Delete ProgressEvents
            progress_count = self.db.query(ProgressEvent).filter(
                ProgressEvent.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["progress_events"] = progress_count

            # Delete AnalyticsSnapshots
            analytics_count = self.db.query(AnalyticsSnapshot).filter(
                AnalyticsSnapshot.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["analytics_snapshots"] = analytics_count

            # Delete JourneyAssessments
            assessment_count = self.db.query(JourneyAssessment).filter(
                JourneyAssessment.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["journey_assessments"] = assessment_count

            # Delete QuestionnaireDrafts
            draft_count = self.db.query(QuestionnaireDraft).filter(
                QuestionnaireDraft.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["questionnaire_drafts"] = draft_count

            # Delete timeline-related data
            # Get committed timelines first
            committed_timelines = self.db.query(CommittedTimeline).filter(
                CommittedTimeline.user_id == user_id
            ).all()

            milestone_count = 0
            stage_count = 0
            for timeline in committed_timelines:
                stages = self.db.query(TimelineStage).filter(
                    TimelineStage.committed_timeline_id == timeline.id
                ).all()
                for stage in stages:
                    m_count = self.db.query(TimelineMilestone).filter(
                        TimelineMilestone.timeline_stage_id == stage.id
                    ).delete()
                    milestone_count += m_count
                s_count = self.db.query(TimelineStage).filter(
                    TimelineStage.committed_timeline_id == timeline.id
                ).delete()
                stage_count += s_count

            receipt["deleted_counts"]["timeline_milestones"] = milestone_count
            receipt["deleted_counts"]["timeline_stages"] = stage_count

            # Delete timelines
            committed_count = self.db.query(CommittedTimeline).filter(
                CommittedTimeline.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["committed_timelines"] = committed_count

            draft_timeline_count = self.db.query(DraftTimeline).filter(
                DraftTimeline.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["draft_timelines"] = draft_timeline_count

            # Delete DocumentArtifacts
            doc_count = self.db.query(DocumentArtifact).filter(
                DocumentArtifact.user_id == user_id
            ).delete()
            receipt["deleted_counts"]["document_artifacts"] = doc_count

            self.db.commit()

            # Log the deletion (audit logs are retained)
            self.audit_logger.log_data_deletion(
                user_id=requesting_user_id or user_id,
                target_user_id=user_id,
                ip_address=ip_address,
                changes=receipt,
            )

            logger.info(f"Data deletion completed for user {user_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Data deletion failed for user {user_id}: {e}")
            raise PrivacyEngineError(f"Data deletion failed: {e}") from e

        return receipt

    def get_data_export(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        GDPR data portability - export all user data as JSON.

        Args:
            user_id: ID of user whose data to export
            ip_address: IP address for audit logging

        Returns:
            Dictionary with all user data organized by type
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise PrivacyEngineError(f"User {user_id} not found")

        export = {
            "export_info": {
                "user_id": str(user_id),
                "export_date": datetime.utcnow().isoformat(),
                "format_version": "1.0",
            },
            "user_profile": {
                "email": user.email,
                "full_name": user.full_name,
                "institution": user.institution,
                "field_of_study": user.field_of_study,
                "created_at": user.created_at.isoformat(),
            },
            "documents": [],
            "timelines": {
                "drafts": [],
                "committed": [],
            },
            "assessments": [],
            "progress_events": [],
            "feedback_records": [],
            "analytics_snapshots": [],
        }

        # Export documents
        documents = self.db.query(DocumentArtifact).filter(
            DocumentArtifact.user_id == user_id
        ).all()
        for doc in documents:
            export["documents"].append({
                "id": str(doc.id),
                "title": doc.title,
                "description": doc.description,
                "file_type": doc.file_type,
                "document_type": doc.document_type,
                "word_count": doc.word_count,
                "created_at": doc.created_at.isoformat(),
            })

        # Export draft timelines
        draft_timelines = self.db.query(DraftTimeline).filter(
            DraftTimeline.user_id == user_id
        ).all()
        for timeline in draft_timelines:
            export["timelines"]["drafts"].append({
                "id": str(timeline.id),
                "title": timeline.title,
                "description": timeline.description,
                "status": timeline.status,
                "created_at": timeline.created_at.isoformat(),
            })

        # Export committed timelines with stages and milestones
        committed_timelines = self.db.query(CommittedTimeline).filter(
            CommittedTimeline.user_id == user_id
        ).all()
        for timeline in committed_timelines:
            timeline_data = {
                "id": str(timeline.id),
                "title": timeline.title,
                "description": timeline.description,
                "committed_date": timeline.committed_date.isoformat() if timeline.committed_date else None,
                "target_completion_date": timeline.target_completion_date.isoformat() if timeline.target_completion_date else None,
                "stages": [],
            }

            stages = self.db.query(TimelineStage).filter(
                TimelineStage.committed_timeline_id == timeline.id
            ).order_by(TimelineStage.stage_order).all()

            for stage in stages:
                stage_data = {
                    "id": str(stage.id),
                    "title": stage.title,
                    "description": stage.description,
                    "stage_order": stage.stage_order,
                    "status": stage.status,
                    "milestones": [],
                }

                milestones = self.db.query(TimelineMilestone).filter(
                    TimelineMilestone.timeline_stage_id == stage.id
                ).all()

                for milestone in milestones:
                    stage_data["milestones"].append({
                        "id": str(milestone.id),
                        "title": milestone.title,
                        "description": milestone.description,
                        "target_date": milestone.target_date.isoformat() if milestone.target_date else None,
                        "is_completed": milestone.is_completed,
                        "is_critical": milestone.is_critical,
                    })

                timeline_data["stages"].append(stage_data)

            export["timelines"]["committed"].append(timeline_data)

        # Export assessments
        assessments = self.db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == user_id
        ).all()
        for assessment in assessments:
            export["assessments"].append({
                "id": str(assessment.id),
                "assessment_date": assessment.assessment_date.isoformat(),
                "assessment_type": assessment.assessment_type,
                "overall_progress_rating": assessment.overall_progress_rating,
                "research_quality_rating": assessment.research_quality_rating,
                "timeline_adherence_rating": assessment.timeline_adherence_rating,
                "strengths": assessment.strengths,
                "challenges": assessment.challenges,
                "action_items": assessment.action_items,
                "notes": assessment.notes,
            })

        # Export progress events
        events = self.db.query(ProgressEvent).filter(
            ProgressEvent.user_id == user_id
        ).all()
        for event in events:
            export["progress_events"].append({
                "id": str(event.id),
                "event_type": event.event_type,
                "title": event.title,
                "description": event.description,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "impact_level": event.impact_level,
                "tags": event.tags,
                "notes": event.notes,
            })

        # Export feedback records
        feedbacks = self.db.query(FeedbackRecord).filter(
            FeedbackRecord.user_id == user_id
        ).all()
        for feedback in feedbacks:
            export["feedback_records"].append({
                "id": str(feedback.id),
                "feedback_type": feedback.feedback_type,
                "source": feedback.source,
                "entity_type": feedback.entity_type,
                "original_value": feedback.original_value,
                "corrected_value": feedback.corrected_value,
                "notes": feedback.notes,
                "created_at": feedback.created_at.isoformat(),
            })

        # Export analytics snapshots
        snapshots = self.db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.user_id == user_id
        ).all()
        for snapshot in snapshots:
            export["analytics_snapshots"].append({
                "id": str(snapshot.id),
                "snapshot_date": snapshot.snapshot_date.isoformat() if snapshot.snapshot_date else None,
                "overall_completion_percent": snapshot.overall_completion_percent,
                "current_stage": snapshot.current_stage,
                "created_at": snapshot.created_at.isoformat(),
            })

        # Log the export
        self.audit_logger.log_data_export(
            user_id=user_id,
            ip_address=ip_address,
        )

        return export

    def filter_sensitive_fields(
        self,
        data: Dict[str, Any],
        role: str,
    ) -> Dict[str, Any]:
        """
        Filter out fields based on viewer's role.

        Args:
            data: Dictionary containing data to filter
            role: Role of the viewer (student, supervisor, admin, institution)

        Returns:
            Filtered copy of the data
        """
        if role not in self.VALID_ROLES:
            raise PrivacyEngineError(f"Invalid role: {role}")

        sensitive_fields = self.SENSITIVE_FIELDS_BY_ROLE.get(role, set())

        if not sensitive_fields:
            return data

        result = deepcopy(data)
        self._filter_sensitive_dict(result, sensitive_fields)
        return result

    # Private helper methods

    def _is_supervisor_of(self, supervisor_id: UUID, student_id: UUID) -> bool:
        """
        Check if supervisor_id is a supervisor of student_id.

        This is a placeholder implementation. In a real system, you would
        have a supervisor-student relationship table.
        """
        # For now, check if supervisor is a superuser (admin)
        # In production, you'd have a proper supervisor-student mapping
        supervisor = self.db.query(User).filter(User.id == supervisor_id).first()
        if supervisor and supervisor.is_superuser:
            return True

        # TODO: Add proper supervisor-student relationship checking
        # This could involve checking a supervisor_student_mapping table
        # or checking if they're in the same institution with supervisor role

        return False

    def _anonymize_dict(
        self,
        data: Dict[str, Any],
        fields_to_anonymize: Set[str],
    ) -> None:
        """Recursively anonymize fields in a dictionary."""
        for key in list(data.keys()):
            if key in fields_to_anonymize:
                if isinstance(data[key], str):
                    # Create anonymous hash
                    data[key] = self._create_anonymous_id(data[key])
                elif data[key] is not None:
                    data[key] = "[ANONYMIZED]"
            elif isinstance(data[key], dict):
                self._anonymize_dict(data[key], fields_to_anonymize)
            elif isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        self._anonymize_dict(item, fields_to_anonymize)

    def _create_anonymous_id(self, value: str) -> str:
        """Create a consistent anonymous identifier from a value."""
        # Use hash to create consistent anonymous ID
        hash_obj = hashlib.sha256(value.encode())
        return f"anon_{hash_obj.hexdigest()[:12]}"

    def _filter_sensitive_dict(
        self,
        data: Dict[str, Any],
        sensitive_fields: Set[str],
    ) -> None:
        """Recursively filter sensitive fields from a dictionary."""
        for key in list(data.keys()):
            if key in sensitive_fields:
                data[key] = "[FILTERED]"
            elif isinstance(data[key], dict):
                self._filter_sensitive_dict(data[key], sensitive_fields)
            elif isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        self._filter_sensitive_dict(item, sensitive_fields)


# Convenience functions
def enforce_tenant_isolation(
    db: Session,
    user_id: UUID,
    resource_user_id: UUID,
    role: str = PrivacyEngine.ROLE_STUDENT,
    **kwargs,
) -> bool:
    """Convenience function to enforce tenant isolation."""
    engine = PrivacyEngine(db)
    return engine.enforce_tenant_isolation(
        user_id=user_id,
        resource_user_id=resource_user_id,
        role=role,
        **kwargs,
    )


def anonymize_for_aggregation(
    data: Dict[str, Any],
    fields_to_anonymize: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Convenience function to anonymize data for aggregation."""
    # This doesn't need a db session
    from copy import deepcopy

    if fields_to_anonymize is None:
        fields_to_anonymize = PrivacyEngine.DEFAULT_ANONYMIZE_FIELDS

    result = deepcopy(data)

    def _anonymize(d: Dict[str, Any], fields: Set[str]) -> None:
        for key in list(d.keys()):
            if key in fields:
                if isinstance(d[key], str):
                    hash_obj = hashlib.sha256(d[key].encode())
                    d[key] = f"anon_{hash_obj.hexdigest()[:12]}"
                elif d[key] is not None:
                    d[key] = "[ANONYMIZED]"
            elif isinstance(d[key], dict):
                _anonymize(d[key], fields)
            elif isinstance(d[key], list):
                for item in d[key]:
                    if isinstance(item, dict):
                        _anonymize(item, fields)

    _anonymize(result, set(fields_to_anonymize))
    return result

"""Audit Logger service for tracking data access and modifications.

This module provides append-only audit logging for compliance and security.
All logs are immutable once created.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


logger = logging.getLogger(__name__)


class AuditLoggerError(Exception):
    """Base exception for audit logger errors."""
    pass


class AuditLogger:
    """
    Service for logging data access and modifications.

    Provides append-only audit logging for:
    - Data access events
    - Data modifications (create, update, delete)
    - Permission denials
    - Data exports and deletions

    Rules:
    - All logs are append-only (never updated or deleted)
    - Logs are stored in the audit_logs table
    - IP addresses and user agents are captured when available
    """

    def __init__(self, db: Session):
        """
        Initialize audit logger.

        Args:
            db: Database session
        """
        self.db = db

    def log_access(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        action: str = AuditLog.ACTION_ACCESS,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        target_user_id: Optional[UUID] = None,
        reason: Optional[str] = None,
        status: str = AuditLog.STATUS_SUCCESS,
    ) -> UUID:
        """
        Log a data access event.

        Args:
            user_id: ID of user performing the access
            resource_type: Type of resource being accessed
            resource_id: Optional ID of specific resource
            action: Type of action (defaults to 'access')
            ip_address: IP address of requester
            user_agent: User agent string
            target_user_id: If accessing another user's data, their ID
            reason: Optional reason for the access
            status: Whether access was successful or denied

        Returns:
            UUID of created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            target_user_id=target_user_id,
            reason=reason,
            status=status,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        log_msg = (
            f"Audit: user={user_id} action={action} "
            f"resource={resource_type}:{resource_id} status={status}"
        )
        if target_user_id:
            log_msg += f" target_user={target_user_id}"

        logger.info(log_msg)

        return audit_log.id

    def log_data_modification(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        target_user_id: Optional[UUID] = None,
        reason: Optional[str] = None,
    ) -> UUID:
        """
        Log a data modification event.

        Args:
            user_id: ID of user performing the modification
            resource_type: Type of resource being modified
            resource_id: ID of the resource
            action: Type of action (create, update, delete)
            changes: Dictionary with before/after values
            ip_address: IP address of requester
            user_agent: User agent string
            target_user_id: If modifying another user's data, their ID
            reason: Optional reason for the modification

        Returns:
            UUID of created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            target_user_id=target_user_id,
            reason=reason,
            status=AuditLog.STATUS_SUCCESS,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.info(
            f"Audit: user={user_id} action={action} "
            f"resource={resource_type}:{resource_id} modified"
        )

        return audit_log.id

    def log_permission_denied(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        target_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> UUID:
        """
        Log a permission denial event.

        Args:
            user_id: ID of user who was denied
            resource_type: Type of resource they tried to access
            resource_id: Optional ID of specific resource
            target_user_id: If trying to access another user's data, their ID
            ip_address: IP address of requester
            user_agent: User agent string
            reason: Why permission was denied

        Returns:
            UUID of created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=AuditLog.ACTION_PERMISSION_DENIED,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            target_user_id=target_user_id,
            reason=reason,
            status=AuditLog.STATUS_DENIED,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.warning(
            f"Audit: PERMISSION DENIED user={user_id} "
            f"resource={resource_type}:{resource_id} target_user={target_user_id}"
        )

        return audit_log.id

    def log_data_export(
        self,
        user_id: UUID,
        target_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> UUID:
        """
        Log a data export event (GDPR data portability).

        Args:
            user_id: ID of user requesting export
            target_user_id: Whose data was exported (same as user_id if self)
            ip_address: IP address of requester
            user_agent: User agent string
            reason: Reason for export request

        Returns:
            UUID of created audit log entry
        """
        return self.log_access(
            user_id=user_id,
            resource_type=AuditLog.RESOURCE_USER,
            resource_id=target_user_id or user_id,
            action=AuditLog.ACTION_EXPORT,
            ip_address=ip_address,
            user_agent=user_agent,
            target_user_id=target_user_id,
            reason=reason or "GDPR data export request",
        )

    def log_consent_revocation(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Log a consent revocation event.

        Args:
            user_id: ID of user revoking consent
            ip_address: IP address of requester
            user_agent: User agent string
            changes: Summary of what was deleted/anonymized

        Returns:
            UUID of created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=AuditLog.ACTION_CONSENT_REVOKE,
            resource_type=AuditLog.RESOURCE_USER,
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            reason="User revoked data processing consent",
            status=AuditLog.STATUS_SUCCESS,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.info(f"Audit: CONSENT REVOKED user={user_id}")

        return audit_log.id

    def log_data_deletion(
        self,
        user_id: UUID,
        target_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Log a data deletion event (GDPR right to erasure).

        Args:
            user_id: ID of user requesting deletion (or admin)
            target_user_id: Whose data was deleted
            ip_address: IP address of requester
            user_agent: User agent string
            changes: Summary of what was deleted

        Returns:
            UUID of created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=AuditLog.ACTION_DATA_DELETION,
            resource_type=AuditLog.RESOURCE_USER,
            resource_id=target_user_id or user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            target_user_id=target_user_id,
            changes=changes,
            reason="GDPR data deletion request",
            status=AuditLog.STATUS_SUCCESS,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.info(
            f"Audit: DATA DELETION user={user_id} target={target_user_id or user_id}"
        )

        return audit_log.id

    def get_audit_trail(
        self,
        user_id: Optional[UUID] = None,
        target_user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filters.

        Args:
            user_id: Filter by user who performed action
            target_user_id: Filter by user whose data was accessed
            resource_type: Filter by resource type
            action_type: Filter by action type
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of audit log entries as dictionaries
        """
        query = self.db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if target_user_id:
            query = query.filter(AuditLog.target_user_id == target_user_id)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if action_type:
            query = query.filter(AuditLog.action_type == action_type)

        logs = query.order_by(
            AuditLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action_type": log.action_type,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "target_user_id": str(log.target_user_id) if log.target_user_id else None,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "status": log.status,
                "reason": log.reason,
                "changes": log.changes,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]

    def get_user_audit_summary(
        self,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get a summary of audit activity for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with activity summary
        """
        from sqlalchemy import func

        # Count by action type
        action_counts = self.db.query(
            AuditLog.action_type,
            func.count(AuditLog.id)
        ).filter(
            AuditLog.user_id == user_id
        ).group_by(AuditLog.action_type).all()

        # Count of times their data was accessed by others
        accessed_by_others = self.db.query(func.count(AuditLog.id)).filter(
            AuditLog.target_user_id == user_id,
            AuditLog.user_id != user_id
        ).scalar()

        # Most recent activity
        most_recent = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).first()

        return {
            "user_id": str(user_id),
            "action_counts": {
                action: count for action, count in action_counts
            },
            "data_accessed_by_others": accessed_by_others or 0,
            "most_recent_activity": (
                most_recent.created_at.isoformat() if most_recent else None
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }


# Convenience functions
def log_access(
    db: Session,
    user_id: UUID,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    action: str = AuditLog.ACTION_ACCESS,
    **kwargs,
) -> UUID:
    """Convenience function to log access."""
    logger_instance = AuditLogger(db)
    return logger_instance.log_access(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        **kwargs,
    )


def log_data_modification(
    db: Session,
    user_id: UUID,
    resource_type: str,
    resource_id: UUID,
    action: str,
    changes: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> UUID:
    """Convenience function to log data modification."""
    logger_instance = AuditLogger(db)
    return logger_instance.log_data_modification(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        changes=changes,
        **kwargs,
    )


def get_audit_trail(
    db: Session,
    user_id: Optional[UUID] = None,
    **kwargs,
) -> List[Dict[str, Any]]:
    """Convenience function to get audit trail."""
    logger_instance = AuditLogger(db)
    return logger_instance.get_audit_trail(user_id=user_id, **kwargs)

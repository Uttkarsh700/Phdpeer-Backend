"""AuditLog model for tracking data access and modifications."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class AuditLog(Base, BaseModel):
    """
    AuditLog model for append-only audit trail.

    Records all data access and modifications for compliance and security.
    This table is append-only - records are never updated or deleted.

    Attributes:
        user_id: The user who performed the action
        action_type: Type of action (access, create, update, delete, export, etc.)
        resource_type: Type of resource accessed (document, timeline, assessment, etc.)
        resource_id: ID of the specific resource (nullable for list operations)
        ip_address: IP address of the requester
        user_agent: Browser/client user agent
        changes: JSON object with before/after values for modifications
        reason: Optional reason or context for the action
        status: Whether the action succeeded or was denied
    """

    __tablename__ = "audit_logs"

    # Action types
    ACTION_ACCESS = "access"
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_EXPORT = "export"
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_CONSENT_REVOKE = "consent_revoke"
    ACTION_DATA_DELETION = "data_deletion"
    ACTION_PERMISSION_DENIED = "permission_denied"

    VALID_ACTION_TYPES = [
        ACTION_ACCESS,
        ACTION_CREATE,
        ACTION_UPDATE,
        ACTION_DELETE,
        ACTION_EXPORT,
        ACTION_LOGIN,
        ACTION_LOGOUT,
        ACTION_CONSENT_REVOKE,
        ACTION_DATA_DELETION,
        ACTION_PERMISSION_DENIED,
    ]

    # Resource types
    RESOURCE_USER = "user"
    RESOURCE_DOCUMENT = "document"
    RESOURCE_TIMELINE = "timeline"
    RESOURCE_STAGE = "stage"
    RESOURCE_MILESTONE = "milestone"
    RESOURCE_ASSESSMENT = "assessment"
    RESOURCE_FEEDBACK = "feedback"
    RESOURCE_PROGRESS = "progress"
    RESOURCE_ANALYTICS = "analytics"

    # Status values
    STATUS_SUCCESS = "success"
    STATUS_DENIED = "denied"
    STATUS_FAILED = "failed"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Nullable for system actions or deleted users
        index=True
    )
    action_type = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String, nullable=True)
    changes = Column(JSONB, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String, nullable=False, default=STATUS_SUCCESS)

    # Optional: who was the target user (for supervisor accessing student data)
    target_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref="audit_logs_performed"
    )
    target_user = relationship(
        "User",
        foreign_keys=[target_user_id],
        backref="audit_logs_received"
    )

    def __repr__(self):
        return (
            f"<AuditLog(user={self.user_id}, action='{self.action_type}', "
            f"resource='{self.resource_type}:{self.resource_id}', status='{self.status}')>"
        )

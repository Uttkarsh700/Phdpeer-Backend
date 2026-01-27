"""Baseline orchestrator for creating and managing baseline records."""
from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.baseline import Baseline
from app.models.user import User
from app.models.document_artifact import DocumentArtifact


class BaselineOrchestratorError(Exception):
    """Base exception for baseline orchestrator errors."""
    pass


class BaselineAlreadyExistsError(BaselineOrchestratorError):
    """Raised when attempting to modify an immutable baseline."""
    pass


class BaselineOrchestrator:
    """
    Orchestrator for creating and managing baseline records.
    
    Baselines are immutable once created. They represent the initial
    state and requirements of a PhD program.
    """
    
    def __init__(self, db: Session):
        """
        Initialize baseline orchestrator.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_baseline(
        self,
        user_id: UUID,
        program_name: str,
        institution: str,
        field_of_study: str,
        start_date: date,
        document_id: Optional[UUID] = None,
        expected_end_date: Optional[date] = None,
        total_duration_months: Optional[int] = None,
        requirements_summary: Optional[str] = None,
        research_area: Optional[str] = None,
        advisor_info: Optional[str] = None,
        funding_status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> UUID:
        """
        Create a new baseline record.
        
        Args:
            user_id: ID of the user creating the baseline
            program_name: Name of the PhD program
            institution: Academic institution
            field_of_study: Research field/discipline
            start_date: Program start date
            document_id: Optional reference to source document
            expected_end_date: Expected completion date
            total_duration_months: Expected duration in months
            requirements_summary: Summary of program requirements
            research_area: Specific research area/topic
            advisor_info: Information about advisor(s)
            funding_status: Funding information
            notes: Additional notes
            
        Returns:
            UUID of the created Baseline
            
        Raises:
            BaselineOrchestratorError: If validation fails
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BaselineOrchestratorError(f"User with ID {user_id} not found")
        
        # Verify document exists and belongs to user (if provided)
        if document_id:
            document = self.db.query(DocumentArtifact).filter(
                DocumentArtifact.id == document_id
            ).first()
            
            if not document:
                raise BaselineOrchestratorError(f"Document with ID {document_id} not found")
            
            if document.user_id != user_id:
                raise BaselineOrchestratorError(
                    f"Document {document_id} does not belong to user {user_id}"
                )
        
        # Create baseline record
        baseline = Baseline(
            user_id=user_id,
            document_artifact_id=document_id,
            program_name=program_name,
            institution=institution,
            field_of_study=field_of_study,
            start_date=start_date,
            expected_end_date=expected_end_date,
            total_duration_months=total_duration_months,
            requirements_summary=requirements_summary,
            research_area=research_area,
            advisor_info=advisor_info,
            funding_status=funding_status,
            notes=notes,
        )
        
        self.db.add(baseline)
        self.db.commit()
        self.db.refresh(baseline)
        
        return baseline.id
    
    def get_baseline(self, baseline_id: UUID) -> Optional[Baseline]:
        """
        Get a baseline by ID.
        
        Args:
            baseline_id: Baseline ID
            
        Returns:
            Baseline or None if not found
        """
        return self.db.query(Baseline).filter(
            Baseline.id == baseline_id
        ).first()
    
    def get_user_baselines(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Baseline]:
        """
        Get all baselines for a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Baselines
        """
        return self.db.query(Baseline).filter(
            Baseline.user_id == user_id
        ).order_by(Baseline.created_at.desc()).offset(skip).limit(limit).all()
    
    def verify_baseline_ownership(
        self,
        baseline_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Verify that a baseline belongs to a specific user.
        
        Args:
            baseline_id: Baseline ID
            user_id: User ID
            
        Returns:
            True if baseline belongs to user, False otherwise
        """
        baseline = self.get_baseline(baseline_id)
        if not baseline:
            return False
        return baseline.user_id == user_id
    
    def get_baseline_with_document(self, baseline_id: UUID) -> Optional[dict]:
        """
        Get baseline with associated document information.
        
        Args:
            baseline_id: Baseline ID
            
        Returns:
            Dictionary with baseline and document info, or None if not found
        """
        baseline = self.db.query(Baseline).filter(
            Baseline.id == baseline_id
        ).first()
        
        if not baseline:
            return None
        
        result = {
            "baseline": baseline,
            "document": None,
        }
        
        if baseline.document_artifact_id:
            document = self.db.query(DocumentArtifact).filter(
                DocumentArtifact.id == baseline.document_artifact_id
            ).first()
            result["document"] = document
        
        return result
    
    def delete_baseline(self, baseline_id: UUID, user_id: UUID) -> bool:
        """
        Delete a baseline.
        
        Note: Baselines are immutable, but can be deleted by their owner.
        Deletion will cascade to dependent records (draft timelines).
        
        Args:
            baseline_id: Baseline ID
            user_id: User ID (for ownership verification)
            
        Returns:
            True if deleted, False if not found or not owned by user
            
        Raises:
            BaselineOrchestratorError: If baseline has committed timelines
        """
        baseline = self.get_baseline(baseline_id)
        
        if not baseline:
            return False
        
        if baseline.user_id != user_id:
            raise BaselineOrchestratorError(
                "Cannot delete baseline: not owned by user"
            )
        
        # Check if baseline is referenced by committed timelines
        from app.models.committed_timeline import CommittedTimeline
        committed_count = self.db.query(CommittedTimeline).filter(
            CommittedTimeline.baseline_id == baseline_id
        ).count()
        
        if committed_count > 0:
            raise BaselineOrchestratorError(
                f"Cannot delete baseline: {committed_count} committed timeline(s) reference it"
            )
        
        self.db.delete(baseline)
        self.db.commit()
        return True

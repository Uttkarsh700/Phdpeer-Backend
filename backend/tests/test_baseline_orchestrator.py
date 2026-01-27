"""Tests for BaselineOrchestrator."""
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.document_artifact import DocumentArtifact
from app.orchestrators.baseline_orchestrator import (
    BaselineOrchestrator,
    BaselineOrchestratorError,
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="phd.student@university.edu",
        hashed_password="hashed_password",
        full_name="Jane Doe",
        institution="Test University",
        field_of_study="Computer Science",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_document(db, test_user):
    """Create a test document."""
    document = DocumentArtifact(
        user_id=test_user.id,
        title="Research Proposal",
        file_type="pdf",
        file_path="/uploads/test.pdf",
        file_size_bytes=1000,
        metadata="Test document content",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def test_create_baseline_success(db, test_user, test_document):
    """Test creating a baseline successfully."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        document_id=test_document.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Machine Learning",
        start_date=date.today(),
        expected_end_date=date.today() + timedelta(days=1460),  # ~4 years
        total_duration_months=48,
        requirements_summary="Complete coursework, research, and dissertation",
        research_area="Deep Learning",
        advisor_info="Dr. Smith",
        funding_status="Fully Funded",
        notes="Starting fall semester",
    )
    
    assert baseline_id is not None
    
    # Verify baseline was created
    baseline = orchestrator.get_baseline(baseline_id)
    assert baseline is not None
    assert baseline.user_id == test_user.id
    assert baseline.document_artifact_id == test_document.id
    assert baseline.program_name == "PhD in Computer Science"
    assert baseline.institution == "Test University"


def test_create_baseline_without_document(db, test_user):
    """Test creating a baseline without a document."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    
    assert baseline_id is not None
    
    baseline = orchestrator.get_baseline(baseline_id)
    assert baseline is not None
    assert baseline.document_artifact_id is None


def test_create_baseline_invalid_user(db):
    """Test creating baseline with non-existent user."""
    orchestrator = BaselineOrchestrator(db)
    
    from uuid import uuid4
    
    with pytest.raises(BaselineOrchestratorError) as exc_info:
        orchestrator.create_baseline(
            user_id=uuid4(),
            program_name="PhD in Computer Science",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today(),
        )
    
    assert "User" in str(exc_info.value)
    assert "not found" in str(exc_info.value)


def test_create_baseline_invalid_document(db, test_user):
    """Test creating baseline with non-existent document."""
    orchestrator = BaselineOrchestrator(db)
    
    from uuid import uuid4
    
    with pytest.raises(BaselineOrchestratorError) as exc_info:
        orchestrator.create_baseline(
            user_id=test_user.id,
            document_id=uuid4(),
            program_name="PhD in Computer Science",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today(),
        )
    
    assert "Document" in str(exc_info.value)
    assert "not found" in str(exc_info.value)


def test_create_baseline_document_ownership(db, test_user, test_document):
    """Test that document ownership is verified."""
    orchestrator = BaselineOrchestrator(db)
    
    # Create another user
    other_user = User(
        email="other@university.edu",
        hashed_password="hashed_password",
        full_name="John Smith",
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    # Try to create baseline with other user's document
    with pytest.raises(BaselineOrchestratorError) as exc_info:
        orchestrator.create_baseline(
            user_id=other_user.id,
            document_id=test_document.id,
            program_name="PhD in Computer Science",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today(),
        )
    
    assert "does not belong to user" in str(exc_info.value)


def test_get_user_baselines(db, test_user):
    """Test getting all baselines for a user."""
    orchestrator = BaselineOrchestrator(db)
    
    # Create multiple baselines
    for i in range(3):
        orchestrator.create_baseline(
            user_id=test_user.id,
            program_name=f"PhD Program {i}",
            institution="Test University",
            field_of_study="Computer Science",
            start_date=date.today(),
        )
    
    baselines = orchestrator.get_user_baselines(test_user.id)
    assert len(baselines) == 3


def test_verify_baseline_ownership(db, test_user):
    """Test verifying baseline ownership."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    
    # Verify ownership
    assert orchestrator.verify_baseline_ownership(baseline_id, test_user.id) is True
    
    # Create another user and verify they don't own it
    other_user = User(
        email="other@university.edu",
        hashed_password="hashed_password",
        full_name="John Smith",
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    assert orchestrator.verify_baseline_ownership(baseline_id, other_user.id) is False


def test_get_baseline_with_document(db, test_user, test_document):
    """Test getting baseline with document information."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        document_id=test_document.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    
    result = orchestrator.get_baseline_with_document(baseline_id)
    
    assert result is not None
    assert result["baseline"] is not None
    assert result["document"] is not None
    assert result["document"].id == test_document.id


def test_delete_baseline(db, test_user):
    """Test deleting a baseline."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    
    # Delete baseline
    result = orchestrator.delete_baseline(baseline_id, test_user.id)
    assert result is True
    
    # Verify it's deleted
    baseline = orchestrator.get_baseline(baseline_id)
    assert baseline is None


def test_delete_baseline_wrong_user(db, test_user):
    """Test that users can't delete others' baselines."""
    orchestrator = BaselineOrchestrator(db)
    
    baseline_id = orchestrator.create_baseline(
        user_id=test_user.id,
        program_name="PhD in Computer Science",
        institution="Test University",
        field_of_study="Computer Science",
        start_date=date.today(),
    )
    
    # Create another user
    other_user = User(
        email="other@university.edu",
        hashed_password="hashed_password",
        full_name="John Smith",
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    # Try to delete with wrong user
    with pytest.raises(BaselineOrchestratorError) as exc_info:
        orchestrator.delete_baseline(baseline_id, other_user.id)
    
    assert "not owned by user" in str(exc_info.value)

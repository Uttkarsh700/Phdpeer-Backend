"""Tests for DocumentService."""
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.services.document_service import (
    DocumentService,
    UnsupportedFileTypeError,
    DocumentServiceError,
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
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_upload_document_unsupported_type(db, test_user):
    """Test uploading unsupported file type."""
    service = DocumentService(db)
    
    with pytest.raises(UnsupportedFileTypeError):
        service.upload_document(
            user_id=test_user.id,
            file_content=b"test content",
            filename="test.txt",
        )


def test_upload_document_nonexistent_user(db):
    """Test uploading document for nonexistent user."""
    service = DocumentService(db)
    
    with pytest.raises(DocumentServiceError):
        service.upload_document(
            user_id=uuid4(),
            file_content=b"test content",
            filename="test.pdf",
        )


def test_get_document(db, test_user):
    """Test getting a document."""
    service = DocumentService(db)
    
    # Create a mock document by directly inserting
    from app.models.document_artifact import DocumentArtifact
    
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=1000,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Retrieve it
    retrieved = service.get_document(doc.id)
    assert retrieved is not None
    assert retrieved.title == "Test Document"


def test_get_user_documents(db, test_user):
    """Test getting all documents for a user."""
    service = DocumentService(db)
    
    from app.models.document_artifact import DocumentArtifact
    
    # Create multiple documents
    for i in range(3):
        doc = DocumentArtifact(
            user_id=test_user.id,
            title=f"Document {i}",
            file_type="pdf",
            file_path=f"/path/to/file{i}.pdf",
            file_size_bytes=1000,
        )
        db.add(doc)
    
    db.commit()
    
    # Retrieve all
    documents = service.get_user_documents(test_user.id)
    assert len(documents) == 3


def test_delete_document(db, test_user):
    """Test deleting a document."""
    service = DocumentService(db)
    
    from app.models.document_artifact import DocumentArtifact
    
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=1000,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Delete it
    result = service.delete_document(doc.id)
    assert result is True
    
    # Verify it's gone
    retrieved = service.get_document(doc.id)
    assert retrieved is None


def test_document_text_normalization(db, test_user):
    """Test that document text is normalized during upload."""
    service = DocumentService(db)
    from app.models.document_artifact import DocumentArtifact
    
    # Create document with normalized text
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=1000,
        document_text="This is normalized text.\n\nWith proper spacing.",
        word_count=7,
        detected_language="en",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Verify normalized text is stored
    assert doc.document_text is not None
    assert doc.word_count == 7
    assert doc.detected_language == "en"


def test_get_section_map(db, test_user):
    """Test retrieving section map from document."""
    service = DocumentService(db)
    from app.models.document_artifact import DocumentArtifact
    
    section_map = {
        "sections": [
            {"title": "Introduction", "level": 1, "word_count": 100},
            {"title": "Methods", "level": 1, "word_count": 200},
        ],
        "total_sections": 2,
        "has_abstract": False,
        "has_references": False,
        "max_depth": 1
    }
    
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=1000,
        document_text="Sample text",
        section_map_json=section_map,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Retrieve section map
    retrieved_map = service.get_section_map(doc.id)
    assert retrieved_map is not None
    assert retrieved_map["total_sections"] == 2
    assert len(retrieved_map["sections"]) == 2


def test_get_document_metadata(db, test_user):
    """Test retrieving comprehensive document metadata."""
    service = DocumentService(db)
    from app.models.document_artifact import DocumentArtifact
    
    section_map = {
        "sections": [],
        "total_sections": 0,
        "has_abstract": False,
        "has_references": False,
        "max_depth": 0
    }
    
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        description="A test document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=5000,
        document_type="proposal",
        document_text="Sample text content",
        word_count=150,
        detected_language="en",
        section_map_json=section_map,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Get metadata
    metadata = service.get_document_metadata(doc.id)
    
    assert metadata is not None
    assert metadata["title"] == "Test Document"
    assert metadata["description"] == "A test document"
    assert metadata["file_type"] == "pdf"
    assert metadata["file_size_bytes"] == 5000
    assert metadata["document_type"] == "proposal"
    assert metadata["word_count"] == 150
    assert metadata["detected_language"] == "en"
    assert metadata["has_section_map"] is True
    assert metadata["section_count"] == 0


def test_get_document_metadata_nonexistent(db):
    """Test getting metadata for nonexistent document."""
    service = DocumentService(db)
    
    metadata = service.get_document_metadata(uuid4())
    assert metadata is None


def test_get_extracted_text_returns_normalized_text(db, test_user):
    """Test that get_extracted_text returns normalized document_text."""
    service = DocumentService(db)
    from app.models.document_artifact import DocumentArtifact
    
    normalized_text = "This is the normalized text."
    
    doc = DocumentArtifact(
        user_id=test_user.id,
        title="Test Document",
        file_type="pdf",
        file_path="/path/to/file.pdf",
        file_size_bytes=1000,
        document_text=normalized_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Get extracted text
    text = service.get_extracted_text(doc.id)
    assert text == normalized_text

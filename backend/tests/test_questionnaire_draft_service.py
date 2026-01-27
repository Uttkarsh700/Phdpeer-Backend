"""Tests for QuestionnaireDraftService."""
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.questionnaire_draft import QuestionnaireDraft, QuestionnaireVersion
from app.services.questionnaire_draft_service import (
    QuestionnaireDraftService,
    QuestionnaireDraftError,
    QuestionnaireVersionError
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
        hashed_password="hashed",
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_questionnaire_version(db):
    """Create a test questionnaire version."""
    schema = {
        "sections": [
            {
                "id": "research_progress",
                "title": "Research Progress",
                "questions": [
                    {"id": "rp_1", "text": "How satisfied are you with your research progress?", "type": "scale"},
                    {"id": "rp_2", "text": "Are you meeting your research milestones?", "type": "scale"}
                ]
            },
            {
                "id": "wellbeing",
                "title": "Mental Well-being",
                "questions": [
                    {"id": "wb_1", "text": "How would you rate your overall mental health?", "type": "scale"},
                    {"id": "wb_2", "text": "Do you feel supported?", "type": "scale"}
                ]
            }
        ]
    }
    
    version = QuestionnaireVersion(
        version_number="1.0",
        title="PhD Journey Assessment v1.0",
        description="Initial version",
        schema_json=schema,
        is_active=True,
        total_questions=4,
        total_sections=2
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


class TestQuestionnaireDraftService:
    """Test suite for questionnaire draft service."""
    
    def test_create_draft(self, db, test_user, test_questionnaire_version):
        """Test creating a new draft."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(
            user_id=test_user.id,
            draft_name="Test Draft"
        )
        
        assert draft_id is not None
        
        # Verify draft was created
        draft = db.query(QuestionnaireDraft).filter(
            QuestionnaireDraft.id == draft_id
        ).first()
        
        assert draft is not None
        assert draft.user_id == test_user.id
        assert draft.draft_name == "Test Draft"
        assert draft.progress_percentage == 0
        assert draft.is_submitted is False
    
    def test_create_draft_default_version(self, db, test_user, test_questionnaire_version):
        """Test creating draft with default active version."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        draft = db.query(QuestionnaireDraft).get(draft_id)
        assert draft.questionnaire_version_id == test_questionnaire_version.id
    
    def test_create_draft_nonexistent_user(self, db, test_questionnaire_version):
        """Test error when creating draft for nonexistent user."""
        service = QuestionnaireDraftService(db)
        
        with pytest.raises(QuestionnaireDraftError) as exc:
            service.create_draft(user_id=uuid4())
        
        assert "not found" in str(exc.value)
    
    def test_save_section(self, db, test_user, test_questionnaire_version):
        """Test saving section responses."""
        service = QuestionnaireDraftService(db)
        
        # Create draft
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Save first section
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4, "rp_2": 3},
            is_section_complete=True
        )
        
        assert result["progress_percentage"] == 50  # 2 of 4 questions answered
        assert "research_progress" in result["completed_sections"]
        assert result["responses"]["research_progress"]["rp_1"] == 4
    
    def test_save_section_incremental(self, db, test_user, test_questionnaire_version):
        """Test saving section responses incrementally."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Save first question
        service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4}
        )
        
        # Save second question
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_2": 3},
            is_section_complete=True
        )
        
        # Both responses should be present
        assert result["responses"]["research_progress"]["rp_1"] == 4
        assert result["responses"]["research_progress"]["rp_2"] == 3
        assert result["progress_percentage"] == 50
    
    def test_save_section_multiple_sections(self, db, test_user, test_questionnaire_version):
        """Test saving multiple sections."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Save first section
        service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4, "rp_2": 3},
            is_section_complete=True
        )
        
        # Save second section
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="wellbeing",
            responses={"wb_1": 5, "wb_2": 4},
            is_section_complete=True
        )
        
        # All responses should be present
        assert len(result["responses"]) == 2
        assert result["progress_percentage"] == 100  # All 4 questions answered
        assert len(result["completed_sections"]) == 2
    
    def test_save_section_wrong_user(self, db, test_user, test_questionnaire_version):
        """Test error when saving section with wrong user."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        with pytest.raises(QuestionnaireDraftError) as exc:
            service.save_section(
                draft_id=draft_id,
                user_id=uuid4(),  # Different user
                section_id="research_progress",
                responses={"rp_1": 4}
            )
        
        assert "not found or not owned" in str(exc.value)
    
    def test_save_section_submitted_draft(self, db, test_user, test_questionnaire_version):
        """Test error when editing submitted draft."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Mark as submitted
        service.mark_as_submitted(draft_id, test_user.id, uuid4())
        
        # Try to save section
        with pytest.raises(QuestionnaireDraftError) as exc:
            service.save_section(
                draft_id=draft_id,
                user_id=test_user.id,
                section_id="research_progress",
                responses={"rp_1": 4}
            )
        
        assert "Cannot edit submitted draft" in str(exc.value)
    
    def test_get_draft(self, db, test_user, test_questionnaire_version):
        """Test retrieving a draft."""
        service = QuestionnaireDraftService(db)
        
        # Create and save draft
        draft_id = service.create_draft(user_id=test_user.id, draft_name="My Draft")
        service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4}
        )
        
        # Get draft
        draft = service.get_draft(draft_id, test_user.id)
        
        assert draft is not None
        assert draft["draft_name"] == "My Draft"
        assert draft["responses"]["research_progress"]["rp_1"] == 4
        assert draft["progress_percentage"] > 0
    
    def test_get_draft_wrong_user(self, db, test_user, test_questionnaire_version):
        """Test getting draft with wrong user returns None."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Try to get with different user
        draft = service.get_draft(draft_id, uuid4())
        
        assert draft is None
    
    def test_get_user_drafts(self, db, test_user, test_questionnaire_version):
        """Test getting all drafts for a user."""
        service = QuestionnaireDraftService(db)
        
        # Create multiple drafts
        draft_id_1 = service.create_draft(user_id=test_user.id, draft_name="Draft 1")
        draft_id_2 = service.create_draft(user_id=test_user.id, draft_name="Draft 2")
        
        # Get all drafts
        drafts = service.get_user_drafts(test_user.id)
        
        assert len(drafts) == 2
        draft_names = {d["draft_name"] for d in drafts}
        assert "Draft 1" in draft_names
        assert "Draft 2" in draft_names
    
    def test_get_user_drafts_exclude_submitted(self, db, test_user, test_questionnaire_version):
        """Test getting drafts excludes submitted by default."""
        service = QuestionnaireDraftService(db)
        
        # Create drafts
        draft_id_1 = service.create_draft(user_id=test_user.id, draft_name="Draft 1")
        draft_id_2 = service.create_draft(user_id=test_user.id, draft_name="Draft 2")
        
        # Submit one draft
        service.mark_as_submitted(draft_id_1, test_user.id, uuid4())
        
        # Get drafts (exclude submitted)
        drafts = service.get_user_drafts(test_user.id, include_submitted=False)
        
        assert len(drafts) == 1
        assert drafts[0]["draft_name"] == "Draft 2"
    
    def test_get_user_drafts_include_submitted(self, db, test_user, test_questionnaire_version):
        """Test getting drafts includes submitted when requested."""
        service = QuestionnaireDraftService(db)
        
        # Create and submit draft
        draft_id = service.create_draft(user_id=test_user.id)
        service.mark_as_submitted(draft_id, test_user.id, uuid4())
        
        # Get drafts (include submitted)
        drafts = service.get_user_drafts(test_user.id, include_submitted=True)
        
        assert len(drafts) == 1
        assert drafts[0]["is_submitted"] is True
    
    def test_delete_draft(self, db, test_user, test_questionnaire_version):
        """Test deleting a draft."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Delete draft
        result = service.delete_draft(draft_id, test_user.id)
        
        assert result is True
        
        # Verify deleted
        draft = db.query(QuestionnaireDraft).get(draft_id)
        assert draft is None
    
    def test_delete_draft_wrong_user(self, db, test_user, test_questionnaire_version):
        """Test deleting draft with wrong user fails."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Try to delete with different user
        result = service.delete_draft(draft_id, uuid4())
        
        assert result is False
    
    def test_delete_draft_submitted(self, db, test_user, test_questionnaire_version):
        """Test error when deleting submitted draft."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        service.mark_as_submitted(draft_id, test_user.id, uuid4())
        
        with pytest.raises(QuestionnaireDraftError) as exc:
            service.delete_draft(draft_id, test_user.id)
        
        assert "Cannot delete submitted draft" in str(exc.value)
    
    def test_mark_as_submitted(self, db, test_user, test_questionnaire_version):
        """Test marking draft as submitted."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        submission_id = uuid4()
        
        result = service.mark_as_submitted(draft_id, test_user.id, submission_id)
        
        assert result["is_submitted"] is True
        assert result["submission_id"] == str(submission_id)
    
    def test_mark_as_submitted_twice(self, db, test_user, test_questionnaire_version):
        """Test error when marking draft as submitted twice."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        service.mark_as_submitted(draft_id, test_user.id, uuid4())
        
        with pytest.raises(QuestionnaireDraftError) as exc:
            service.mark_as_submitted(draft_id, test_user.id, uuid4())
        
        assert "already submitted" in str(exc.value)


class TestQuestionnaireVersionManagement:
    """Test suite for questionnaire version management."""
    
    def test_create_version(self, db):
        """Test creating a new questionnaire version."""
        service = QuestionnaireDraftService(db)
        
        schema = {
            "sections": [
                {"id": "section_1", "questions": [{"id": "q1"}, {"id": "q2"}]}
            ]
        }
        
        version_id = service.create_version(
            version_number="1.0",
            title="Test Version",
            schema=schema,
            description="Test description"
        )
        
        assert version_id is not None
        
        # Verify version
        version = db.query(QuestionnaireVersion).get(version_id)
        assert version.version_number == "1.0"
        assert version.total_sections == 1
        assert version.total_questions == 2
        assert version.is_active is True
    
    def test_create_version_duplicate(self, db):
        """Test error when creating duplicate version."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        service.create_version("1.0", "Test", schema)
        
        with pytest.raises(QuestionnaireVersionError) as exc:
            service.create_version("1.0", "Test", schema)
        
        assert "already exists" in str(exc.value)
    
    def test_create_version_deactivates_others(self, db):
        """Test creating active version deactivates others."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        
        # Create first version (active)
        v1_id = service.create_version("1.0", "V1", schema, is_active=True)
        
        # Create second version (active)
        v2_id = service.create_version("2.0", "V2", schema, is_active=True)
        
        # First version should now be inactive
        v1 = db.query(QuestionnaireVersion).get(v1_id)
        assert v1.is_active is False
        
        # Second version should be active
        v2 = db.query(QuestionnaireVersion).get(v2_id)
        assert v2.is_active is True
    
    def test_get_active_version(self, db):
        """Test getting active version."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        service.create_version("1.0", "V1", schema, is_active=False)
        service.create_version("2.0", "V2", schema, is_active=True)
        
        active = service.get_active_version()
        
        assert active is not None
        assert active.version_number == "2.0"
    
    def test_get_version(self, db):
        """Test getting version by ID."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        version_id = service.create_version("1.0", "Test", schema)
        
        version = service.get_version(version_id)
        
        assert version is not None
        assert version.version_number == "1.0"
    
    def test_get_all_versions(self, db):
        """Test getting all versions."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        service.create_version("1.0", "V1", schema)
        service.create_version("2.0", "V2", schema)
        
        versions = service.get_all_versions()
        
        assert len(versions) == 2
    
    def test_get_all_versions_exclude_deprecated(self, db):
        """Test getting all versions excludes deprecated."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        v1_id = service.create_version("1.0", "V1", schema)
        service.create_version("2.0", "V2", schema)
        
        # Deprecate first version
        service.deprecate_version(v1_id)
        
        # Get all (exclude deprecated)
        versions = service.get_all_versions(include_deprecated=False)
        
        assert len(versions) == 1
        assert versions[0].version_number == "2.0"
    
    def test_deprecate_version(self, db):
        """Test deprecating a version."""
        service = QuestionnaireDraftService(db)
        
        schema = {"sections": []}
        version_id = service.create_version("1.0", "Test", schema, is_active=True)
        
        result = service.deprecate_version(version_id)
        
        assert result is True
        
        # Verify deprecated
        version = db.query(QuestionnaireVersion).get(version_id)
        assert version.is_deprecated is True
        assert version.is_active is False


class TestProgressCalculation:
    """Test suite for progress calculation."""
    
    def test_progress_empty_draft(self, db, test_user, test_questionnaire_version):
        """Test progress is 0 for empty draft."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        draft = service.get_draft(draft_id, test_user.id)
        
        assert draft["progress_percentage"] == 0
    
    def test_progress_partial_section(self, db, test_user, test_questionnaire_version):
        """Test progress with partial section completion."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Answer 1 of 2 questions in first section
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4}
        )
        
        # 1 of 4 total questions = 25%
        assert result["progress_percentage"] == 25
    
    def test_progress_full_section(self, db, test_user, test_questionnaire_version):
        """Test progress with full section completion."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Answer all questions in first section
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4, "rp_2": 3}
        )
        
        # 2 of 4 total questions = 50%
        assert result["progress_percentage"] == 50
    
    def test_progress_complete(self, db, test_user, test_questionnaire_version):
        """Test progress at 100% when all answered."""
        service = QuestionnaireDraftService(db)
        
        draft_id = service.create_draft(user_id=test_user.id)
        
        # Answer all questions
        service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="research_progress",
            responses={"rp_1": 4, "rp_2": 3}
        )
        
        result = service.save_section(
            draft_id=draft_id,
            user_id=test_user.id,
            section_id="wellbeing",
            responses={"wb_1": 5, "wb_2": 4}
        )
        
        assert result["progress_percentage"] == 100

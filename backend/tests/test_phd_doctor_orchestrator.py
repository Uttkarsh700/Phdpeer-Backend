"""
Comprehensive tests for PhDDoctorOrchestrator.

Tests:
- Submission validation
- Score computation
- Assessment storage
- Recommendation generation
- Draft integration
- Decision tracing
- Idempotency
"""

"""
Comprehensive tests for PhDDoctorOrchestrator.

Tests:
- Submission validation
- Score computation
- Assessment storage
- Recommendation generation
- Draft integration
- Decision tracing
- Idempotency
"""

import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.journey_assessment import JourneyAssessment
from app.models.questionnaire_draft import QuestionnaireDraft, QuestionnaireVersion
from app.models.idempotency import IdempotencyKey, DecisionTrace, EvidenceBundle
from app.orchestrators.phd_doctor_orchestrator import (
    PhDDoctorOrchestrator,
    PhDDoctorOrchestratorError,
    IncompleteSubmissionError
)
from app.services.journey_health_engine import HealthDimension


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
def sample_responses():
    """Create sample questionnaire responses."""
    return [
        {"dimension": "RESEARCH_PROGRESS", "question_id": "rp_1", "response_value": 4},
        {"dimension": "RESEARCH_PROGRESS", "question_id": "rp_2", "response_value": 3},
        {"dimension": "RESEARCH_PROGRESS", "question_id": "rp_3", "response_value": 5},
        {"dimension": "MENTAL_WELLBEING", "question_id": "wb_1", "response_value": 2},
        {"dimension": "MENTAL_WELLBEING", "question_id": "wb_2", "response_value": 1},
        {"dimension": "WORK_LIFE_BALANCE", "question_id": "wlb_1", "response_value": 3},
        {"dimension": "WORK_LIFE_BALANCE", "question_id": "wlb_2", "response_value": 3},
        {"dimension": "TIME_MANAGEMENT", "question_id": "tm_1", "response_value": 4},
    ]


class TestSubmissionValidation:
    """Test submission validation logic."""
    
    def test_submit_success(self, db, test_user, sample_responses):
        """Test successful submission."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assert "assessment_id" in result
        assert "overall_score" in result
        assert "recommendations" in result
    
    def test_submit_nonexistent_user(self, db, sample_responses):
        """Test submission with nonexistent user fails."""
        orchestrator = PhDDoctorOrchestrator(db)
        fake_user_id = uuid4()
        
        with pytest.raises(PhDDoctorOrchestratorError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=fake_user_id,
                responses=sample_responses
            )
        
        assert "not found" in str(exc.value)
    
    def test_submit_empty_responses(self, db, test_user):
        """Test submission with empty responses fails."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        with pytest.raises(IncompleteSubmissionError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=test_user.id,
                responses=[]
            )
        
        assert "No questionnaire responses" in str(exc.value)
    
    def test_submit_insufficient_responses(self, db, test_user):
        """Test submission with too few responses fails."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        responses = [
            {"dimension": "RESEARCH_PROGRESS", "question_id": "q1", "response_value": 3},
            {"dimension": "MENTAL_WELLBEING", "question_id": "q2", "response_value": 4},
        ]
        
        with pytest.raises(IncompleteSubmissionError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=test_user.id,
                responses=responses
            )
        
        assert "Insufficient responses" in str(exc.value)
        assert "minimum 5 required" in str(exc.value)
    
    def test_submit_missing_dimension(self, db, test_user):
        """Test submission with missing dimension field fails."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        responses = [
            {"question_id": "q1", "response_value": 3},  # Missing dimension
            {"dimension": "MENTAL_WELLBEING", "question_id": "q2", "response_value": 4},
            {"dimension": "WORK_LIFE_BALANCE", "question_id": "q3", "response_value": 3},
            {"dimension": "TIME_MANAGEMENT", "question_id": "q4", "response_value": 4},
            {"dimension": "MOTIVATION", "question_id": "q5", "response_value": 5},
        ]
        
        with pytest.raises(IncompleteSubmissionError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=test_user.id,
                responses=responses
            )
        
        assert "missing 'dimension' field" in str(exc.value)
    
    def test_submit_invalid_response_value(self, db, test_user):
        """Test submission with invalid response value fails."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        responses = [
            {"dimension": "RESEARCH_PROGRESS", "question_id": "q1", "response_value": 6},  # Invalid
            {"dimension": "MENTAL_WELLBEING", "question_id": "q2", "response_value": 4},
            {"dimension": "WORK_LIFE_BALANCE", "question_id": "q3", "response_value": 3},
            {"dimension": "TIME_MANAGEMENT", "question_id": "q4", "response_value": 4},
            {"dimension": "MOTIVATION", "question_id": "q5", "response_value": 5},
        ]
        
        with pytest.raises(IncompleteSubmissionError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=test_user.id,
                responses=responses
            )
        
        assert "invalid value" in str(exc.value)
        assert "must be 1-5" in str(exc.value)


class TestScoreComputation:
    """Test score computation logic."""
    
    def test_scores_computed(self, db, test_user, sample_responses):
        """Test that scores are computed correctly."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assert result["overall_score"] >= 0
        assert result["overall_score"] <= 100
        assert "overall_status" in result
        assert result["overall_status"] in ["excellent", "good", "fair", "concerning", "critical"]
    
    def test_dimension_scores(self, db, test_user, sample_responses):
        """Test that dimension scores are included."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assert "dimensions" in result
        assert len(result["dimensions"]) > 0
        
        for dimension, score_data in result["dimensions"].items():
            assert "score" in score_data
            assert "status" in score_data
            assert score_data["score"] >= 0
            assert score_data["score"] <= 100


class TestAssessmentStorage:
    """Test assessment storage."""
    
    def test_assessment_stored(self, db, test_user, sample_responses):
        """Test that assessment is stored in database."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assessment_id = result["assessment_id"]
        
        # Verify assessment exists in database
        assessment = db.query(JourneyAssessment).filter(
            JourneyAssessment.id == assessment_id
        ).first()
        
        assert assessment is not None
        assert assessment.user_id == test_user.id
        assert assessment.overall_progress_rating is not None
    
    def test_no_score_without_submission(self, db, test_user):
        """Test that no score exists without submission."""
        # Query assessments before submission
        assessments = db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == test_user.id
        ).all()
        
        assert len(assessments) == 0
    
    def test_assessment_includes_recommendations(self, db, test_user, sample_responses):
        """Test that assessment stores recommendations."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assessment_id = result["assessment_id"]
        assessment = db.query(JourneyAssessment).get(assessment_id)
        
        # Action items should be stored
        assert assessment.action_items is not None
        assert len(assessment.action_items) > 0


class TestRecommendationGeneration:
    """Test recommendation generation."""
    
    def test_recommendations_generated(self, db, test_user, sample_responses):
        """Test that recommendations are generated."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
    
    def test_recommendations_structure(self, db, test_user, sample_responses):
        """Test recommendation structure."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        for rec in result["recommendations"]:
            assert "priority" in rec
            assert "title" in rec
            assert "description" in rec
            assert "dimension" in rec
            assert "action_items" in rec
            assert isinstance(rec["action_items"], list)
            assert len(rec["action_items"]) > 0
    
    def test_critical_dimensions_identified(self, db, test_user):
        """Test that critical dimensions are identified."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        # Create responses with critical mental wellbeing
        responses = [
            {"dimension": "MENTAL_WELLBEING", "question_id": "wb_1", "response_value": 1},
            {"dimension": "MENTAL_WELLBEING", "question_id": "wb_2", "response_value": 1},
            {"dimension": "RESEARCH_PROGRESS", "question_id": "rp_1", "response_value": 5},
            {"dimension": "WORK_LIFE_BALANCE", "question_id": "wlb_1", "response_value": 5},
            {"dimension": "TIME_MANAGEMENT", "question_id": "tm_1", "response_value": 5},
        ]
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=responses
        )
        
        assert "critical_areas" in result
        assert len(result["critical_areas"]) > 0
        
        # Mental wellbeing should be in critical areas
        critical_dims = [area["dimension"] for area in result["critical_areas"]]
        assert "mental_wellbeing" in critical_dims


class TestDraftIntegration:
    """Test integration with questionnaire drafts."""
    
    def test_submit_with_draft(self, db, test_user, sample_responses):
        """Test submission with draft ID marks draft as submitted."""
        # Create a questionnaire version
        version = QuestionnaireVersion(
            version_number="1.0",
            title="Test",
            schema_json={"sections": []},
            is_active=True,
            total_questions=10,
            total_sections=2
        )
        db.add(version)
        db.flush()
        
        # Create a draft
        draft = QuestionnaireDraft(
            user_id=test_user.id,
            questionnaire_version_id=version.id,
            responses_json={},
            is_submitted=False
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses,
            draft_id=draft.id
        )
        
        # Verify draft is marked as submitted
        db.refresh(draft)
        assert draft.is_submitted is True
        assert draft.submission_id == result["assessment_id"]
    
    def test_submit_with_already_submitted_draft(self, db, test_user, sample_responses):
        """Test submission with already submitted draft fails."""
        version = QuestionnaireVersion(
            version_number="1.0",
            title="Test",
            schema_json={"sections": []},
            is_active=True,
            total_questions=10,
            total_sections=2
        )
        db.add(version)
        db.flush()
        
        draft = QuestionnaireDraft(
            user_id=test_user.id,
            questionnaire_version_id=version.id,
            responses_json={},
            is_submitted=True
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        with pytest.raises(PhDDoctorOrchestratorError) as exc:
            orchestrator.submit(
                request_id=str(uuid4()),
                user_id=test_user.id,
                responses=sample_responses,
                draft_id=draft.id
            )
        
        assert "already been submitted" in str(exc.value)


class TestDecisionTracing:
    """Test decision tracing."""
    
    def test_decision_trace_created(self, db, test_user, sample_responses):
        """Test that decision trace is created."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Verify decision trace exists
        traces = db.query(DecisionTrace).all()
        assert len(traces) > 0
    
    def test_evidence_bundle_created(self, db, test_user, sample_responses):
        """Test that evidence bundle is created."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Verify evidence bundle exists
        evidence = db.query(EvidenceBundle).all()
        assert len(evidence) > 0
    
    def test_trace_includes_steps(self, db, test_user, sample_responses):
        """Test that trace includes all pipeline steps."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        orchestrator.submit(
            request_id=str(uuid4()),
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Get the trace
        trace = db.query(DecisionTrace).first()
        assert trace is not None
        
        trace_data = trace.trace_json
        assert "steps" in trace_data
        
        # Check for expected steps
        step_actions = [step["action"] for step in trace_data["steps"]]
        assert "validate_submission" in step_actions
        assert "convert_responses" in step_actions
        assert "compute_scores" in step_actions
        assert "store_assessment" in step_actions


class TestIdempotency:
    """Test idempotency of submissions."""
    
    def test_duplicate_request_id_returns_cached(self, db, test_user, sample_responses):
        """Test that duplicate request_id returns cached response."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        request_id = str(uuid4())
        
        # First submission
        result1 = orchestrator.submit(
            request_id=request_id,
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Second submission with same request_id
        result2 = orchestrator.submit(
            request_id=request_id,
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Should return same result
        assert result1["assessment_id"] == result2["assessment_id"]
        
        # Should only create one assessment
        assessments = db.query(JourneyAssessment).filter(
            JourneyAssessment.user_id == test_user.id
        ).all()
        assert len(assessments) == 1
    
    def test_idempotency_key_stored(self, db, test_user, sample_responses):
        """Test that idempotency key is stored."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        request_id = str(uuid4())
        
        orchestrator.submit(
            request_id=request_id,
            user_id=test_user.id,
            responses=sample_responses
        )
        
        # Verify idempotency key exists
        key = db.query(IdempotencyKey).filter(
            IdempotencyKey.key == request_id
        ).first()
        
        assert key is not None
        assert key.status == "COMPLETED"


class TestBackwardsCompatibility:
    """Test backwards compatibility with old submit_questionnaire method."""
    
    def test_submit_questionnaire_still_works(self, db, test_user, sample_responses):
        """Test that old submit_questionnaire method still works."""
        orchestrator = PhDDoctorOrchestrator(db, test_user.id)
        
        result = orchestrator.submit_questionnaire(
            user_id=test_user.id,
            responses=sample_responses
        )
        
        assert "assessment_id" in result
        assert "overall_score" in result

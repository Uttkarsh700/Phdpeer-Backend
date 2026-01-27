"""
Comprehensive tests for OpportunityRelevanceEngine.

Tests:
- Discipline scoring
- Stage scoring
- Timeline scoring
- Deadline scoring
- Overall scoring
- Ranking
- Reason tag generation
"""

import pytest
from datetime import date, timedelta

from app.services.opportunity_relevance_engine import (
    OpportunityRelevanceEngine,
    Opportunity,
    UserProfile,
    TimelineContext,
    OpportunityType,
    ResearchStage,
    ReasonTag,
)


@pytest.fixture
def engine():
    """Create engine instance."""
    return OpportunityRelevanceEngine()


@pytest.fixture
def cs_early_stage_user():
    """Computer Science early-stage PhD user."""
    return UserProfile(
        discipline="Computer Science",
        subdisciplines=["Machine Learning", "AI"],
        research_stage=ResearchStage.EARLY,
        keywords=["deep learning", "neural networks", "computer vision"],
        institution_type="R1",
        geographic_region="US"
    )


@pytest.fixture
def bio_mid_stage_user():
    """Biology mid-stage PhD user."""
    return UserProfile(
        discipline="Biology",
        subdisciplines=["Molecular Biology", "Genetics"],
        research_stage=ResearchStage.MID,
        keywords=["gene expression", "CRISPR", "cell biology"],
        institution_type="R1",
        geographic_region="US"
    )


@pytest.fixture
def timeline_data_collection():
    """Timeline context for data collection stage."""
    return TimelineContext(
        current_stage_name="Data Collection",
        current_stage_progress=0.4,
        upcoming_stages=["Data Analysis", "Writing"],
        critical_milestones=["Complete dataset", "Preliminary analysis"],
        expected_completion_date=date.today() + timedelta(days=730)
    )


class TestDisciplineScoring:
    """Test discipline alignment scoring."""
    
    def test_exact_discipline_match(self, engine, cs_early_stage_user):
        """Test exact discipline match scores 100."""
        opportunity = Opportunity(
            opportunity_id="opp_1",
            title="CS Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY, ResearchStage.MID],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.discipline_score == 100.0
        assert ReasonTag.EXACT_DISCIPLINE_MATCH in score.reason_tags
    
    def test_subdiscipline_match(self, engine, cs_early_stage_user):
        """Test subdiscipline match scores 85."""
        opportunity = Opportunity(
            opportunity_id="opp_2",
            title="ML Workshop",
            opportunity_type=OpportunityType.WORKSHOP,
            disciplines=["Machine Learning", "AI"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.discipline_score == 85.0
        assert ReasonTag.BROAD_DISCIPLINE_MATCH in score.reason_tags
    
    def test_keyword_overlap(self, engine, cs_early_stage_user):
        """Test keyword overlap scoring."""
        opportunity = Opportunity(
            opportunity_id="opp_3",
            title="AI Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Engineering"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60),
            keywords=["deep learning", "computer vision", "robotics"]
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert 50.0 <= score.discipline_score <= 80.0
        assert ReasonTag.INTERDISCIPLINARY_MATCH in score.reason_tags
    
    def test_discipline_mismatch(self, engine, cs_early_stage_user):
        """Test discipline mismatch scores low."""
        opportunity = Opportunity(
            opportunity_id="opp_4",
            title="Literature Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Literature", "Humanities"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.discipline_score == 20.0
        assert ReasonTag.DISCIPLINE_MISMATCH in score.reason_tags


class TestStageScoring:
    """Test research stage scoring."""
    
    def test_perfect_stage_match(self, engine, cs_early_stage_user):
        """Test perfect stage match scores 100."""
        opportunity = Opportunity(
            opportunity_id="opp_5",
            title="Early Career Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.stage_score == 100.0
        assert ReasonTag.STAGE_PERFECT_MATCH in score.reason_tags
    
    def test_adjacent_stage_match(self, engine, cs_early_stage_user):
        """Test adjacent stage match scores 75."""
        opportunity = Opportunity(
            opportunity_id="opp_6",
            title="Mid-Career Award",
            opportunity_type=OpportunityType.AWARD,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.MID],  # Adjacent to EARLY
            deadline=date.today() + timedelta(days=60)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.stage_score == 75.0
        assert ReasonTag.STAGE_GOOD_MATCH in score.reason_tags
    
    def test_all_stages_acceptable(self, engine, cs_early_stage_user):
        """Test opportunity open to all stages."""
        opportunity = Opportunity(
            opportunity_id="opp_7",
            title="General Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[
                ResearchStage.EARLY,
                ResearchStage.MID,
                ResearchStage.LATE
            ],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.stage_score >= 60.0


class TestTimelineScoring:
    """Test timeline compatibility scoring."""
    
    def test_aligns_with_current_stage(self, engine, cs_early_stage_user, timeline_data_collection):
        """Test opportunity aligning with current stage."""
        opportunity = Opportunity(
            opportunity_id="opp_8",
            title="Data Collection Workshop",
            opportunity_type=OpportunityType.WORKSHOP,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY, ResearchStage.MID],
            deadline=date.today() + timedelta(days=30),
            keywords=["data collection", "research methods"]
        )
        
        score = engine.score_opportunity(
            opportunity,
            cs_early_stage_user,
            timeline_context=timeline_data_collection
        )
        
        assert score.timeline_score >= 80.0
        assert ReasonTag.ALIGNS_WITH_CURRENT_STAGE in score.reason_tags
    
    def test_aligns_with_upcoming_stage(self, engine, cs_early_stage_user, timeline_data_collection):
        """Test opportunity aligning with upcoming stage."""
        opportunity = Opportunity(
            opportunity_id="opp_9",
            title="Data Analysis Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.MID],
            deadline=date.today() + timedelta(days=60),
            keywords=["data analysis", "statistics"]
        )
        
        score = engine.score_opportunity(
            opportunity,
            cs_early_stage_user,
            timeline_context=timeline_data_collection
        )
        
        assert score.timeline_score >= 70.0
        assert ReasonTag.ALIGNS_WITH_UPCOMING_STAGE in score.reason_tags
    
    def test_supports_milestone(self, engine, cs_early_stage_user, timeline_data_collection):
        """Test opportunity supporting critical milestone."""
        opportunity = Opportunity(
            opportunity_id="opp_10",
            title="Dataset Completion Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY, ResearchStage.MID],
            deadline=date.today() + timedelta(days=60),
            keywords=["dataset", "preliminary analysis"]
        )
        
        score = engine.score_opportunity(
            opportunity,
            cs_early_stage_user,
            timeline_context=timeline_data_collection
        )
        
        assert score.timeline_score >= 70.0
        assert ReasonTag.SUPPORTS_MILESTONE in score.reason_tags
    
    def test_no_timeline_context(self, engine, cs_early_stage_user):
        """Test scoring without timeline context."""
        opportunity = Opportunity(
            opportunity_id="opp_11",
            title="Generic Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.timeline_score == 50.0  # Neutral score


class TestDeadlineScoring:
    """Test deadline suitability scoring."""
    
    def test_deadline_missed(self, engine, cs_early_stage_user):
        """Test missed deadline scores 0."""
        opportunity = Opportunity(
            opportunity_id="opp_12",
            title="Past Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() - timedelta(days=1)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 0.0
        assert ReasonTag.DEADLINE_MISSED in score.reason_tags
    
    def test_deadline_very_tight(self, engine, cs_early_stage_user):
        """Test very tight deadline (< 1 week)."""
        opportunity = Opportunity(
            opportunity_id="opp_13",
            title="Urgent Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=5)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 40.0
        assert ReasonTag.DEADLINE_VERY_TIGHT in score.reason_tags
    
    def test_deadline_tight(self, engine, cs_early_stage_user):
        """Test tight deadline (1-2 weeks)."""
        opportunity = Opportunity(
            opportunity_id="opp_14",
            title="Soon Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=10)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 65.0
        assert ReasonTag.DEADLINE_TIGHT in score.reason_tags
    
    def test_deadline_optimal_grant(self, engine, cs_early_stage_user):
        """Test optimal deadline for grant (30-90 days)."""
        opportunity = Opportunity(
            opportunity_id="opp_15",
            title="Research Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 100.0
        assert ReasonTag.DEADLINE_OPTIMAL in score.reason_tags
    
    def test_deadline_optimal_conference(self, engine, cs_early_stage_user):
        """Test optimal deadline for conference (14-60 days)."""
        opportunity = Opportunity(
            opportunity_id="opp_16",
            title="Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 100.0
        assert ReasonTag.DEADLINE_OPTIMAL in score.reason_tags
    
    def test_deadline_too_far(self, engine, cs_early_stage_user):
        """Test deadline too far in future."""
        opportunity = Opportunity(
            opportunity_id="opp_17",
            title="Future Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=200)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.deadline_score == 70.0
        assert ReasonTag.DEADLINE_TOO_FAR in score.reason_tags


class TestOverallScoring:
    """Test overall scoring and weighting."""
    
    def test_perfect_opportunity(self, engine, cs_early_stage_user):
        """Test perfect match opportunity."""
        opportunity = Opportunity(
            opportunity_id="opp_18",
            title="Perfect CS Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60),
            keywords=["deep learning", "neural networks"],
            prestige_level="high"
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        # Should have high overall score
        assert score.overall_score >= 90.0
        assert score.discipline_score == 100.0
        assert score.stage_score == 100.0
        assert score.deadline_score == 100.0
    
    def test_weighted_scoring(self, engine, cs_early_stage_user):
        """Test that scores are weighted correctly."""
        opportunity = Opportunity(
            opportunity_id="opp_19",
            title="Partial Match",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],  # Perfect match
            eligible_stages=[ResearchStage.MID],  # Adjacent stage
            deadline=date.today() + timedelta(days=5),  # Very tight
            keywords=[]
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        # Discipline: 100 * 0.40 = 40
        # Stage: 75 * 0.30 = 22.5
        # Timeline: 50 * 0.15 = 7.5
        # Deadline: 40 * 0.15 = 6
        # Expected: ~76
        
        assert 70.0 <= score.overall_score <= 80.0
    
    def test_low_relevance_opportunity(self, engine, cs_early_stage_user):
        """Test low relevance opportunity."""
        opportunity = Opportunity(
            opportunity_id="opp_20",
            title="Unrelated Award",
            opportunity_type=OpportunityType.AWARD,
            disciplines=["Literature"],  # Mismatch
            eligible_stages=[ResearchStage.LATE],  # Wrong stage
            deadline=date.today() - timedelta(days=1),  # Missed
            keywords=[]
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.overall_score < 30.0
        assert score.recommended_action == "skip"


class TestRanking:
    """Test opportunity ranking."""
    
    def test_rank_multiple_opportunities(self, engine, cs_early_stage_user):
        """Test ranking multiple opportunities."""
        opportunities = [
            Opportunity(
                opportunity_id="opp_21",
                title="Good Conference",
                opportunity_type=OpportunityType.CONFERENCE,
                disciplines=["Computer Science"],
                eligible_stages=[ResearchStage.EARLY],
                deadline=date.today() + timedelta(days=30)
            ),
            Opportunity(
                opportunity_id="opp_22",
                title="Perfect Grant",
                opportunity_type=OpportunityType.GRANT,
                disciplines=["Computer Science"],
                eligible_stages=[ResearchStage.EARLY],
                deadline=date.today() + timedelta(days=60),
                keywords=["deep learning"],
                prestige_level="high"
            ),
            Opportunity(
                opportunity_id="opp_23",
                title="Unrelated Workshop",
                opportunity_type=OpportunityType.WORKSHOP,
                disciplines=["Biology"],
                eligible_stages=[ResearchStage.MID],
                deadline=date.today() + timedelta(days=20)
            ),
        ]
        
        ranked = engine.rank_opportunities(opportunities, cs_early_stage_user)
        
        # Should be sorted by relevance
        assert len(ranked) == 3
        assert ranked[0].opportunity_id == "opp_22"  # Perfect Grant
        assert ranked[1].opportunity_id == "opp_21"  # Good Conference
        assert ranked[2].opportunity_id == "opp_23"  # Unrelated
        
        # Scores should be descending
        assert ranked[0].overall_score > ranked[1].overall_score
        assert ranked[1].overall_score > ranked[2].overall_score
    
    def test_rank_with_min_score(self, engine, cs_early_stage_user):
        """Test ranking with minimum score threshold."""
        opportunities = [
            Opportunity(
                opportunity_id="opp_24",
                title="Good Conference",
                opportunity_type=OpportunityType.CONFERENCE,
                disciplines=["Computer Science"],
                eligible_stages=[ResearchStage.EARLY],
                deadline=date.today() + timedelta(days=30)
            ),
            Opportunity(
                opportunity_id="opp_25",
                title="Unrelated",
                opportunity_type=OpportunityType.WORKSHOP,
                disciplines=["Literature"],
                eligible_stages=[ResearchStage.LATE],
                deadline=date.today() + timedelta(days=20)
            ),
        ]
        
        ranked = engine.rank_opportunities(
            opportunities,
            cs_early_stage_user,
            min_score=50.0
        )
        
        # Should filter out low-relevance opportunity
        assert len(ranked) == 1
        assert ranked[0].opportunity_id == "opp_24"


class TestReasonTags:
    """Test reason tag generation."""
    
    def test_characteristic_tags(self, engine, cs_early_stage_user):
        """Test characteristic tags are added."""
        opportunity = Opportunity(
            opportunity_id="opp_26",
            title="Prestigious Conference",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30),
            prestige_level="high"
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert ReasonTag.HIGH_PRESTIGE in score.reason_tags
        assert ReasonTag.PUBLICATION_VENUE in score.reason_tags
        assert ReasonTag.NETWORKING_OPPORTUNITY in score.reason_tags
        assert ReasonTag.CAREER_BUILDING in score.reason_tags
    
    def test_funding_opportunity_tag(self, engine, cs_early_stage_user):
        """Test funding opportunity tag."""
        opportunity = Opportunity(
            opportunity_id="opp_27",
            title="Research Grant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60),
            funding_amount=50000.0
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert ReasonTag.FUNDING_OPPORTUNITY in score.reason_tags


class TestRecommendedActions:
    """Test recommended action determination."""
    
    def test_apply_now_action(self, engine, cs_early_stage_user):
        """Test 'apply_now' recommendation."""
        opportunity = Opportunity(
            opportunity_id="opp_28",
            title="Excellent Match",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=45)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.overall_score >= 75.0
        assert score.recommended_action == "apply_now"
    
    def test_prepare_action(self, engine, cs_early_stage_user):
        """Test 'prepare' recommendation."""
        opportunity = Opportunity(
            opportunity_id="opp_29",
            title="Good Match",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY, ResearchStage.MID],
            deadline=date.today() + timedelta(days=90)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        # Good relevance + optimal (far) deadline
        if score.overall_score >= 60:
            assert score.recommended_action in ["prepare", "apply_now"]
    
    def test_skip_action(self, engine, cs_early_stage_user):
        """Test 'skip' recommendation."""
        opportunity = Opportunity(
            opportunity_id="opp_30",
            title="Poor Match",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Literature"],
            eligible_stages=[ResearchStage.LATE],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.overall_score < 50.0
        assert score.recommended_action == "skip"


class TestUrgencyLevel:
    """Test urgency level determination."""
    
    def test_high_urgency(self, engine, cs_early_stage_user):
        """Test high urgency for relevant + optimal deadline."""
        opportunity = Opportunity(
            opportunity_id="opp_31",
            title="Urgent Relevant",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=45)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        if score.overall_score >= 70:
            assert score.urgency_level == "high"
    
    def test_low_urgency(self, engine, cs_early_stage_user):
        """Test low urgency for low relevance."""
        opportunity = Opportunity(
            opportunity_id="opp_32",
            title="Low Relevance",
            opportunity_type=OpportunityType.WORKSHOP,
            disciplines=["Biology"],
            eligible_stages=[ResearchStage.LATE],
            deadline=date.today() + timedelta(days=30)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        assert score.urgency_level == "low"


class TestExplanationGeneration:
    """Test human-readable explanation generation."""
    
    def test_explanation_includes_key_points(self, engine, cs_early_stage_user):
        """Test explanation includes key scoring points."""
        opportunity = Opportunity(
            opportunity_id="opp_33",
            title="Perfect Match",
            opportunity_type=OpportunityType.GRANT,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=60)
        )
        
        score = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        explanation_lower = score.explanation.lower()
        
        # Should mention discipline match
        assert any(word in explanation_lower for word in ["exact", "discipline", "match"])
        
        # Should mention stage
        assert any(word in explanation_lower for word in ["stage", "perfect"])
        
        # Should mention deadline
        assert any(word in explanation_lower for word in ["deadline", "optimal", "timing"])


class TestDeterminism:
    """Test that scoring is deterministic."""
    
    def test_same_inputs_same_output(self, engine, cs_early_stage_user):
        """Test same inputs produce same outputs."""
        opportunity = Opportunity(
            opportunity_id="opp_34",
            title="Test Opportunity",
            opportunity_type=OpportunityType.CONFERENCE,
            disciplines=["Computer Science"],
            eligible_stages=[ResearchStage.EARLY],
            deadline=date.today() + timedelta(days=30)
        )
        
        # Score twice
        score1 = engine.score_opportunity(opportunity, cs_early_stage_user)
        score2 = engine.score_opportunity(opportunity, cs_early_stage_user)
        
        # Should be identical
        assert score1.overall_score == score2.overall_score
        assert score1.discipline_score == score2.discipline_score
        assert score1.stage_score == score2.stage_score
        assert score1.timeline_score == score2.timeline_score
        assert score1.deadline_score == score2.deadline_score
        assert set(score1.reason_tags) == set(score2.reason_tags)
        assert score1.recommended_action == score2.recommended_action

"""
Comprehensive tests for JourneyHealthEngine.

Tests:
- Dimension scoring (1-5 scale → 0-100)
- Status determination (excellent to critical)
- Overall score calculation (weighted average)
- Recommendation generation (rule-based)
- Edge cases (empty responses, single dimension, etc.)
"""

import pytest
from app.services.journey_health_engine import (
    JourneyHealthEngine,
    QuestionResponse,
    HealthDimension,
    HealthStatus,
    JourneyHealthReport,
)


class TestDimensionScoring:
    """Test dimension scoring logic."""
    
    def test_perfect_score(self):
        """Test dimension with all 5s scores 100."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 5),
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q2", 5),
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q3", 5),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.RESEARCH_PROGRESS]
        
        assert score.score == 100.0
        assert score.status == HealthStatus.EXCELLENT
    
    def test_lowest_score(self):
        """Test dimension with all 1s scores 0."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q2", 1),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.MENTAL_WELLBEING]
        
        assert score.score == 0.0
        assert score.status == HealthStatus.CRITICAL
    
    def test_midpoint_score(self):
        """Test dimension with all 3s scores 50."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 3),
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q2", 3),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.WORK_LIFE_BALANCE]
        
        assert score.score == 50.0
        assert score.status == HealthStatus.FAIR
    
    def test_average_score(self):
        """Test dimension with mixed scores averages correctly."""
        engine = JourneyHealthEngine()
        
        # Scores: 1=0, 3=50, 5=100 → average = 50
        responses = [
            QuestionResponse(HealthDimension.MOTIVATION, "q1", 1),
            QuestionResponse(HealthDimension.MOTIVATION, "q2", 3),
            QuestionResponse(HealthDimension.MOTIVATION, "q3", 5),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.MOTIVATION]
        
        assert score.score == 50.0
    
    def test_scale_conversion(self):
        """Test 1-5 scale converts correctly to 0-100."""
        engine = JourneyHealthEngine()
        
        # Test each scale point
        test_cases = [
            (1, 0.0),    # 1 → 0
            (2, 25.0),   # 2 → 25
            (3, 50.0),   # 3 → 50
            (4, 75.0),   # 4 → 75
            (5, 100.0),  # 5 → 100
        ]
        
        for value, expected in test_cases:
            responses = [
                QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q1", value)
            ]
            report = engine.assess_health(responses)
            score = report.dimension_scores[HealthDimension.TIME_MANAGEMENT]
            assert score.score == expected, f"Value {value} should convert to {expected}"


class TestStatusDetermination:
    """Test health status determination logic."""
    
    def test_status_thresholds(self):
        """Test status is determined correctly by thresholds."""
        engine = JourneyHealthEngine()
        
        test_cases = [
            (100, HealthStatus.EXCELLENT),  # >= 80
            (90, HealthStatus.EXCELLENT),
            (80, HealthStatus.EXCELLENT),
            (75, HealthStatus.GOOD),        # >= 65
            (65, HealthStatus.GOOD),
            (60, HealthStatus.FAIR),        # >= 50
            (50, HealthStatus.FAIR),
            (45, HealthStatus.CONCERNING),  # >= 35
            (35, HealthStatus.CONCERNING),
            (30, HealthStatus.CRITICAL),    # < 35
            (0, HealthStatus.CRITICAL),
        ]
        
        for score, expected_status in test_cases:
            status = engine._determine_status(score)
            assert status == expected_status, f"Score {score} should be {expected_status}"


class TestOverallScoreCalculation:
    """Test overall score calculation with weighted dimensions."""
    
    def test_uniform_scores_no_weight(self):
        """Test overall score with all dimensions equal (ignoring weights)."""
        engine = JourneyHealthEngine()
        
        # All dimensions score 50
        responses = []
        for dimension in HealthDimension:
            responses.extend([
                QuestionResponse(dimension, f"{dimension.value}_q1", 3),
                QuestionResponse(dimension, f"{dimension.value}_q2", 3),
            ])
        
        report = engine.assess_health(responses)
        
        # With weights, overall won't be exactly 50, but should be close
        assert 45 <= report.overall_score <= 55
    
    def test_critical_dimension_affects_overall(self):
        """Test that critical dimension lowers overall score."""
        engine = JourneyHealthEngine()
        
        # Most dimensions excellent (5), one critical (1)
        responses = []
        for dimension in HealthDimension:
            if dimension == HealthDimension.MENTAL_WELLBEING:
                value = 1  # Critical
            else:
                value = 5  # Excellent
            
            responses.append(QuestionResponse(dimension, f"{dimension.value}_q1", value))
        
        report = engine.assess_health(responses)
        
        # Overall should be pulled down by the critical dimension
        assert report.overall_score < 100
        assert report.overall_score > 0
    
    def test_weighted_dimensions(self):
        """Test that dimension weights affect overall score."""
        engine = JourneyHealthEngine()
        
        # High-weight dimension (mental_wellbeing) has low score
        # Low-weight dimensions have high scores
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),  # Weight 1.3, score 0
            QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q1", 5),   # Weight 0.9, score 100
            QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q2", 5),
        ]
        
        report = engine.assess_health(responses)
        
        # Mental wellbeing's low score should have more impact due to higher weight
        assert report.overall_score < 50


class TestRecommendationGeneration:
    """Test recommendation generation logic."""
    
    def test_critical_dimension_gets_high_priority(self):
        """Test critical dimension generates high-priority recommendation."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q2", 1),
        ]
        
        report = engine.assess_health(responses)
        
        assert len(report.recommendations) > 0
        mental_rec = next(
            (r for r in report.recommendations if r.dimension == HealthDimension.MENTAL_WELLBEING),
            None
        )
        assert mental_rec is not None
        assert mental_rec.priority == "high"
    
    def test_concerning_dimension_gets_medium_priority(self):
        """Test concerning dimension generates medium-priority recommendation."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 2),  # Score 25
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q2", 2),
        ]
        
        report = engine.assess_health(responses)
        
        wlb_rec = next(
            (r for r in report.recommendations if r.dimension == HealthDimension.WORK_LIFE_BALANCE),
            None
        )
        assert wlb_rec is not None
        assert wlb_rec.priority == "medium"
    
    def test_fair_dimension_gets_low_priority(self):
        """Test fair dimension generates low-priority recommendation."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q1", 3),  # Score 50
            QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q2", 3),
        ]
        
        report = engine.assess_health(responses)
        
        tm_rec = next(
            (r for r in report.recommendations if r.dimension == HealthDimension.TIME_MANAGEMENT),
            None
        )
        assert tm_rec is not None
        assert tm_rec.priority == "low"
    
    def test_excellent_dimension_no_recommendation(self):
        """Test excellent dimension doesn't generate recommendation."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.ACADEMIC_CONFIDENCE, "q1", 5),
            QuestionResponse(HealthDimension.ACADEMIC_CONFIDENCE, "q2", 5),
        ]
        
        report = engine.assess_health(responses)
        
        # Should have no recommendations for excellent dimension
        ac_rec = next(
            (r for r in report.recommendations if r.dimension == HealthDimension.ACADEMIC_CONFIDENCE),
            None
        )
        assert ac_rec is None
    
    def test_recommendations_sorted_by_priority(self):
        """Test recommendations are sorted high → medium → low."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),       # Critical → high
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 2),     # Concerning → medium
            QuestionResponse(HealthDimension.TIME_MANAGEMENT, "q1", 3),       # Fair → low
        ]
        
        report = engine.assess_health(responses)
        
        priorities = [r.priority for r in report.recommendations]
        assert priorities == sorted(priorities, key=lambda p: {"high": 0, "medium": 1, "low": 2}[p])
    
    def test_recommendation_has_action_items(self):
        """Test recommendations include concrete action items."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.SUPERVISOR_RELATIONSHIP, "q1", 1),
        ]
        
        report = engine.assess_health(responses)
        
        sr_rec = report.recommendations[0]
        assert len(sr_rec.action_items) > 0
        assert all(isinstance(action, str) for action in sr_rec.action_items)


class TestStrengthsAndConcerns:
    """Test identification of strengths and concerns."""
    
    def test_high_scores_identified_as_strength(self):
        """Test that mostly high scores (4-5) are identified as strength."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 5),
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q2", 4),
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q3", 5),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.RESEARCH_PROGRESS]
        
        assert len(score.strengths) > 0
    
    def test_low_scores_identified_as_concern(self):
        """Test that mostly low scores (1-2) are identified as concern."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q2", 2),
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q3", 1),
        ]
        
        report = engine.assess_health(responses)
        score = report.dimension_scores[HealthDimension.MENTAL_WELLBEING]
        
        assert len(score.concerns) > 0


class TestMultipleDimensions:
    """Test assessment with multiple dimensions."""
    
    def test_all_dimensions(self):
        """Test assessment with all 8 dimensions."""
        engine = JourneyHealthEngine()
        
        responses = []
        for dimension in HealthDimension:
            responses.extend([
                QuestionResponse(dimension, f"{dimension.value}_q1", 3),
                QuestionResponse(dimension, f"{dimension.value}_q2", 4),
            ])
        
        report = engine.assess_health(responses)
        
        assert len(report.dimension_scores) == 8
        assert report.overall_score > 0
        assert report.overall_status in HealthStatus
    
    def test_mixed_dimension_scores(self):
        """Test with some dimensions excellent, some critical."""
        engine = JourneyHealthEngine()
        
        responses = [
            # Excellent dimensions
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 5),
            QuestionResponse(HealthDimension.ACADEMIC_CONFIDENCE, "q1", 5),
            # Critical dimensions
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 1),
        ]
        
        report = engine.assess_health(responses)
        
        # Should have both excellent and critical dimensions
        critical_dims = report.get_critical_dimensions()
        healthy_dims = report.get_healthy_dimensions()
        
        assert len(critical_dims) > 0
        assert len(healthy_dims) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_responses_raises_error(self):
        """Test that empty responses raise ValueError."""
        engine = JourneyHealthEngine()
        
        with pytest.raises(ValueError) as exc:
            engine.assess_health([])
        
        assert "No questionnaire responses provided" in str(exc.value)
    
    def test_single_response(self):
        """Test assessment with single response."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MOTIVATION, "q1", 4)
        ]
        
        report = engine.assess_health(responses)
        
        assert len(report.dimension_scores) == 1
        assert report.overall_score == 75.0  # Single response, value 4 → 75
    
    def test_single_dimension_multiple_questions(self):
        """Test single dimension with multiple questions."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.SUPPORT_NETWORK, "q1", 2),
            QuestionResponse(HealthDimension.SUPPORT_NETWORK, "q2", 3),
            QuestionResponse(HealthDimension.SUPPORT_NETWORK, "q3", 4),
        ]
        
        report = engine.assess_health(responses)
        
        assert len(report.dimension_scores) == 1
        score = report.dimension_scores[HealthDimension.SUPPORT_NETWORK]
        # (25 + 50 + 75) / 3 = 50
        assert score.score == 50.0


class TestReportMethods:
    """Test JourneyHealthReport helper methods."""
    
    def test_get_critical_dimensions(self):
        """Test getting critical/concerning dimensions."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),     # Critical
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 2),    # Concerning
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 5),    # Excellent
        ]
        
        report = engine.assess_health(responses)
        critical_dims = report.get_critical_dimensions()
        
        assert len(critical_dims) == 2
        dim_names = {d.dimension for d in critical_dims}
        assert HealthDimension.MENTAL_WELLBEING in dim_names
        assert HealthDimension.WORK_LIFE_BALANCE in dim_names
    
    def test_get_healthy_dimensions(self):
        """Test getting good/excellent dimensions."""
        engine = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 5),      # Excellent
            QuestionResponse(HealthDimension.ACADEMIC_CONFIDENCE, "q1", 4),    # Good
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 1),       # Critical
        ]
        
        report = engine.assess_health(responses)
        healthy_dims = report.get_healthy_dimensions()
        
        assert len(healthy_dims) == 2
        dim_names = {d.dimension for d in healthy_dims}
        assert HealthDimension.RESEARCH_PROGRESS in dim_names
        assert HealthDimension.ACADEMIC_CONFIDENCE in dim_names


class TestScoringTransparency:
    """Test that scoring is transparent and repeatable."""
    
    def test_same_inputs_same_outputs(self):
        """Test that same inputs always produce same outputs (deterministic)."""
        engine1 = JourneyHealthEngine()
        engine2 = JourneyHealthEngine()
        
        responses = [
            QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 3),
            QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q1", 4),
            QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "q1", 2),
        ]
        
        report1 = engine1.assess_health(responses)
        report2 = engine2.assess_health(responses)
        
        assert report1.overall_score == report2.overall_score
        assert report1.overall_status == report2.overall_status
        assert len(report1.recommendations) == len(report2.recommendations)
    
    def test_scoring_formula_documented(self):
        """Test that scoring formula is clear and documented."""
        engine = JourneyHealthEngine()
        
        # Formula: ((value - 1) / 4) * 100
        # Test with known values
        responses = [QuestionResponse(HealthDimension.MOTIVATION, "q1", 3)]
        report = engine.assess_health(responses)
        
        # Manual calculation: ((3 - 1) / 4) * 100 = 50
        assert report.dimension_scores[HealthDimension.MOTIVATION].score == 50.0
    
    def test_thresholds_documented(self):
        """Test that status thresholds are clearly defined."""
        engine = JourneyHealthEngine()
        
        # Thresholds should be accessible
        assert engine.THRESHOLDS[HealthStatus.EXCELLENT] == 80
        assert engine.THRESHOLDS[HealthStatus.GOOD] == 65
        assert engine.THRESHOLDS[HealthStatus.FAIR] == 50
        assert engine.THRESHOLDS[HealthStatus.CONCERNING] == 35
        assert engine.THRESHOLDS[HealthStatus.CRITICAL] == 0
    
    def test_weights_documented(self):
        """Test that dimension weights are clearly defined."""
        engine = JourneyHealthEngine()
        
        # Weights should be accessible
        assert HealthDimension.MENTAL_WELLBEING in engine.DIMENSION_RULES
        assert "weight" in engine.DIMENSION_RULES[HealthDimension.MENTAL_WELLBEING]
        
        # Mental wellbeing should have high weight
        mental_weight = engine.DIMENSION_RULES[HealthDimension.MENTAL_WELLBEING]["weight"]
        assert mental_weight > 1.0

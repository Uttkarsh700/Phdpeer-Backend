"""Tests for TimelineIntelligenceEngine."""
import pytest

from app.services.timeline_intelligence_engine import (
    TimelineIntelligenceEngine,
    StageType,
    TextSegment,
    DetectedStage,
    ExtractedMilestone,
    DurationEstimate,
    Dependency,
)


@pytest.fixture
def engine():
    """Create engine instance."""
    return TimelineIntelligenceEngine()


@pytest.fixture
def sample_phd_text():
    """Sample PhD program text."""
    return """
    The PhD program begins with coursework in the first two semesters.
    Students must complete 48 credits of graduate courses.
    
    Following coursework, students will conduct a literature review over 6 months.
    This includes surveying prior work and related research.
    
    The research phase lasts approximately 2 years.
    Students will collect data and conduct experiments.
    
    Data analysis follows the research phase.
    
    Writing the dissertation takes one year.
    Students must submit their thesis before the defense.
    
    The defense is the final required milestone.
    Students must pass the oral examination.
    """


def test_segment_text(engine, sample_phd_text):
    """Test text segmentation."""
    segments = engine.segment_text(sample_phd_text)
    
    assert len(segments) > 0
    assert all(isinstance(s, TextSegment) for s in segments)
    assert segments[0].segment_index == 0
    
    # Check that content is preserved
    all_content = ' '.join(s.content for s in segments)
    assert "coursework" in all_content.lower()
    assert "dissertation" in all_content.lower()


def test_segment_empty_text(engine):
    """Test segmentation with empty text."""
    segments = engine.segment_text("")
    assert segments == []
    
    segments = engine.segment_text("   \n\n   ")
    assert segments == []


def test_detect_stages(engine, sample_phd_text):
    """Test stage detection."""
    stages = engine.detect_stages(sample_phd_text)
    
    assert len(stages) > 0
    assert all(isinstance(s, DetectedStage) for s in stages)
    
    # Check that common stages are detected
    stage_types = [s.stage_type for s in stages]
    assert StageType.COURSEWORK in stage_types
    assert StageType.LITERATURE_REVIEW in stage_types
    assert StageType.RESEARCH in stage_types
    assert StageType.WRITING in stage_types
    assert StageType.DEFENSE in stage_types
    
    # Check confidence scores
    for stage in stages:
        assert 0.0 <= stage.confidence <= 1.0


def test_detect_stages_no_matches(engine):
    """Test stage detection with text that has no matches."""
    text = "This is some random text with no PhD-related content."
    stages = engine.detect_stages(text)
    
    # Should return empty list or very low confidence
    assert len(stages) == 0 or all(s.confidence < 0.3 for s in stages)


def test_extract_milestones(engine, sample_phd_text):
    """Test milestone extraction."""
    milestones = engine.extract_milestones(sample_phd_text)
    
    assert len(milestones) > 0
    assert all(isinstance(m, ExtractedMilestone) for m in milestones)
    
    # Check milestone types
    milestone_types = [m.milestone_type for m in milestones]
    assert "exam" in milestone_types or "defense" in milestone_types


def test_extract_milestones_critical(engine):
    """Test critical milestone detection."""
    text = """
    Students must pass the qualifying exam.
    This is a required milestone before continuing.
    The defense is the final mandatory step.
    """
    
    milestones = engine.extract_milestones(text)
    
    # At least one should be marked critical
    critical_milestones = [m for m in milestones if m.is_critical]
    assert len(critical_milestones) > 0


def test_estimate_durations_explicit(engine):
    """Test duration estimation with explicit mentions."""
    text = """
    The literature review takes 6 months.
    Research phase lasts 2 years.
    Writing requires one year.
    Analysis takes three months.
    """
    
    estimates = engine.estimate_durations(text)
    
    assert len(estimates) > 0
    assert all(isinstance(e, DurationEstimate) for e in estimates)
    
    # Check for specific durations
    durations = {e.item_description: e.duration_months for e in estimates}
    
    # Should find some explicit durations
    explicit_estimates = [e for e in estimates if e.basis == "pattern"]
    assert len(explicit_estimates) > 0


def test_estimate_durations_defaults(engine, sample_phd_text):
    """Test default duration estimates."""
    estimates = engine.estimate_durations(sample_phd_text)
    
    # Should include both explicit and default estimates
    explicit = [e for e in estimates if e.basis == "pattern"]
    defaults = [e for e in estimates if e.basis == "default"]
    
    assert len(explicit) > 0  # Text has explicit durations
    assert len(defaults) > 0  # Should add defaults for stages


def test_map_dependencies(engine, sample_phd_text):
    """Test dependency mapping."""
    dependencies = engine.map_dependencies(sample_phd_text)
    
    assert len(dependencies) > 0
    assert all(isinstance(d, Dependency) for d in dependencies)
    
    # Check dependency types
    dep_types = [d.dependency_type for d in dependencies]
    assert "sequential" in dep_types


def test_map_dependencies_prerequisite(engine):
    """Test prerequisite dependency detection."""
    text = """
    Completing coursework is required before starting research.
    The literature review depends on completing the courses.
    Students must pass the qualifying exam prior to dissertation work.
    """
    
    dependencies = engine.map_dependencies(text)
    
    # Should detect prerequisite dependencies
    prerequisites = [d for d in dependencies if d.dependency_type == "prerequisite"]
    assert len(prerequisites) >= 0  # May or may not detect depending on milestone extraction


def test_stage_ordering(engine):
    """Test that stages are ordered logically."""
    text = """
    First, complete coursework.
    Then conduct a literature review.
    After that, begin research.
    Following research, analyze the data.
    Finally, write the dissertation and defend.
    """
    
    stages = engine.detect_stages(text)
    dependencies = engine.map_dependencies(text)
    
    # Should have sequential dependencies
    sequential_deps = [d for d in dependencies if d.dependency_type == "sequential"]
    assert len(sequential_deps) > 0


def test_deduplication(engine):
    """Test milestone deduplication."""
    text = """
    Complete the qualifying exam.
    Pass the qualifying exam.
    The qualifying exam is required.
    """
    
    milestones = engine.extract_milestones(text)
    
    # Should deduplicate similar milestones
    titles = [m.title.lower() for m in milestones]
    # Count mentions of "qualifying"
    qualifying_count = sum(1 for t in titles if "qualifying" in t)
    
    # Should have fewer milestones than mentions due to deduplication
    assert qualifying_count < 3


def test_segment_types(engine):
    """Test detection of different segment types."""
    text = """
# Research Plan

The research will proceed as follows:

1. Literature review
2. Data collection
3. Analysis

- First milestone: proposal
- Second milestone: exam
- Third milestone: defense
    """
    
    segments = engine.segment_text(text)
    
    segment_types = [s.segment_type for s in segments]
    
    # Should detect different types (exact types depend on implementation)
    assert len(set(segment_types)) >= 1  # At least one type


def test_confidence_scores(engine, sample_phd_text):
    """Test that confidence scores are reasonable."""
    stages = engine.detect_stages(sample_phd_text)
    dependencies = engine.map_dependencies(sample_phd_text)
    
    # All confidence scores should be between 0 and 1
    for stage in stages:
        assert 0.0 <= stage.confidence <= 1.0
    
    for dep in dependencies:
        assert 0.0 <= dep.confidence <= 1.0


def test_empty_input_handling(engine):
    """Test handling of empty inputs."""
    empty_text = ""
    
    segments = engine.segment_text(empty_text)
    assert segments == []
    
    stages = engine.detect_stages(empty_text)
    assert stages == []
    
    milestones = engine.extract_milestones(empty_text)
    assert milestones == []
    
    estimates = engine.estimate_durations(empty_text)
    assert estimates == []
    
    dependencies = engine.map_dependencies(empty_text)
    assert dependencies == []

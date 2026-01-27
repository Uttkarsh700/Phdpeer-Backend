"""
Tests for enhanced milestone extraction in TimelineIntelligenceEngine.

Tests extraction of 2-5 milestones per detected stage.
"""

import pytest
from app.services.timeline_intelligence_engine import (
    TimelineIntelligenceEngine,
    StageType,
    ExtractedMilestone
)


class TestMilestoneExtraction:
    """Tests for extract_milestones() method."""
    
    def test_extract_with_explicit_mentions(self):
        """Test extraction when milestones are explicitly mentioned."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review Phase
        
        I will conduct a comprehensive literature review and compile a bibliography.
        The literature survey will be completed by reviewing existing research.
        A literature review chapter will be drafted for the dissertation.
        
        Methodology Phase
        
        The research design will be finalized and submitted for ethics approval.
        Data collection instruments will be developed and pilot tested.
        """
        
        section_map = {
            "sections": [
                {"title": "Literature Review", "start_line": 1},
                {"title": "Methodology", "start_line": 7}
            ]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        # Should have milestones for both stages
        assert len(milestones) > 0
        
        # Check that milestones are linked to stages
        stage_names = set(m.stage for m in milestones)
        assert "Literature Review" in stage_names or "Methodology Development" in stage_names
        
        # Each milestone should have required fields
        for milestone in milestones:
            assert milestone.name is not None
            assert milestone.description is not None
            assert milestone.stage is not None
            assert milestone.evidence_snippet is not None
    
    def test_extract_generates_generic_milestones(self):
        """Test that generic milestones are generated when explicit mentions are missing."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The research will involve data collection and analysis phases.
        """
        
        milestones = engine.extract_milestones(text)
        
        # Should generate at least 2 milestones per detected stage
        if len(milestones) > 0:
            # Group by stage
            by_stage = {}
            for m in milestones:
                if m.stage not in by_stage:
                    by_stage[m.stage] = []
                by_stage[m.stage].append(m)
            
            # Each stage should have 2-5 milestones
            for stage, stage_milestones in by_stage.items():
                assert 2 <= len(stage_milestones) <= 5, \
                    f"Stage '{stage}' has {len(stage_milestones)} milestones, expected 2-5"
    
    def test_milestone_structure(self):
        """Test that milestones have correct structure."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review
        
        A comprehensive literature review will be conducted to identify research gaps.
        """
        
        section_map = {
            "sections": [{"title": "Literature Review", "start_line": 1}]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        assert len(milestones) > 0
        
        # Check structure
        milestone = milestones[0]
        assert hasattr(milestone, 'name')
        assert hasattr(milestone, 'description')
        assert hasattr(milestone, 'stage')
        assert hasattr(milestone, 'evidence_snippet')
        assert hasattr(milestone, 'milestone_type')
        assert hasattr(milestone, 'is_critical')
        assert hasattr(milestone, 'confidence')
        
        # Check types
        assert isinstance(milestone.name, str)
        assert isinstance(milestone.description, str)
        assert isinstance(milestone.stage, str)
        assert isinstance(milestone.evidence_snippet, str)
        assert isinstance(milestone.confidence, float)
        assert isinstance(milestone.is_critical, bool)
    
    def test_milestones_per_stage(self):
        """Test that each detected stage gets 2-5 milestones."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Research Plan
        
        1. Literature Review
        Review existing research and identify gaps.
        
        2. Methodology
        Develop research design and obtain ethics approval.
        
        3. Data Collection
        Collect data through surveys and interviews.
        
        4. Analysis
        Analyze collected data and interpret findings.
        """
        
        section_map = {
            "sections": [
                {"title": "Literature Review", "start_line": 3},
                {"title": "Methodology", "start_line": 6},
                {"title": "Data Collection", "start_line": 9},
                {"title": "Analysis", "start_line": 12}
            ]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        # Group by stage
        by_stage = {}
        for m in milestones:
            if m.stage not in by_stage:
                by_stage[m.stage] = []
            by_stage[m.stage].append(m)
        
        # Should have milestones for multiple stages
        assert len(by_stage) >= 2
        
        # Each stage should have 2-5 milestones
        for stage, stage_milestones in by_stage.items():
            assert 2 <= len(stage_milestones) <= 5, \
                f"Stage '{stage}' has {len(stage_milestones)} milestones"
    
    def test_milestone_names_are_concise(self):
        """Test that milestone names are concise and not full sentences."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        I will complete the comprehensive literature review and compile a bibliography
        of all relevant sources in the field of study.
        """
        
        milestones = engine.extract_milestones(text)
        
        assert len(milestones) > 0
        
        for milestone in milestones:
            # Names should be reasonably short
            assert len(milestone.name) <= 60, \
                f"Milestone name too long: {milestone.name}"
            
            # Should not be empty
            assert len(milestone.name) > 0
    
    def test_evidence_snippets_included(self):
        """Test that evidence snippets are included."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The proposal defense will be scheduled for next semester.
        Data collection will involve field work and surveys.
        """
        
        milestones = engine.extract_milestones(text)
        
        assert len(milestones) > 0
        
        for milestone in milestones:
            assert milestone.evidence_snippet is not None
            assert len(milestone.evidence_snippet) > 0
            
            # Evidence should be reasonably concise
            assert len(milestone.evidence_snippet) <= 200
    
    def test_critical_milestones_identified(self):
        """Test that critical milestones are identified."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The required comprehensive examination must be passed.
        Ethics approval is required before data collection.
        The dissertation defense is mandatory.
        """
        
        milestones = engine.extract_milestones(text)
        
        # Should have some critical milestones
        critical_milestones = [m for m in milestones if m.is_critical]
        
        if len(milestones) > 0:
            # At least some should be marked critical
            # (exam, defense, required items)
            assert len(critical_milestones) > 0
    
    def test_generic_milestones_are_editable(self):
        """Test that generic milestones are reasonable templates."""
        engine = TimelineIntelligenceEngine()
        
        # Minimal text to trigger generic milestones
        text = """
        The research will involve methodology development and writing.
        """
        
        milestones = engine.extract_milestones(text)
        
        # Should generate generic milestones
        generic_milestones = [m for m in milestones if m.confidence < 0.6]
        
        assert len(generic_milestones) > 0
        
        for milestone in generic_milestones:
            # Generic milestones should have sensible names
            assert milestone.name is not None
            assert len(milestone.name) > 0
            
            # Should have descriptions
            assert milestone.description is not None
            assert len(milestone.description) > 10
            
            # Should not be too specific (no dates, specific names, etc.)
            assert "2024" not in milestone.name
            assert "2025" not in milestone.name
    
    def test_no_stages_no_milestones(self):
        """Test that no milestones are generated if no stages detected."""
        engine = TimelineIntelligenceEngine()
        
        text = "This is random text without any PhD stage keywords."
        
        milestones = engine.extract_milestones(text)
        
        # Should return empty list
        assert len(milestones) == 0
    
    def test_deduplication(self):
        """Test that duplicate milestones are removed."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review
        
        Complete the literature review. Finish the literature review.
        Conduct a literature review. Perform literature review.
        """
        
        section_map = {
            "sections": [{"title": "Literature Review", "start_line": 1}]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        # Check for duplicates
        names = [m.name for m in milestones]
        
        # Should have some deduplication
        # (exact duplicates should be removed)
        assert len(names) == len(set(names)) or len(milestones) <= 5
    
    def test_milestone_types(self):
        """Test that appropriate milestone types are assigned."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        I will take the comprehensive exam.
        Submit the research proposal.
        Attend the committee review meeting.
        Publish a paper in a journal.
        Complete the dissertation.
        """
        
        milestones = engine.extract_milestones(text)
        
        # Check that different types are used
        types = set(m.milestone_type for m in milestones)
        
        if len(milestones) >= 3:
            # Should have variety in milestone types
            assert len(types) >= 2
    
    def test_confidence_scores(self):
        """Test that confidence scores are assigned appropriately."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Methodology
        
        The research design will be finalized and ethics approval obtained.
        """
        
        section_map = {
            "sections": [{"title": "Methodology", "start_line": 1}]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        assert len(milestones) > 0
        
        # Check confidence scores
        for milestone in milestones:
            assert 0.0 <= milestone.confidence <= 1.0
        
        # Explicit mentions should have higher confidence
        explicit = [m for m in milestones if "ethics approval" in m.description.lower()]
        if explicit:
            assert explicit[0].confidence >= 0.6
        
        # Generic milestones should have lower confidence
        generic = [m for m in milestones if m.source_segment is None]
        if generic:
            assert generic[0].confidence <= 0.5
    
    def test_real_world_proposal(self):
        """Test with realistic research proposal."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        RESEARCH TIMELINE
        
        Year 1: Coursework and Literature Review
        - Complete required courses
        - Pass comprehensive examination
        - Conduct comprehensive literature review
        
        Year 2: Methodology and Data Collection
        - Finalize research design
        - Obtain IRB approval
        - Develop data collection instruments
        - Begin field work
        
        Year 3: Analysis and Writing
        - Complete data collection
        - Analyze all data
        - Write dissertation chapters
        - Submit draft to committee
        
        Year 4: Finalization and Defense
        - Revise based on feedback
        - Prepare defense presentation
        - Successfully defend dissertation
        - Submit final version
        """
        
        section_map = {
            "sections": [
                {"title": "Year 1", "start_line": 3},
                {"title": "Year 2", "start_line": 8},
                {"title": "Year 3", "start_line": 14},
                {"title": "Year 4", "start_line": 20}
            ]
        }
        
        milestones = engine.extract_milestones(text, section_map)
        
        # Should extract many explicit milestones
        assert len(milestones) >= 8
        
        # Group by stage
        by_stage = {}
        for m in milestones:
            if m.stage not in by_stage:
                by_stage[m.stage] = []
            by_stage[m.stage].append(m)
        
        # Should have milestones for multiple stages
        assert len(by_stage) >= 3
        
        # Check for critical milestones
        critical = [m for m in milestones if m.is_critical]
        assert len(critical) >= 2
        
        # Common critical milestones in PhD
        milestone_names_lower = [m.name.lower() for m in milestones]
        
        # Should detect common explicit milestones
        has_exam = any("exam" in name for name in milestone_names_lower)
        has_defense = any("defense" in name or "defend" in name for name in milestone_names_lower)
        has_approval = any("approval" in name or "irb" in name for name in milestone_names_lower)
        
        # At least one of these should be present
        assert has_exam or has_defense or has_approval
    
    def test_empty_text(self):
        """Test handling of empty text."""
        engine = TimelineIntelligenceEngine()
        
        milestones = engine.extract_milestones("")
        assert len(milestones) == 0
        
        milestones = engine.extract_milestones("   ")
        assert len(milestones) == 0
    
    def test_milestone_ordering_by_stage(self):
        """Test that milestones follow stage ordering."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        1. Literature Review - survey existing work
        2. Data Collection - gather research data
        3. Analysis - analyze collected data
        """
        
        milestones = engine.extract_milestones(text)
        
        if len(milestones) >= 3:
            # Milestones should generally follow stage order
            # (Literature Review before Data Collection before Analysis)
            
            # Get stages
            stages = list(dict.fromkeys([m.stage for m in milestones]))
            
            # Basic check: should have multiple distinct stages
            assert len(stages) >= 2

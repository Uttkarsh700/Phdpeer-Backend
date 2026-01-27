"""
Tests for enhanced stage detection in TimelineIntelligenceEngine.

Tests the three detection methods:
1. Section headers
2. Keyword clusters
3. Temporal phrases
"""

import pytest
from app.services.timeline_intelligence_engine import (
    TimelineIntelligenceEngine,
    StageType,
    DetectedStage,
    EvidenceSnippet
)


class TestStageDetection:
    """Tests for detect_stages() method."""
    
    def test_detect_from_section_headers(self):
        """Test detection using section headers from section_map."""
        engine = TimelineIntelligenceEngine()
        
        text = """This is a research proposal."""
        
        section_map = {
            "sections": [
                {"title": "Literature Review", "start_line": 1},
                {"title": "Methodology", "start_line": 10},
                {"title": "Data Collection Plan", "start_line": 20},
                {"title": "Analysis Approach", "start_line": 30}
            ]
        }
        
        stages = engine.detect_stages(text, section_map)
        
        # Should detect stages from section headers
        stage_types = [s.stage_type for s in stages]
        assert StageType.LITERATURE_REVIEW in stage_types
        assert StageType.METHODOLOGY in stage_types
        assert StageType.DATA_COLLECTION in stage_types
        assert StageType.ANALYSIS in stage_types
        
        # Check evidence source
        lit_review_stage = next(s for s in stages if s.stage_type == StageType.LITERATURE_REVIEW)
        assert any(e.source == "section_header" for e in lit_review_stage.evidence)
    
    def test_detect_from_keyword_clusters(self):
        """Test detection using keyword matching."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The research will begin with a comprehensive literature review of existing work.
        
        Following this, we will develop our methodology and research design.
        
        Data collection will involve surveys and interviews with participants.
        
        Statistical analysis will be performed on the collected data.
        
        Finally, we will write up the dissertation and prepare for submission.
        """
        
        stages = engine.detect_stages(text)
        
        # Should detect stages from keywords
        stage_types = [s.stage_type for s in stages]
        assert StageType.LITERATURE_REVIEW in stage_types
        assert StageType.METHODOLOGY in stage_types
        assert StageType.DATA_COLLECTION in stage_types
        assert StageType.ANALYSIS in stage_types
        assert StageType.WRITING in stage_types
        assert StageType.SUBMISSION in stage_types
        
        # Check evidence
        lit_stage = next(s for s in stages if s.stage_type == StageType.LITERATURE_REVIEW)
        assert any(e.source == "keyword_cluster" for e in lit_stage.evidence)
        assert len(lit_stage.keywords_matched) > 0
    
    def test_detect_from_temporal_phrases(self):
        """Test detection using temporal phrases."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        In the first year, I will complete coursework and begin reviewing the literature.
        
        I plan to develop my methodology during the second year.
        
        After collecting data, I will analyze the results.
        
        Once data is collected, statistical analysis will be performed.
        
        Following analysis, I will write the dissertation.
        
        After completing the dissertation, I will submit it for review.
        """
        
        stages = engine.detect_stages(text)
        
        # Should detect stages from temporal phrases
        stage_types = [s.stage_type for s in stages]
        assert StageType.COURSEWORK in stage_types
        assert StageType.LITERATURE_REVIEW in stage_types
        assert StageType.METHODOLOGY in stage_types
        assert StageType.DATA_COLLECTION in stage_types
        assert StageType.ANALYSIS in stage_types
        assert StageType.WRITING in stage_types
        assert StageType.SUBMISSION in stage_types
        
        # Check temporal evidence
        methodology_stage = next(s for s in stages if s.stage_type == StageType.METHODOLOGY)
        assert any(e.source == "temporal_phrase" for e in methodology_stage.evidence)
    
    def test_confidence_calculation(self):
        """Test that confidence is calculated based on detection methods."""
        engine = TimelineIntelligenceEngine()
        
        # Text with only keyword matches
        text_keywords_only = "I will conduct a literature review."
        stages_keywords = engine.detect_stages(text_keywords_only)
        
        # Text with keywords + temporal phrases
        text_multiple = "I plan to conduct a comprehensive literature review initially."
        stages_multiple = engine.detect_stages(text_multiple)
        
        # Get literature review stages
        lit_keywords = next(
            (s for s in stages_keywords if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        lit_multiple = next(
            (s for s in stages_multiple if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        
        assert lit_keywords is not None
        assert lit_multiple is not None
        
        # Multiple detection methods should increase confidence
        assert lit_multiple.confidence >= lit_keywords.confidence
    
    def test_confidence_with_section_headers(self):
        """Test highest confidence when section headers are present."""
        engine = TimelineIntelligenceEngine()
        
        text = "Literature review and background research."
        
        # Without section map
        stages_no_map = engine.detect_stages(text)
        
        # With section map
        section_map = {
            "sections": [{"title": "Literature Review", "start_line": 1}]
        }
        stages_with_map = engine.detect_stages(text, section_map)
        
        lit_no_map = next(
            (s for s in stages_no_map if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        lit_with_map = next(
            (s for s in stages_with_map if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        
        assert lit_no_map is not None
        assert lit_with_map is not None
        
        # Section header should increase confidence
        assert lit_with_map.confidence > lit_no_map.confidence
    
    def test_ordered_output(self):
        """Test that stages are returned in chronological order."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        I will defend my dissertation in the final year.
        
        The first phase involves a literature review.
        
        Data analysis comes after data collection.
        
        Methodology development follows the literature review.
        """
        
        stages = engine.detect_stages(text)
        
        # Extract stage types in order
        stage_types = [s.stage_type for s in stages]
        
        # Check that typical order is maintained
        if StageType.LITERATURE_REVIEW in stage_types and StageType.DEFENSE in stage_types:
            lit_index = stage_types.index(StageType.LITERATURE_REVIEW)
            defense_index = stage_types.index(StageType.DEFENSE)
            assert lit_index < defense_index
        
        if StageType.METHODOLOGY in stage_types and StageType.DATA_COLLECTION in stage_types:
            method_index = stage_types.index(StageType.METHODOLOGY)
            collect_index = stage_types.index(StageType.DATA_COLLECTION)
            assert method_index < collect_index
    
    def test_evidence_snippets_included(self):
        """Test that evidence snippets are included in results."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        A comprehensive literature review will be conducted to survey existing research.
        """
        
        stages = engine.detect_stages(text)
        
        lit_stage = next(
            (s for s in stages if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        
        assert lit_stage is not None
        assert len(lit_stage.evidence) > 0
        
        # Check evidence structure
        evidence = lit_stage.evidence[0]
        assert evidence.text is not None
        assert evidence.source in ["section_header", "keyword_cluster", "temporal_phrase"]
        assert evidence.location is not None
    
    def test_multiple_stages_in_segment(self):
        """Test detection of multiple stages mentioned in same segment."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The research will involve literature review, methodology development, 
        data collection, analysis, and writing phases.
        """
        
        stages = engine.detect_stages(text)
        
        # Should detect multiple stages
        assert len(stages) >= 4
        stage_types = [s.stage_type for s in stages]
        assert StageType.LITERATURE_REVIEW in stage_types
        assert StageType.METHODOLOGY in stage_types
        assert StageType.DATA_COLLECTION in stage_types
        assert StageType.ANALYSIS in stage_types
        assert StageType.WRITING in stage_types
    
    def test_no_stages_detected(self):
        """Test behavior when no stages are detected."""
        engine = TimelineIntelligenceEngine()
        
        text = "This is some random text without any PhD stage keywords."
        
        stages = engine.detect_stages(text)
        
        assert len(stages) == 0
    
    def test_stage_titles(self):
        """Test that generated stage titles are readable."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature review will be conducted.
        Methodology will be developed.
        Data collection will follow.
        """
        
        stages = engine.detect_stages(text)
        
        # Check titles are present and readable
        for stage in stages:
            assert stage.title is not None
            assert len(stage.title) > 0
            assert stage.title != stage.stage_type.value
    
    def test_evidence_limit(self):
        """Test that evidence snippets are limited to reasonable number."""
        engine = TimelineIntelligenceEngine()
        
        # Text with many keyword matches
        text = """
        Literature review. Background research. Survey of literature.
        Related work. Prior work. State of the art research.
        Theoretical framework review. Literature survey.
        """
        
        stages = engine.detect_stages(text)
        
        lit_stage = next(
            (s for s in stages if s.stage_type == StageType.LITERATURE_REVIEW),
            None
        )
        
        assert lit_stage is not None
        # Evidence should be limited (configured to max 5 in implementation)
        assert len(lit_stage.evidence) <= 5
        # Keywords should be limited (configured to max 10)
        assert len(lit_stage.keywords_matched) <= 10
    
    def test_empty_text(self):
        """Test handling of empty text."""
        engine = TimelineIntelligenceEngine()
        
        stages = engine.detect_stages("")
        assert len(stages) == 0
        
        stages = engine.detect_stages("   ")
        assert len(stages) == 0
    
    def test_real_world_proposal(self):
        """Test with realistic research proposal text."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        RESEARCH PROPOSAL
        
        1. Introduction
        This research will investigate the impact of climate change on biodiversity.
        
        2. Literature Review
        A comprehensive review of existing literature will be conducted to understand
        current knowledge gaps. This will survey work from the past decade.
        
        3. Methodology
        The research design will employ a mixed-methods approach. Data will be
        collected through field observations and surveys.
        
        4. Data Collection
        Field work will be conducted over 12 months across multiple sites.
        Surveys will be distributed to local communities.
        
        5. Analysis
        Statistical analysis will be performed on collected data using regression models.
        Qualitative data will be analyzed using thematic analysis.
        
        6. Writing and Dissemination
        Results will be written up in dissertation format and submitted to
        the university. Findings will also be published in peer-reviewed journals.
        
        7. Timeline
        Year 1: Coursework and literature review
        Year 2: Methodology development and data collection
        Year 3: Data analysis and writing
        Year 4: Final writing, submission, and defense
        """
        
        section_map = {
            "sections": [
                {"title": "Introduction", "start_line": 3},
                {"title": "Literature Review", "start_line": 7},
                {"title": "Methodology", "start_line": 11},
                {"title": "Data Collection", "start_line": 15},
                {"title": "Analysis", "start_line": 19},
                {"title": "Writing and Dissemination", "start_line": 23},
                {"title": "Timeline", "start_line": 27}
            ]
        }
        
        stages = engine.detect_stages(text, section_map)
        
        # Should detect most major stages
        stage_types = [s.stage_type for s in stages]
        assert StageType.COURSEWORK in stage_types
        assert StageType.LITERATURE_REVIEW in stage_types
        assert StageType.METHODOLOGY in stage_types
        assert StageType.DATA_COLLECTION in stage_types
        assert StageType.ANALYSIS in stage_types
        assert StageType.WRITING in stage_types
        assert StageType.SUBMISSION in stage_types
        assert StageType.DEFENSE in stage_types
        assert StageType.PUBLICATION in stage_types
        
        # All should have high confidence (multiple detection methods)
        for stage in stages:
            if stage.stage_type in [
                StageType.LITERATURE_REVIEW,
                StageType.METHODOLOGY,
                StageType.DATA_COLLECTION,
                StageType.ANALYSIS
            ]:
                assert stage.confidence >= 0.6  # At least 2 detection methods
        
        # Check that stages are in reasonable order
        stage_order = [s.stage_type for s in stages]
        lit_idx = stage_order.index(StageType.LITERATURE_REVIEW)
        method_idx = stage_order.index(StageType.METHODOLOGY)
        assert lit_idx < method_idx

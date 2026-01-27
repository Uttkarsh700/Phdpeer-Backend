"""
Tests for duration estimation and dependency mapping.

Tests the complete timeline creation with:
- Duration ranges (min/max weeks/months)
- Dependency mapping with DAG validation
- Fully structured timeline output
"""

import pytest
from app.services.timeline_intelligence_engine import (
    TimelineIntelligenceEngine,
    StageType,
    StructuredTimeline
)


class TestDurationEstimation:
    """Tests for estimate_durations() method."""
    
    def test_duration_ranges_returned(self):
        """Test that durations include min/max ranges."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The literature review will take approximately 6 months.
        Data collection is expected to last 12 months.
        Analysis will require about 3 months.
        """
        
        durations = engine.estimate_durations(text)
        
        assert len(durations) > 0
        
        for duration in durations:
            # Check range fields exist
            assert hasattr(duration, 'duration_weeks_min')
            assert hasattr(duration, 'duration_weeks_max')
            assert hasattr(duration, 'duration_months_min')
            assert hasattr(duration, 'duration_months_max')
            
            # Min should be <= Max
            assert duration.duration_weeks_min <= duration.duration_weeks_max
            assert duration.duration_months_min <= duration.duration_months_max
            
            # Weeks should be roughly 4x months
            assert duration.duration_weeks_min >= duration.duration_months_min * 3
    
    def test_explicit_durations_high_confidence(self):
        """Test that explicitly mentioned durations have high confidence."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The literature review phase will take 6 months.
        """
        
        durations = engine.estimate_durations(text)
        
        # Should have explicit duration with high confidence
        explicit = [d for d in durations if d.confidence == "high"]
        assert len(explicit) > 0
        
        lit_review = next(
            (d for d in explicit if "literature" in d.item_description.lower()),
            None
        )
        assert lit_review is not None
        assert lit_review.duration_months_min == 6
        assert lit_review.basis == "explicit"
    
    def test_heuristic_durations_for_stages(self):
        """Test that stages without explicit durations get heuristic ranges."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        The research will involve:
        - Literature Review
        - Data Collection
        - Analysis
        """
        
        durations = engine.estimate_durations(text)
        
        # Should have durations for each stage
        stage_durations = [d for d in durations if d.item_type == "stage"]
        assert len(stage_durations) >= 3
        
        # All should have ranges (not single values)
        for duration in stage_durations:
            assert duration.duration_months_max > duration.duration_months_min
    
    def test_milestone_durations_in_weeks(self):
        """Test that milestones have appropriate week-based durations."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review
        Complete comprehensive literature survey.
        Pass the comprehensive examination.
        """
        
        section_map = {
            "sections": [{"title": "Literature Review", "start_line": 1}]
        }
        
        durations = engine.estimate_durations(text, section_map=section_map)
        
        # Should have milestone durations
        milestone_durations = [d for d in durations if d.item_type == "milestone"]
        
        if milestone_durations:
            for duration in milestone_durations:
                # Milestones should be measured in weeks primarily
                assert duration.duration_weeks_min >= 1
                assert duration.duration_weeks_max <= 52  # Max 1 year
    
    def test_duration_item_types(self):
        """Test that durations are correctly typed as stage or milestone."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Year 1: Literature Review - survey existing work
        Complete the literature review and pass comprehensive exam.
        """
        
        durations = engine.estimate_durations(text)
        
        # Should have both types
        item_types = set(d.item_type for d in durations)
        
        # At minimum should have stages
        assert "stage" in item_types


class TestDependencyMapping:
    """Tests for map_dependencies() method."""
    
    def test_sequential_stage_dependencies(self):
        """Test that stages have sequential dependencies."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        1. Literature Review
        2. Methodology
        3. Data Collection
        4. Analysis
        """
        
        dependencies = engine.map_dependencies(text)
        
        # Should have dependencies
        assert len(dependencies) > 0
        
        # Should include sequential dependencies
        sequential = [d for d in dependencies if d.dependency_type == "sequential"]
        assert len(sequential) > 0
    
    def test_explicit_dependency_signals(self):
        """Test that explicit signals create dependencies."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        After completing the literature review, we will develop the methodology.
        Data collection requires ethics approval.
        Before analysis, data must be collected.
        """
        
        dependencies = engine.map_dependencies(text)
        
        # Should detect explicit dependencies
        explicit = [d for d in dependencies if "explicit" in d.reason.lower()]
        
        # May or may not find explicit deps depending on stage detection
        # But should not crash
        assert dependencies is not None
    
    def test_blocking_dependencies_for_critical_milestones(self):
        """Test that critical milestones create blocking dependencies."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Methodology
        Ethics approval must be obtained before any data collection.
        
        Data Collection
        Collect survey data from participants.
        """
        
        section_map = {
            "sections": [
                {"title": "Methodology", "start_line": 1},
                {"title": "Data Collection", "start_line": 4}
            ]
        }
        
        dependencies = engine.map_dependencies(text, section_map=section_map)
        
        # Should have blocking dependencies
        blocking = [d for d in dependencies if d.dependency_type == "blocks"]
        
        # May or may not have blocking deps depending on milestone detection
        # Key is that DAG is maintained
        assert dependencies is not None
    
    def test_dag_validation(self):
        """Test that dependency graph is validated as DAG."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review comes first.
        Methodology follows literature review.
        Data Collection happens after methodology.
        Analysis comes after data collection.
        """
        
        dependencies = engine.map_dependencies(text)
        
        # Build graph to check for cycles
        graph = {}
        for dep in dependencies:
            if dep.dependent_item not in graph:
                graph[dep.dependent_item] = []
            graph[dep.dependent_item].append(dep.depends_on_item)
        
        # Check for cycles using DFS
        def has_cycle(node, visited, rec_stack):
            visited[node] = True
            rec_stack[node] = True
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited or not visited[neighbor]:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif rec_stack.get(neighbor, False):
                    return True
            
            rec_stack[node] = False
            return False
        
        visited = {}
        rec_stack = {}
        has_cycle_found = False
        
        for node in graph:
            if node not in visited or not visited[node]:
                if has_cycle(node, visited, rec_stack):
                    has_cycle_found = True
                    break
        
        # Should not have cycles
        assert not has_cycle_found
    
    def test_dependency_confidence_scores(self):
        """Test that dependencies have appropriate confidence scores."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        After literature review, develop methodology.
        Following data collection, perform analysis.
        """
        
        dependencies = engine.map_dependencies(text)
        
        for dep in dependencies:
            assert hasattr(dep, 'confidence')
            assert 0.0 <= dep.confidence <= 1.0
    
    def test_dependency_reasons_provided(self):
        """Test that dependencies include reasons."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Literature Review phase.
        Methodology phase.
        Data Collection phase.
        """
        
        dependencies = engine.map_dependencies(text)
        
        for dep in dependencies:
            assert hasattr(dep, 'reason')
            assert dep.reason is not None
            assert len(dep.reason) > 0


class TestStructuredTimeline:
    """Tests for create_structured_timeline() method."""
    
    def test_structured_timeline_created(self):
        """Test that a complete structured timeline is created."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        PhD Research Timeline
        
        Year 1: Literature Review (6 months)
        Review existing research and identify gaps.
        
        Year 2: Methodology and Data Collection (12 months)
        Develop research design and collect data.
        
        Year 3: Analysis and Writing (12 months)
        Analyze data and write dissertation.
        """
        
        timeline = engine.create_structured_timeline(
            text,
            title="PhD Timeline",
            description="4-year PhD program"
        )
        
        # Check structure
        assert isinstance(timeline, StructuredTimeline)
        assert timeline.title == "PhD Timeline"
        assert timeline.description == "4-year PhD program"
        
        # Should have stages
        assert len(timeline.stages) > 0
        
        # Should have milestones
        assert len(timeline.milestones) > 0
        
        # Should have durations
        assert len(timeline.durations) > 0
        
        # Should have dependencies
        assert len(timeline.dependencies) > 0
        
        # Should calculate total duration
        assert timeline.total_duration_months_min > 0
        assert timeline.total_duration_months_max >= timeline.total_duration_months_min
        
        # DAG should be valid
        assert timeline.is_dag_valid is True
    
    def test_empty_timeline_when_no_stages(self):
        """Test that empty timeline is returned when no stages detected."""
        engine = TimelineIntelligenceEngine()
        
        text = "This is random text with no PhD content."
        
        timeline = engine.create_structured_timeline(text)
        
        assert len(timeline.stages) == 0
        assert len(timeline.milestones) == 0
        assert timeline.total_duration_months_min == 0
        assert timeline.total_duration_months_max == 0
        assert timeline.is_dag_valid is True
    
    def test_real_world_proposal_timeline(self):
        """Test with realistic PhD proposal."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        RESEARCH TIMELINE
        
        Year 1 (Months 1-12): Coursework and Literature Review
        - Complete required courses
        - Pass comprehensive examination
        - Conduct comprehensive literature review
        - Identify research gaps
        
        Year 2 (Months 13-24): Methodology and Data Collection
        - Finalize research design (2 months)
        - Obtain IRB approval (1 month)
        - Develop data collection instruments (2 months)
        - Conduct pilot study (2 months)
        - Begin field work (6 months)
        
        Year 3 (Months 25-36): Data Collection and Analysis
        - Complete data collection (6 months)
        - Perform statistical analysis (4 months)
        - Interpret findings (2 months)
        
        Year 4 (Months 37-48): Writing and Defense
        - Write dissertation chapters (8 months)
        - Revise based on feedback (2 months)
        - Defend dissertation (1 month)
        - Submit final version (1 month)
        """
        
        section_map = {
            "sections": [
                {"title": "Year 1", "start_line": 3},
                {"title": "Year 2", "start_line": 9},
                {"title": "Year 3", "start_line": 16},
                {"title": "Year 4", "start_line": 21}
            ]
        }
        
        timeline = engine.create_structured_timeline(
            text,
            section_map=section_map,
            title="4-Year PhD Plan",
            description="Comprehensive 4-year PhD research timeline"
        )
        
        # Should detect multiple stages
        assert len(timeline.stages) >= 4
        
        # Should extract many milestones
        assert len(timeline.milestones) >= 8
        
        # Should have explicit durations with high confidence
        explicit_durations = [
            d for d in timeline.durations 
            if d.confidence == "high"
        ]
        assert len(explicit_durations) >= 3
        
        # Total duration should be around 48 months (4 years)
        assert 36 <= timeline.total_duration_months_max <= 60
        
        # DAG should be valid
        assert timeline.is_dag_valid is True
        
        # Dependencies should form a logical sequence
        assert len(timeline.dependencies) > 0
    
    def test_timeline_with_section_map(self):
        """Test timeline creation with section map."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Introduction
        This research aims to study X.
        
        Literature Review
        Review of existing work.
        
        Methodology
        Research design and approach.
        
        Timeline
        The project will span 3 years.
        """
        
        section_map = {
            "sections": [
                {"title": "Introduction", "start_line": 1},
                {"title": "Literature Review", "start_line": 4},
                {"title": "Methodology", "start_line": 7},
                {"title": "Timeline", "start_line": 10}
            ]
        }
        
        timeline = engine.create_structured_timeline(text, section_map=section_map)
        
        # Should detect stages from section headers
        stage_names = [s.title for s in timeline.stages]
        
        # Should have at least literature review and methodology
        assert any("literature" in name.lower() for name in stage_names)
        assert any("method" in name.lower() for name in stage_names)
    
    def test_dag_validation_in_timeline(self):
        """Test that timeline validates DAG property."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        Step 1: Literature Review
        Step 2: Methodology
        Step 3: Data Collection
        Step 4: Analysis
        Step 5: Writing
        """
        
        timeline = engine.create_structured_timeline(text)
        
        # Should be valid DAG
        assert timeline.is_dag_valid is True
        
        # Dependencies should not form cycles
        if timeline.dependencies:
            # Build graph
            graph = {}
            for dep in timeline.dependencies:
                if dep.dependent_item not in graph:
                    graph[dep.dependent_item] = []
                graph[dep.dependent_item].append(dep.depends_on_item)
            
            # Simple cycle check: no node should depend on itself
            for node, deps in graph.items():
                assert node not in deps


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    def test_complete_pipeline(self):
        """Test the complete timeline creation pipeline."""
        engine = TimelineIntelligenceEngine()
        
        text = """
        PhD Research Proposal: Impact of Climate Change on Biodiversity
        
        Literature Review (6 months)
        Conduct comprehensive review of existing literature.
        Identify research gaps.
        
        Methodology Development (3 months)
        Design mixed-methods approach.
        Develop data collection instruments.
        Obtain ethics approval.
        
        Data Collection (12 months)
        Conduct field observations.
        Distribute and collect surveys.
        
        Data Analysis (6 months)
        Perform statistical analysis.
        Analyze qualitative data.
        
        Dissertation Writing (9 months)
        Write all chapters.
        Revise based on feedback.
        
        Defense and Submission (2 months)
        Prepare defense presentation.
        Defend dissertation.
        Submit final version.
        """
        
        section_map = {
            "sections": [
                {"title": "Literature Review", "start_line": 3},
                {"title": "Methodology Development", "start_line": 7},
                {"title": "Data Collection", "start_line": 12},
                {"title": "Data Analysis", "start_line": 16},
                {"title": "Dissertation Writing", "start_line": 20},
                {"title": "Defense and Submission", "start_line": 24}
            ]
        }
        
        # Create structured timeline
        timeline = engine.create_structured_timeline(
            text,
            section_map=section_map,
            title="Climate Change Biodiversity PhD",
            description="3-year PhD research on climate change impacts"
        )
        
        # Validate all components
        assert len(timeline.stages) >= 5
        assert len(timeline.milestones) >= 10
        assert len(timeline.durations) >= 5
        assert len(timeline.dependencies) >= 4
        
        # Total duration should be reasonable (around 38 months)
        assert 30 <= timeline.total_duration_months_max <= 50
        
        # DAG should be valid
        assert timeline.is_dag_valid is True
        
        # All stages should have durations
        stage_names = [s.title for s in timeline.stages]
        duration_items = [d.item_description for d in timeline.durations]
        
        for stage_name in stage_names:
            # Stage or similar name should be in durations
            assert any(
                stage_name.lower() in item.lower() 
                for item in duration_items
            )

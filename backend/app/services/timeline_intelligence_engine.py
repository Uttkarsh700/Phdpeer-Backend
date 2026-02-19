"""Timeline Intelligence Engine for extracting timeline information from text.

This module provides LLM-powered timeline extraction with fallback to defaults.
Uses Claude via the Anthropic API for intelligent extraction.
"""
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class StageType(str, Enum):
    """Enumeration of PhD timeline stages."""
    COURSEWORK = "coursework"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    WRITING = "writing"
    SUBMISSION = "submission"
    DEFENSE = "defense"
    PUBLICATION = "publication"
    OTHER = "other"


@dataclass
class TextSegment:
    """Represents a segment of text."""
    content: str
    segment_index: int
    line_numbers: tuple
    segment_type: str = "paragraph"  # paragraph, section, list_item
    
    def __str__(self) -> str:
        return f"Segment {self.segment_index}: {self.content[:50]}..."


@dataclass
class EvidenceSnippet:
    """Represents evidence for a detected stage."""
    text: str
    source: str  # "section_header", "keyword_cluster", "temporal_phrase"
    location: str  # e.g., "Section 2.1", "Line 45-50"
    
    def __str__(self) -> str:
        return f"[{self.source}] {self.text[:50]}..."


@dataclass
class DetectedStage:
    """Represents a detected timeline stage."""
    stage_type: StageType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    keywords_matched: List[str] = field(default_factory=list)
    source_segments: List[int] = field(default_factory=list)
    evidence: List[EvidenceSnippet] = field(default_factory=list)
    order_hint: int = 0  # Suggested order in timeline
    
    def __str__(self) -> str:
        return f"{self.stage_type.value}: {self.title} (confidence: {self.confidence:.2f})"


@dataclass
class ExtractedMilestone:
    """Represents an extracted milestone."""
    name: str
    description: str
    stage: str  # Associated stage name
    milestone_type: str  # deliverable, exam, review, publication, etc.
    evidence_snippet: str
    keywords: List[str] = field(default_factory=list)
    source_segment: Optional[int] = None
    is_critical: bool = False
    confidence: float = 0.5
    
    def __str__(self) -> str:
        return f"{'[CRITICAL] ' if self.is_critical else ''}{self.name}"


@dataclass
class DurationEstimate:
    """Represents a duration estimate with range."""
    item_description: str
    item_type: str  # "stage" or "milestone"
    duration_weeks_min: int
    duration_weeks_max: int
    duration_months_min: int
    duration_months_max: int
    confidence: str  # low, medium, high
    basis: str  # explicit, pattern, heuristic, default
    source_text: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.item_description}: {self.duration_months_min}-{self.duration_months_max} months ({self.confidence})"


@dataclass
class Dependency:
    """Represents a dependency between stages or milestones."""
    dependent_item: str
    depends_on_item: str
    dependency_type: str  # sequential, prerequisite, parallel, blocks
    confidence: float
    reason: str = ""  # Why this dependency exists
    
    def __str__(self) -> str:
        return f"{self.dependent_item} -> {self.depends_on_item} ({self.dependency_type})"


@dataclass
class StructuredTimeline:
    """Complete structured timeline ready for DraftTimeline creation."""
    title: str
    description: str
    stages: List[DetectedStage]
    milestones: List[ExtractedMilestone]
    durations: List[DurationEstimate]
    dependencies: List[Dependency]
    total_duration_months_min: int
    total_duration_months_max: int
    is_dag_valid: bool
    
    def __str__(self) -> str:
        return f"Timeline: {self.title} ({len(self.stages)} stages, {len(self.milestones)} milestones)"


logger = logging.getLogger(__name__)


class TimelineIntelligenceEngine:
    """
    LLM-powered engine for extracting timeline information from PhD documents.

    Uses Claude via the Anthropic API for intelligent extraction with
    fallback to generic defaults if LLM calls fail.

    Architecture:
    - First LLM call: detect_stages + extract_milestones (combined, cached)
    - Second LLM call: estimate_durations + map_dependencies (combined, cached)
    - Validators run after each call to fix any issues
    - Feedback Engine applies learned corrections to duration estimates
    """

    def __init__(self, db: Optional[Any] = None, apply_feedback_adjustments: bool = True):
        """
        Initialize the timeline intelligence engine with LLM client.

        Args:
            db: Optional database session for feedback engine
            apply_feedback_adjustments: Whether to apply learned feedback adjustments
        """
        self._llm_client = None
        self._llm_available = True
        self._db = db
        self._apply_feedback_adjustments = apply_feedback_adjustments
        self._feedback_engine = None

        # Cache for LLM results to avoid duplicate calls
        self._stages_milestones_cache: Dict[str, Tuple[List[DetectedStage], List[ExtractedMilestone]]] = {}
        self._durations_dependencies_cache: Dict[str, Tuple[List[DurationEstimate], List[Dependency]]] = {}

        # Try to initialize LLM client
        try:
            from app.services.llm.client import LLMClient, LLMError
            self._llm_client = LLMClient()
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.warning(f"LLM client initialization failed, using fallback mode: {e}")
            self._llm_available = False

        # Try to initialize feedback engine if db provided
        if db and apply_feedback_adjustments:
            try:
                from app.services.feedback_engine import FeedbackEngine
                self._feedback_engine = FeedbackEngine(db, use_llm=False)
                logger.info("Feedback engine initialized for learned adjustments")
            except Exception as e:
                logger.warning(f"Feedback engine initialization failed: {e}")
                self._feedback_engine = None

    def _get_cache_key(self, text: str, section_map: Optional[Dict] = None) -> str:
        """Generate a cache key from text and section_map."""
        content = text + str(section_map or {})
        return hashlib.md5(content.encode()).hexdigest()

    def detect_stages(
        self,
        text: str,
        section_map: Optional[Dict] = None
    ) -> List[DetectedStage]:
        """
        Detect timeline stages using LLM with fallback to defaults.

        This method calls the LLM to extract both stages and milestones,
        caching milestones for the subsequent extract_milestones call.

        Args:
            text: Plain text input from document
            section_map: Optional section structure from document processing

        Returns:
            List of DetectedStage objects sorted by order_hint
        """
        cache_key = self._get_cache_key(text, section_map)

        # Check cache first
        if cache_key in self._stages_milestones_cache:
            stages, _ = self._stages_milestones_cache[cache_key]
            logger.debug("Returning cached stages")
            return stages

        # Try LLM extraction
        if self._llm_available and self._llm_client:
            try:
                stages, milestones = self._extract_stages_and_milestones_llm(text, section_map)
                self._stages_milestones_cache[cache_key] = (stages, milestones)
                return stages
            except Exception as e:
                logger.error(f"LLM extraction failed, using fallback: {e}")

        # Fallback to generic PhD stages
        stages, milestones = self._get_fallback_stages_and_milestones()
        self._stages_milestones_cache[cache_key] = (stages, milestones)
        return stages

    def extract_milestones(
        self,
        text: str,
        section_map: Optional[Dict] = None
    ) -> List[ExtractedMilestone]:
        """
        Extract milestones for detected stages.

        Returns cached milestones from the combined LLM call made by detect_stages.
        If detect_stages hasn't been called yet, calls it first.

        Args:
            text: Plain text input from document
            section_map: Optional section structure from document processing

        Returns:
            List of ExtractedMilestone objects
        """
        cache_key = self._get_cache_key(text, section_map)

        # Check cache first
        if cache_key in self._stages_milestones_cache:
            _, milestones = self._stages_milestones_cache[cache_key]
            logger.debug("Returning cached milestones")
            return milestones

        # Cache miss - call detect_stages to populate cache
        self.detect_stages(text, section_map)

        # Now return cached milestones
        if cache_key in self._stages_milestones_cache:
            _, milestones = self._stages_milestones_cache[cache_key]
            return milestones

        # Should not reach here, but fallback just in case
        _, milestones = self._get_fallback_stages_and_milestones()
        return milestones

    def estimate_durations(
        self,
        text: str,
        stages: Optional[List[DetectedStage]] = None,
        milestones: Optional[List[ExtractedMilestone]] = None,
        section_map: Optional[Dict] = None,
        discipline: Optional[str] = None
    ) -> List[DurationEstimate]:
        """
        Estimate duration ranges for stages and milestones using LLM.

        This method calls the LLM to extract both durations and dependencies,
        caching dependencies for the subsequent map_dependencies call.
        After extraction, applies learned feedback adjustments if available.

        Args:
            text: Plain text input from document
            stages: Pre-detected stages (will detect if not provided)
            milestones: Pre-extracted milestones (will extract if not provided)
            section_map: Optional section structure
            discipline: Optional field of study for calibrated estimates

        Returns:
            List of DurationEstimate objects (with feedback adjustments applied)
        """
        # Ensure stages and milestones are available
        if stages is None:
            stages = self.detect_stages(text, section_map)
        if milestones is None:
            milestones = self.extract_milestones(text, section_map)

        # Create cache key including discipline
        cache_key = self._get_cache_key(text, section_map) + str(discipline or "")

        # Check cache first
        if cache_key in self._durations_dependencies_cache:
            durations, _ = self._durations_dependencies_cache[cache_key]
            logger.debug("Returning cached durations")
            return durations

        # Try LLM extraction
        if self._llm_available and self._llm_client:
            try:
                durations, dependencies = self._extract_durations_and_dependencies_llm(
                    text, stages, milestones, section_map, discipline
                )
            except Exception as e:
                logger.error(f"LLM duration extraction failed, using fallback: {e}")
                durations, dependencies = self._get_fallback_durations_and_dependencies(stages, milestones)
        else:
            # Fallback to default durations
            durations, dependencies = self._get_fallback_durations_and_dependencies(stages, milestones)

        # Apply learned feedback adjustments if feedback engine is available
        if self._feedback_engine and self._apply_feedback_adjustments:
            try:
                _, _, durations = self._feedback_engine.apply_learned_adjustments(
                    stages, milestones, durations, discipline
                )
                logger.info("Applied learned feedback adjustments to durations")
            except Exception as e:
                logger.warning(f"Failed to apply feedback adjustments: {e}")

        self._durations_dependencies_cache[cache_key] = (durations, dependencies)
        return durations

    def map_dependencies(
        self,
        text: str,
        stages: Optional[List[DetectedStage]] = None,
        milestones: Optional[List[ExtractedMilestone]] = None,
        section_map: Optional[Dict] = None
    ) -> List[Dependency]:
        """
        Map dependencies between stages and milestones.

        Returns cached dependencies from the combined LLM call made by estimate_durations.
        If estimate_durations hasn't been called yet, calls it first.

        Args:
            text: Plain text input from document
            stages: Pre-detected stages (will detect if not provided)
            milestones: Pre-extracted milestones (will extract if not provided)
            section_map: Optional section structure

        Returns:
            List of Dependency objects (guaranteed to form valid DAG)
        """
        # Ensure stages and milestones are available
        if stages is None:
            stages = self.detect_stages(text, section_map)
        if milestones is None:
            milestones = self.extract_milestones(text, section_map)

        cache_key = self._get_cache_key(text, section_map)

        # Check cache first (without discipline suffix for dependencies)
        for key in self._durations_dependencies_cache:
            if key.startswith(cache_key):
                _, dependencies = self._durations_dependencies_cache[key]
                logger.debug("Returning cached dependencies")
                return dependencies

        # Cache miss - call estimate_durations to populate cache
        self.estimate_durations(text, stages, milestones, section_map)

        # Now return cached dependencies
        for key in self._durations_dependencies_cache:
            if key.startswith(cache_key):
                _, dependencies = self._durations_dependencies_cache[key]
                return dependencies

        # Should not reach here, but fallback just in case
        _, dependencies = self._get_fallback_durations_and_dependencies(stages, milestones)
        return dependencies

    def _extract_stages_and_milestones_llm(
        self,
        text: str,
        section_map: Optional[Dict]
    ) -> Tuple[List[DetectedStage], List[ExtractedMilestone]]:
        """
        Extract stages and milestones using LLM.

        Makes a single LLM call with the combined prompt, then parses
        and validates the results.
        """
        from app.services.llm.prompts import build_stages_and_milestones_prompt
        from app.services.llm.parsers import parse_stages, parse_milestones
        from app.services.llm.validators import validate_output, validate_stage_milestone_consistency

        # Build prompt
        system_prompt, user_prompt = build_stages_and_milestones_prompt(text, section_map)

        # Call LLM
        logger.info("Calling LLM for stages and milestones extraction")
        response = self._llm_client.call(system_prompt, user_prompt)

        # Parse response
        stages = parse_stages(response)
        milestones = parse_milestones(response)

        logger.info(f"LLM returned {len(stages)} stages and {len(milestones)} milestones")

        # Validate and fix issues
        stages, milestones, _, _ = validate_output(stages, milestones, [], [])
        stages, milestones = validate_stage_milestone_consistency(stages, milestones)

        return stages, milestones

    def _extract_durations_and_dependencies_llm(
        self,
        text: str,
        stages: List[DetectedStage],
        milestones: List[ExtractedMilestone],
        section_map: Optional[Dict],
        discipline: Optional[str]
    ) -> Tuple[List[DurationEstimate], List[Dependency]]:
        """
        Extract durations and dependencies using LLM.

        Makes a single LLM call with the combined prompt, then parses
        and validates the results.
        """
        from app.services.llm.prompts import build_durations_and_dependencies_prompt
        from app.services.llm.parsers import parse_durations, parse_dependencies
        from app.services.llm.validators import validate_output

        # Convert stages and milestones to JSON format for the prompt
        stages_json = [
            {
                "title": s.title,
                "stage_type": s.stage_type.value,
                "description": s.description,
            }
            for s in stages
        ]
        milestones_json = [
            {
                "name": m.name,
                "stage": m.stage,
                "milestone_type": m.milestone_type,
                "is_critical": m.is_critical,
            }
            for m in milestones
        ]

        # Build prompt
        system_prompt, user_prompt = build_durations_and_dependencies_prompt(
            text, stages_json, milestones_json, section_map, discipline
        )

        # Call LLM
        logger.info("Calling LLM for durations and dependencies extraction")
        response = self._llm_client.call(system_prompt, user_prompt)

        # Parse response
        durations = parse_durations(response)
        dependencies = parse_dependencies(response)

        logger.info(f"LLM returned {len(durations)} durations and {len(dependencies)} dependencies")

        # Validate and fix issues
        _, _, durations, dependencies = validate_output(stages, milestones, durations, dependencies)

        return durations, dependencies

    def _get_fallback_stages_and_milestones(
        self
    ) -> Tuple[List[DetectedStage], List[ExtractedMilestone]]:
        """
        Generate fallback stages and milestones when LLM is unavailable.

        Returns a generic PhD timeline structure.
        """
        logger.info("Using fallback stages and milestones")

        # Generic PhD stages
        stages = [
            DetectedStage(
                stage_type=StageType.LITERATURE_REVIEW,
                title="Literature Review",
                description="Comprehensive review of existing research and identification of gaps",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=1
            ),
            DetectedStage(
                stage_type=StageType.METHODOLOGY,
                title="Methodology Development",
                description="Design and validation of research methodology",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=2
            ),
            DetectedStage(
                stage_type=StageType.DATA_COLLECTION,
                title="Data Collection",
                description="Primary data gathering and experimental work",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=3
            ),
            DetectedStage(
                stage_type=StageType.ANALYSIS,
                title="Data Analysis",
                description="Analysis and interpretation of collected data",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=4
            ),
            DetectedStage(
                stage_type=StageType.WRITING,
                title="Writing Phase",
                description="Dissertation writing and revision",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=5
            ),
            DetectedStage(
                stage_type=StageType.DEFENSE,
                title="Defense Preparation",
                description="Preparation and completion of dissertation defense",
                confidence=0.5,
                keywords_matched=[],
                source_segments=[],
                evidence=[],
                order_hint=6
            ),
        ]

        # Generic milestones (2 per stage)
        milestones = []
        for stage in stages:
            milestones.extend([
                ExtractedMilestone(
                    name=f"Begin {stage.title}",
                    description=f"Initiate work on {stage.title.lower()}",
                    stage=stage.title,
                    milestone_type="deliverable",
                    evidence_snippet=stage.description,
                    keywords=[],
                    source_segment=None,
                    is_critical=False,
                    confidence=0.4
                ),
                ExtractedMilestone(
                    name=f"Complete {stage.title}",
                    description=f"Finish all activities in {stage.title.lower()}",
                    stage=stage.title,
                    milestone_type="deliverable",
                    evidence_snippet=stage.description,
                    keywords=[],
                    source_segment=None,
                    is_critical=True,
                    confidence=0.4
                ),
            ])

        return stages, milestones

    def _get_fallback_durations_and_dependencies(
        self,
        stages: List[DetectedStage],
        milestones: List[ExtractedMilestone]
    ) -> Tuple[List[DurationEstimate], List[Dependency]]:
        """
        Generate fallback durations and dependencies when LLM is unavailable.

        Returns default duration estimates and sequential dependencies.
        """
        logger.info("Using fallback durations and dependencies")

        # Default durations by stage type (months: min, max)
        default_stage_durations = {
            StageType.COURSEWORK: (12, 24),
            StageType.LITERATURE_REVIEW: (3, 9),
            StageType.METHODOLOGY: (2, 6),
            StageType.DATA_COLLECTION: (6, 18),
            StageType.ANALYSIS: (3, 9),
            StageType.WRITING: (6, 15),
            StageType.SUBMISSION: (1, 2),
            StageType.DEFENSE: (1, 3),
            StageType.PUBLICATION: (3, 12),
            StageType.OTHER: (3, 6),
        }

        durations = []

        # Stage durations
        for stage in stages:
            min_months, max_months = default_stage_durations.get(stage.stage_type, (3, 6))
            durations.append(DurationEstimate(
                item_description=stage.title,
                item_type="stage",
                duration_weeks_min=min_months * 4,
                duration_weeks_max=max_months * 4,
                duration_months_min=min_months,
                duration_months_max=max_months,
                confidence="low",
                basis="llm_estimate",
                source_text=None
            ))

        # Milestone durations (default 2-4 weeks)
        for milestone in milestones:
            weeks_min = 2
            weeks_max = 4 if not milestone.is_critical else 6
            durations.append(DurationEstimate(
                item_description=milestone.name,
                item_type="milestone",
                duration_weeks_min=weeks_min,
                duration_weeks_max=weeks_max,
                duration_months_min=1,
                duration_months_max=max(1, weeks_max // 4),
                confidence="low",
                basis="llm_estimate",
                source_text=None
            ))

        # Sequential dependencies between stages
        dependencies = []
        sorted_stages = sorted(stages, key=lambda s: s.order_hint)

        for i in range(len(sorted_stages) - 1):
            dependencies.append(Dependency(
                dependent_item=sorted_stages[i + 1].title,
                depends_on_item=sorted_stages[i].title,
                dependency_type="sequential",
                confidence=0.7,
                reason="Sequential PhD progression"
            ))

        # Milestone dependencies within stages
        milestones_by_stage: Dict[str, List[ExtractedMilestone]] = {}
        for m in milestones:
            if m.stage not in milestones_by_stage:
                milestones_by_stage[m.stage] = []
            milestones_by_stage[m.stage].append(m)

        for stage_title, stage_milestones in milestones_by_stage.items():
            for i in range(len(stage_milestones) - 1):
                dependencies.append(Dependency(
                    dependent_item=stage_milestones[i + 1].name,
                    depends_on_item=stage_milestones[i].name,
                    dependency_type="sequential",
                    confidence=0.5,
                    reason=f"Sequential milestones in {stage_title}"
                ))

        return durations, dependencies

    def create_structured_timeline(
        self,
        text: str,
        section_map: Optional[Dict] = None,
        title: str = "PhD Timeline",
        description: str = ""
    ) -> StructuredTimeline:
        """
        Create a fully structured timeline from text.

        Orchestrates all extraction methods and returns a complete timeline.

        Args:
            text: Plain text input from document
            section_map: Optional section structure
            title: Timeline title
            description: Timeline description

        Returns:
            StructuredTimeline object ready for DraftTimeline creation
        """
        # Extract all components
        stages = self.detect_stages(text, section_map)

        if not stages:
            return StructuredTimeline(
                title=title,
                description=description or "No stages detected in document",
                stages=[],
                milestones=[],
                durations=[],
                dependencies=[],
                total_duration_months_min=0,
                total_duration_months_max=0,
                is_dag_valid=True
            )

        milestones = self.extract_milestones(text, section_map)
        durations = self.estimate_durations(text, stages, milestones, section_map)
        dependencies = self.map_dependencies(text, stages, milestones, section_map)

        # Calculate total duration
        stage_durations = [d for d in durations if d.item_type == "stage"]
        if stage_durations:
            total_min = sum(d.duration_months_min for d in stage_durations)
            total_max = sum(d.duration_months_max for d in stage_durations)
        else:
            total_min = 0
            total_max = 0

        return StructuredTimeline(
            title=title,
            description=description or f"PhD timeline with {len(stages)} stages and {len(milestones)} milestones",
            stages=stages,
            milestones=milestones,
            durations=durations,
            dependencies=dependencies,
            total_duration_months_min=total_min,
            total_duration_months_max=total_max,
            is_dag_valid=True  # Validated by validators
        )

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._stages_milestones_cache.clear()
        self._durations_dependencies_cache.clear()
        logger.debug("Cache cleared")

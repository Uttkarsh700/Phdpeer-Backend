"""Validators to ensure LLM output is consistent and correct.

These validators FIX issues rather than raise exceptions, providing resilient output.
"""
import logging
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple

from app.services.timeline_intelligence_engine import (
    DetectedStage,
    ExtractedMilestone,
    DurationEstimate,
    Dependency,
    StageType,
)

logger = logging.getLogger(__name__)


def validate_output(
    stages: List[DetectedStage],
    milestones: List[ExtractedMilestone],
    durations: List[DurationEstimate],
    dependencies: List[Dependency]
) -> Tuple[List[DetectedStage], List[ExtractedMilestone], List[DurationEstimate], List[Dependency]]:
    """
    Validate and fix all output data.

    This function FIXES issues rather than raising exceptions.
    All returned data is guaranteed to be consistent and valid.

    Validations performed:
    1. Every stage has valid StageType
    2. Every milestone's .stage matches a real stage title
    3. Every milestone has non-empty evidence_snippet
    4. Every stage has a matching duration estimate
    5. All duration_months_min > 0
    6. duration_months_max >= duration_months_min
    7. Dependencies form a valid DAG (cycles removed)

    Args:
        stages: List of detected stages
        milestones: List of extracted milestones
        durations: List of duration estimates
        dependencies: List of dependencies

    Returns:
        Tuple of (stages, milestones, durations, dependencies) - all validated and fixed
    """
    # Step 1: Validate stages
    stages = _validate_stages(stages)

    # Step 2: Validate milestones (needs stage titles)
    stage_titles = {s.title for s in stages}
    milestones = _validate_milestones(milestones, stages, stage_titles)

    # Step 3: Validate durations (needs stage titles and milestone names)
    milestone_names = {m.name for m in milestones}
    durations = _validate_durations(durations, stages, milestones, stage_titles, milestone_names)

    # Step 4: Validate dependencies (needs all item names)
    all_item_names = stage_titles | milestone_names
    dependencies = _validate_dependencies(dependencies, all_item_names)

    return stages, milestones, durations, dependencies


def _validate_stages(stages: List[DetectedStage]) -> List[DetectedStage]:
    """
    Validate and fix stages.

    Ensures every stage has a valid StageType.
    """
    validated = []

    for stage in stages:
        # Check StageType is valid
        if not isinstance(stage.stage_type, StageType):
            try:
                stage.stage_type = StageType(str(stage.stage_type).lower())
            except (ValueError, AttributeError):
                logger.warning(f"Invalid stage_type for '{stage.title}', setting to OTHER")
                # Create new stage with fixed type (dataclass is not mutable by default)
                stage = DetectedStage(
                    stage_type=StageType.OTHER,
                    title=stage.title,
                    description=stage.description,
                    confidence=stage.confidence,
                    keywords_matched=stage.keywords_matched,
                    source_segments=stage.source_segments,
                    evidence=stage.evidence,
                    order_hint=stage.order_hint
                )

        validated.append(stage)

    return validated


def _validate_milestones(
    milestones: List[ExtractedMilestone],
    stages: List[DetectedStage],
    stage_titles: Set[str]
) -> List[ExtractedMilestone]:
    """
    Validate and fix milestones.

    - Ensures .stage matches a real stage title
    - Ensures evidence_snippet is non-empty
    """
    if not stages:
        logger.warning("No stages available, cannot validate milestones")
        return milestones

    validated = []

    for milestone in milestones:
        needs_fix = False
        new_stage = milestone.stage
        new_evidence = milestone.evidence_snippet

        # Check if stage matches a real stage title
        if milestone.stage not in stage_titles:
            new_stage = _find_closest_stage(milestone.stage, stages)
            logger.warning(
                f"Milestone '{milestone.name}' has invalid stage '{milestone.stage}', "
                f"reassigning to '{new_stage}'"
            )
            needs_fix = True

        # Check evidence_snippet is non-empty
        if not milestone.evidence_snippet or not milestone.evidence_snippet.strip():
            new_evidence = milestone.description if milestone.description else f"Milestone: {milestone.name}"
            logger.warning(
                f"Milestone '{milestone.name}' has empty evidence_snippet, using description"
            )
            needs_fix = True

        if needs_fix:
            milestone = ExtractedMilestone(
                name=milestone.name,
                description=milestone.description,
                stage=new_stage,
                milestone_type=milestone.milestone_type,
                evidence_snippet=new_evidence,
                keywords=milestone.keywords,
                source_segment=milestone.source_segment,
                is_critical=milestone.is_critical,
                confidence=milestone.confidence
            )

        validated.append(milestone)

    return validated


def _find_closest_stage(target: str, stages: List[DetectedStage]) -> str:
    """
    Find the closest matching stage title using fuzzy matching.

    Uses multiple matching strategies:
    1. Exact match
    2. Substring containment
    3. Token overlap (word-level matching)
    4. Character-level fuzzy matching (SequenceMatcher)

    Falls back to first stage if no good match found.
    """
    if not stages:
        return target

    target_lower = target.lower().strip()
    stage_titles = [s.title for s in stages]

    # Strategy 1: Exact match (case-insensitive)
    for stage in stages:
        if target_lower == stage.title.lower():
            return stage.title

    # Strategy 2: Substring containment
    for stage in stages:
        stage_lower = stage.title.lower()
        if target_lower in stage_lower or stage_lower in target_lower:
            return stage.title

    # Strategy 3: Token overlap - match individual words
    target_tokens = set(_tokenize(target_lower))
    best_token_match = None
    best_token_score = 0

    for stage in stages:
        stage_tokens = set(_tokenize(stage.title.lower()))
        # Calculate Jaccard similarity
        intersection = len(target_tokens & stage_tokens)
        union = len(target_tokens | stage_tokens)
        if union > 0:
            score = intersection / union
            # Also give bonus for any shared tokens
            if intersection > 0:
                score += 0.1 * intersection
            if score > best_token_score:
                best_token_score = score
                best_token_match = stage.title

    # If good token overlap, use that
    if best_token_score >= 0.3:
        return best_token_match

    # Strategy 4: Character-level fuzzy matching
    best_match = stages[0].title
    best_ratio = 0.0

    for stage in stages:
        ratio = SequenceMatcher(None, target_lower, stage.title.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = stage.title

    # If ratio is reasonable, use it
    if best_ratio >= 0.4:
        return best_match

    # Strategy 5: Partial token matching - if any significant word matches
    significant_target_tokens = {t for t in target_tokens if len(t) > 3}
    for stage in stages:
        stage_tokens = set(_tokenize(stage.title.lower()))
        significant_stage_tokens = {t for t in stage_tokens if len(t) > 3}
        if significant_target_tokens & significant_stage_tokens:
            return stage.title

    # Fallback: use the best fuzzy match we found, or first stage
    if best_ratio >= 0.25:
        return best_match

    logger.warning(f"No good match for stage '{target}', using first stage")
    return stages[0].title


def _tokenize(text: str) -> List[str]:
    """
    Tokenize text into words, removing common stop words and short tokens.
    """
    import re
    # Split on non-alphanumeric characters
    tokens = re.split(r'[^a-z0-9]+', text.lower())
    # Filter out empty strings and very short tokens
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    return [t for t in tokens if t and len(t) > 1 and t not in stop_words]


def fuzzy_match_stage(milestone_stage: str, stage_titles: Set[str], stages: List[DetectedStage]) -> str:
    """
    Public function for fuzzy matching a milestone's stage reference to actual stage titles.

    This can be called from external code (like test files) to perform fuzzy matching.

    Args:
        milestone_stage: The stage name referenced by a milestone
        stage_titles: Set of valid stage titles
        stages: List of DetectedStage objects

    Returns:
        The best matching stage title, or the original if exact match found
    """
    if milestone_stage in stage_titles:
        return milestone_stage
    return _find_closest_stage(milestone_stage, stages)


def _validate_durations(
    durations: List[DurationEstimate],
    stages: List[DetectedStage],
    milestones: List[ExtractedMilestone],
    stage_titles: Set[str],
    milestone_names: Set[str]
) -> List[DurationEstimate]:
    """
    Validate and fix durations.

    - Ensures every stage has a duration estimate
    - Fixes duration_months_min > 0
    - Ensures duration_months_max >= duration_months_min
    """
    validated = []
    covered_items: Set[str] = set()

    for duration in durations:
        needs_fix = False
        new_weeks_min = duration.duration_weeks_min
        new_weeks_max = duration.duration_weeks_max
        new_months_min = duration.duration_months_min
        new_months_max = duration.duration_months_max

        # Track covered items
        covered_items.add(duration.item_description)

        # Fix duration_months_min > 0
        if duration.duration_months_min <= 0:
            new_months_min = 1
            new_weeks_min = max(1, duration.duration_weeks_min) if duration.duration_weeks_min > 0 else 4
            logger.warning(
                f"Duration for '{duration.item_description}' has months_min <= 0, fixing to 1"
            )
            needs_fix = True

        # Fix duration_weeks_min > 0
        if new_weeks_min <= 0:
            new_weeks_min = max(1, new_months_min * 4)
            needs_fix = True

        # Fix duration_months_max >= duration_months_min
        if duration.duration_months_max < new_months_min:
            new_months_max = new_months_min
            logger.warning(
                f"Duration for '{duration.item_description}' has months_max < months_min, fixing"
            )
            needs_fix = True

        # Fix duration_weeks_max >= duration_weeks_min
        if new_weeks_max < new_weeks_min:
            new_weeks_max = new_weeks_min
            needs_fix = True

        if needs_fix:
            duration = DurationEstimate(
                item_description=duration.item_description,
                item_type=duration.item_type,
                duration_weeks_min=new_weeks_min,
                duration_weeks_max=new_weeks_max,
                duration_months_min=new_months_min,
                duration_months_max=new_months_max,
                confidence=duration.confidence,
                basis=duration.basis,
                source_text=duration.source_text
            )

        validated.append(duration)

    # Add missing duration estimates for stages
    for stage in stages:
        if stage.title not in covered_items:
            logger.warning(f"Adding missing duration estimate for stage '{stage.title}'")
            default_duration = _get_default_stage_duration(stage.stage_type)
            validated.append(default_duration._replace_item(stage.title))
            covered_items.add(stage.title)

    # Add missing duration estimates for milestones
    for milestone in milestones:
        if milestone.name not in covered_items:
            logger.warning(f"Adding missing duration estimate for milestone '{milestone.name}'")
            default_duration = _get_default_milestone_duration(milestone.milestone_type, milestone.is_critical)
            validated.append(DurationEstimate(
                item_description=milestone.name,
                item_type="milestone",
                duration_weeks_min=default_duration[0],
                duration_weeks_max=default_duration[1],
                duration_months_min=max(1, default_duration[0] // 4),
                duration_months_max=max(1, default_duration[1] // 4),
                confidence="low",
                basis="llm_estimate",
                source_text=None
            ))
            covered_items.add(milestone.name)

    return validated


def _get_default_stage_duration(stage_type: StageType) -> DurationEstimate:
    """Get default duration estimate for a stage type."""
    # Default durations in months (min, max)
    defaults = {
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

    months_min, months_max = defaults.get(stage_type, (3, 6))

    return DurationEstimate(
        item_description="",  # Will be replaced
        item_type="stage",
        duration_weeks_min=months_min * 4,
        duration_weeks_max=months_max * 4,
        duration_months_min=months_min,
        duration_months_max=months_max,
        confidence="low",
        basis="llm_estimate",
        source_text=None
    )


def _get_default_milestone_duration(milestone_type: str, is_critical: bool) -> Tuple[int, int]:
    """Get default duration in weeks (min, max) for a milestone type."""
    defaults = {
        "exam": (2, 4),
        "proposal": (4, 8),
        "review": (1, 2),
        "publication": (12, 24),
        "presentation": (1, 2),
        "submission": (1, 2),
        "defense": (4, 8),
        "approval": (2, 4),
        "deliverable": (2, 6),
    }

    weeks_min, weeks_max = defaults.get(milestone_type, (2, 4))

    # Critical milestones may take longer
    if is_critical:
        weeks_max = int(weeks_max * 1.5)

    return weeks_min, weeks_max


def _validate_dependencies(
    dependencies: List[Dependency],
    all_item_names: Set[str]
) -> List[Dependency]:
    """
    Validate and fix dependencies.

    - Removes dependencies with invalid item names
    - Removes self-dependencies
    - Removes cycles to ensure valid DAG
    """
    # First pass: filter invalid dependencies
    valid_deps = []

    for dep in dependencies:
        # Check both items exist
        if dep.dependent_item not in all_item_names:
            logger.warning(f"Removing dependency: unknown dependent_item '{dep.dependent_item}'")
            continue

        if dep.depends_on_item not in all_item_names:
            logger.warning(f"Removing dependency: unknown depends_on_item '{dep.depends_on_item}'")
            continue

        # Skip self-dependencies
        if dep.dependent_item == dep.depends_on_item:
            logger.warning(f"Removing self-dependency: '{dep.dependent_item}'")
            continue

        valid_deps.append(dep)

    # Second pass: remove cycles to ensure DAG
    dag_deps = _ensure_dag(valid_deps)

    return dag_deps


def _ensure_dag(dependencies: List[Dependency]) -> List[Dependency]:
    """
    Ensure dependencies form a valid DAG by removing edges that create cycles.

    Uses Kahn's algorithm for topological sort to detect cycles.
    Edges are removed in reverse order of confidence (lowest confidence first).
    """
    if not dependencies:
        return []

    # Sort by confidence (descending) - we'll add high confidence edges first
    sorted_deps = sorted(dependencies, key=lambda d: -d.confidence)

    # Build graph incrementally, checking for cycles
    graph: Dict[str, Set[str]] = {}
    result_deps: List[Dependency] = []

    for dep in sorted_deps:
        # Initialize nodes if needed
        if dep.dependent_item not in graph:
            graph[dep.dependent_item] = set()
        if dep.depends_on_item not in graph:
            graph[dep.depends_on_item] = set()

        # Temporarily add edge
        graph[dep.dependent_item].add(dep.depends_on_item)

        # Check if this creates a cycle
        if _has_cycle(graph):
            # Remove the edge - it creates a cycle
            graph[dep.dependent_item].remove(dep.depends_on_item)
            logger.warning(
                f"Removing dependency that creates cycle: "
                f"'{dep.dependent_item}' -> '{dep.depends_on_item}'"
            )
        else:
            # Edge is valid
            result_deps.append(dep)

    return result_deps


def _has_cycle(graph: Dict[str, Set[str]]) -> bool:
    """
    Detect if graph has a cycle using DFS.

    Args:
        graph: Adjacency set representation {node: {neighbors}}

    Returns:
        True if cycle exists, False otherwise
    """
    # States: 0 = unvisited, 1 = visiting (in current path), 2 = visited
    state: Dict[str, int] = {node: 0 for node in graph}

    def dfs(node: str) -> bool:
        if state[node] == 1:
            # Back edge - cycle detected
            return True
        if state[node] == 2:
            # Already fully processed
            return False

        state[node] = 1  # Mark as visiting

        for neighbor in graph.get(node, set()):
            if neighbor in state and dfs(neighbor):
                return True

        state[node] = 2  # Mark as visited
        return False

    # Check all nodes (graph may be disconnected)
    for node in graph:
        if state[node] == 0:
            if dfs(node):
                return True

    return False


def validate_stage_milestone_consistency(
    stages: List[DetectedStage],
    milestones: List[ExtractedMilestone]
) -> Tuple[List[DetectedStage], List[ExtractedMilestone]]:
    """
    Ensure every stage has at least 2 milestones.

    Adds generic milestones if needed.

    Args:
        stages: List of stages
        milestones: List of milestones

    Returns:
        Tuple of (stages, milestones) with milestones added if needed
    """
    # Count milestones per stage
    milestones_by_stage: Dict[str, List[ExtractedMilestone]] = {}
    for m in milestones:
        if m.stage not in milestones_by_stage:
            milestones_by_stage[m.stage] = []
        milestones_by_stage[m.stage].append(m)

    new_milestones = list(milestones)

    for stage in stages:
        stage_milestones = milestones_by_stage.get(stage.title, [])
        count = len(stage_milestones)

        if count < 2:
            needed = 2 - count
            logger.warning(f"Stage '{stage.title}' has only {count} milestones, adding {needed}")

            for i in range(needed):
                if i == 0 and count == 0:
                    # Add "Begin" milestone
                    new_milestones.append(ExtractedMilestone(
                        name=f"Begin {stage.title}",
                        description=f"Initiate work on {stage.title.lower()} phase",
                        stage=stage.title,
                        milestone_type="deliverable",
                        evidence_snippet=stage.description[:150] if stage.description else f"Start of {stage.title}",
                        keywords=[],
                        source_segment=None,
                        is_critical=False,
                        confidence=0.4
                    ))
                else:
                    # Add "Complete" milestone
                    new_milestones.append(ExtractedMilestone(
                        name=f"Complete {stage.title}",
                        description=f"Finish all activities in {stage.title.lower()} phase",
                        stage=stage.title,
                        milestone_type="deliverable",
                        evidence_snippet=stage.description[:150] if stage.description else f"Completion of {stage.title}",
                        keywords=[],
                        source_segment=None,
                        is_critical=True,
                        confidence=0.4
                    ))

    return stages, new_milestones

"""Parsers to convert LLM JSON output into timeline dataclasses."""
import logging
from typing import Any, Dict, List

from app.services.timeline_intelligence_engine import (
    DetectedStage,
    ExtractedMilestone,
    DurationEstimate,
    Dependency,
    EvidenceSnippet,
    StageType,
)

logger = logging.getLogger(__name__)


def parse_stages(data: Dict[str, Any]) -> List[DetectedStage]:
    """
    Parse LLM output into DetectedStage dataclasses.

    Args:
        data: Dictionary containing 'stages' key with list of stage dicts

    Returns:
        List of DetectedStage objects, sorted by order_hint
    """
    stages_data = data.get("stages", [])
    if not isinstance(stages_data, list):
        logger.warning(f"Expected 'stages' to be a list, got {type(stages_data)}")
        return []

    stages: List[DetectedStage] = []

    for i, stage_dict in enumerate(stages_data):
        if not isinstance(stage_dict, dict):
            logger.warning(f"Skipping stage {i}: expected dict, got {type(stage_dict)}")
            continue

        try:
            stage = _parse_single_stage(stage_dict, i)
            stages.append(stage)
        except Exception as e:
            logger.error(f"Failed to parse stage {i}: {e}")
            continue

    # Sort by order_hint (ascending)
    stages.sort(key=lambda s: s.order_hint)

    return stages


def _parse_single_stage(stage_dict: Dict[str, Any], index: int) -> DetectedStage:
    """Parse a single stage dictionary into DetectedStage."""
    # Parse stage_type with fallback to OTHER
    stage_type_str = stage_dict.get("stage_type", "other")
    try:
        stage_type = StageType(stage_type_str.lower())
    except (ValueError, AttributeError):
        logger.warning(f"Unknown stage_type '{stage_type_str}', using OTHER")
        stage_type = StageType.OTHER

    # Parse evidence quotes into EvidenceSnippet objects
    evidence_quotes = stage_dict.get("evidence_quotes", [])
    if not isinstance(evidence_quotes, list):
        evidence_quotes = []

    evidence_snippets: List[EvidenceSnippet] = []
    for quote in evidence_quotes:
        if isinstance(quote, str) and quote.strip():
            evidence_snippets.append(EvidenceSnippet(
                text=quote[:200],  # Limit length
                source="llm_extraction",
                location="document"
            ))
        elif isinstance(quote, dict):
            evidence_snippets.append(EvidenceSnippet(
                text=str(quote.get("text", ""))[:200],
                source=quote.get("source", "llm_extraction"),
                location=quote.get("location", "document")
            ))

    # Parse keywords
    keywords = stage_dict.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []
    keywords = [str(k) for k in keywords if k][:10]  # Limit to 10

    # Build DetectedStage
    return DetectedStage(
        stage_type=stage_type,
        title=str(stage_dict.get("title", f"Stage {index + 1}")),
        description=str(stage_dict.get("description", ""))[:500],
        confidence=_parse_float(stage_dict.get("confidence"), default=0.5, min_val=0.0, max_val=1.0),
        keywords_matched=keywords,
        source_segments=[],  # Not provided by LLM
        evidence=evidence_snippets,
        order_hint=_parse_int(stage_dict.get("order_hint"), default=index + 1)
    )


def parse_milestones(data: Dict[str, Any]) -> List[ExtractedMilestone]:
    """
    Parse LLM output into ExtractedMilestone dataclasses.

    Args:
        data: Dictionary containing 'milestones' key with list of milestone dicts

    Returns:
        List of ExtractedMilestone objects
    """
    milestones_data = data.get("milestones", [])
    if not isinstance(milestones_data, list):
        logger.warning(f"Expected 'milestones' to be a list, got {type(milestones_data)}")
        return []

    milestones: List[ExtractedMilestone] = []

    for i, milestone_dict in enumerate(milestones_data):
        if not isinstance(milestone_dict, dict):
            logger.warning(f"Skipping milestone {i}: expected dict, got {type(milestone_dict)}")
            continue

        try:
            milestone = _parse_single_milestone(milestone_dict, i)
            milestones.append(milestone)
        except Exception as e:
            logger.error(f"Failed to parse milestone {i}: {e}")
            continue

    return milestones


def _parse_single_milestone(milestone_dict: Dict[str, Any], index: int) -> ExtractedMilestone:
    """Parse a single milestone dictionary into ExtractedMilestone."""
    # Parse keywords
    keywords = milestone_dict.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []
    keywords = [str(k) for k in keywords if k][:5]  # Limit to 5

    # Ensure evidence_snippet is not empty
    evidence_snippet = str(milestone_dict.get("evidence_snippet", "")).strip()
    if not evidence_snippet:
        evidence_snippet = f"Milestone: {milestone_dict.get('name', 'Unknown')}"

    # Parse milestone_type with validation
    milestone_type = str(milestone_dict.get("milestone_type", "deliverable")).lower()
    valid_types = {"deliverable", "exam", "review", "publication", "presentation", "submission", "defense", "approval"}
    if milestone_type not in valid_types:
        logger.warning(f"Unknown milestone_type '{milestone_type}', using 'deliverable'")
        milestone_type = "deliverable"

    return ExtractedMilestone(
        name=str(milestone_dict.get("name", f"Milestone {index + 1}"))[:100],
        description=str(milestone_dict.get("description", ""))[:300],
        stage=str(milestone_dict.get("stage", "Unknown")),
        milestone_type=milestone_type,
        evidence_snippet=evidence_snippet[:200],
        keywords=keywords,
        source_segment=None,  # Not provided by LLM
        is_critical=bool(milestone_dict.get("is_critical", False)),
        confidence=_parse_float(milestone_dict.get("confidence"), default=0.5, min_val=0.0, max_val=1.0)
    )


def parse_durations(data: Dict[str, Any]) -> List[DurationEstimate]:
    """
    Parse LLM output into DurationEstimate dataclasses.

    Args:
        data: Dictionary containing 'durations' key with list of duration dicts

    Returns:
        List of DurationEstimate objects
    """
    durations_data = data.get("durations", [])
    if not isinstance(durations_data, list):
        logger.warning(f"Expected 'durations' to be a list, got {type(durations_data)}")
        return []

    durations: List[DurationEstimate] = []

    for i, duration_dict in enumerate(durations_data):
        if not isinstance(duration_dict, dict):
            logger.warning(f"Skipping duration {i}: expected dict, got {type(duration_dict)}")
            continue

        try:
            duration = _parse_single_duration(duration_dict, i)
            durations.append(duration)
        except Exception as e:
            logger.error(f"Failed to parse duration {i}: {e}")
            continue

    return durations


def _parse_single_duration(duration_dict: Dict[str, Any], index: int) -> DurationEstimate:
    """Parse a single duration dictionary into DurationEstimate."""
    # Parse item_type with validation
    item_type = str(duration_dict.get("item_type", "stage")).lower()
    if item_type not in {"stage", "milestone"}:
        logger.warning(f"Unknown item_type '{item_type}', using 'stage'")
        item_type = "stage"

    # Parse duration values, ensuring min > 0 and max >= min
    weeks_min = max(1, _parse_int(duration_dict.get("duration_weeks_min"), default=4))
    weeks_max = max(weeks_min, _parse_int(duration_dict.get("duration_weeks_max"), default=weeks_min))

    months_min = max(1, _parse_int(duration_dict.get("duration_months_min"), default=max(1, weeks_min // 4)))
    months_max = max(months_min, _parse_int(duration_dict.get("duration_months_max"), default=max(1, weeks_max // 4)))

    # Parse confidence with validation
    confidence = str(duration_dict.get("confidence", "medium")).lower()
    if confidence not in {"low", "medium", "high"}:
        confidence = "medium"

    # Parse basis with validation
    basis = str(duration_dict.get("basis", "llm_estimate")).lower()
    if basis not in {"explicit", "llm_estimate"}:
        basis = "llm_estimate"

    # Parse source_text
    source_text = duration_dict.get("source_text")
    if source_text is not None:
        source_text = str(source_text)[:150]

    return DurationEstimate(
        item_description=str(duration_dict.get("item_description", f"Item {index + 1}")),
        item_type=item_type,
        duration_weeks_min=weeks_min,
        duration_weeks_max=weeks_max,
        duration_months_min=months_min,
        duration_months_max=months_max,
        confidence=confidence,
        basis=basis,
        source_text=source_text
    )


def parse_dependencies(data: Dict[str, Any]) -> List[Dependency]:
    """
    Parse LLM output into Dependency dataclasses.

    Args:
        data: Dictionary containing 'dependencies' key with list of dependency dicts

    Returns:
        List of Dependency objects
    """
    dependencies_data = data.get("dependencies", [])
    if not isinstance(dependencies_data, list):
        logger.warning(f"Expected 'dependencies' to be a list, got {type(dependencies_data)}")
        return []

    dependencies: List[Dependency] = []

    for i, dep_dict in enumerate(dependencies_data):
        if not isinstance(dep_dict, dict):
            logger.warning(f"Skipping dependency {i}: expected dict, got {type(dep_dict)}")
            continue

        try:
            dependency = _parse_single_dependency(dep_dict, i)
            if dependency is not None:
                dependencies.append(dependency)
        except Exception as e:
            logger.error(f"Failed to parse dependency {i}: {e}")
            continue

    return dependencies


def _parse_single_dependency(dep_dict: Dict[str, Any], index: int) -> Dependency | None:
    """Parse a single dependency dictionary into Dependency."""
    dependent_item = str(dep_dict.get("dependent_item", "")).strip()
    depends_on_item = str(dep_dict.get("depends_on_item", "")).strip()

    # Skip if either item is missing or if it's a self-dependency
    if not dependent_item or not depends_on_item:
        logger.warning(f"Skipping dependency {index}: missing item names")
        return None

    if dependent_item == depends_on_item:
        logger.warning(f"Skipping self-dependency: {dependent_item}")
        return None

    # Parse dependency_type with validation
    dep_type = str(dep_dict.get("dependency_type", "sequential")).lower()
    valid_types = {"sequential", "prerequisite", "parallel", "blocks"}
    if dep_type not in valid_types:
        logger.warning(f"Unknown dependency_type '{dep_type}', using 'sequential'")
        dep_type = "sequential"

    return Dependency(
        dependent_item=dependent_item,
        depends_on_item=depends_on_item,
        dependency_type=dep_type,
        confidence=_parse_float(dep_dict.get("confidence"), default=0.7, min_val=0.0, max_val=1.0),
        reason=str(dep_dict.get("reason", ""))[:150]
    )


def _parse_float(value: Any, default: float, min_val: float = None, max_val: float = None) -> float:
    """
    Parse a value as float with bounds checking.

    Args:
        value: Value to parse
        default: Default if parsing fails
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)

    Returns:
        Parsed float within bounds
    """
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default

    if min_val is not None:
        result = max(min_val, result)
    if max_val is not None:
        result = min(max_val, result)

    return result


def _parse_int(value: Any, default: int) -> int:
    """
    Parse a value as integer.

    Args:
        value: Value to parse
        default: Default if parsing fails

    Returns:
        Parsed integer
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

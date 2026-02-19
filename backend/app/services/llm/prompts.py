"""Prompt builders for LLM-based timeline extraction."""
import json
from typing import Any, Dict, List, Optional


# Valid values for enums (must match timeline_intelligence_engine.py)
VALID_STAGE_TYPES = [
    "coursework",
    "literature_review",
    "methodology",
    "data_collection",
    "analysis",
    "writing",
    "submission",
    "defense",
    "publication",
    "other",
]

VALID_MILESTONE_TYPES = [
    "deliverable",
    "exam",
    "review",
    "publication",
    "presentation",
    "submission",
    "defense",
    "approval",
]

VALID_DEPENDENCY_TYPES = [
    "sequential",
    "prerequisite",
    "parallel",
    "blocks",
]

VALID_CONFIDENCE_LEVELS = ["low", "medium", "high"]

VALID_BASIS_VALUES = ["explicit", "llm_estimate"]


def build_stages_and_milestones_prompt(
    text: str,
    section_map: Optional[Dict[str, Any]] = None
) -> tuple[str, str]:
    """
    Build prompts for extracting stages and milestones from document text.

    Combines the functionality of detect_stages and extract_milestones into
    a single LLM call for efficiency.

    Args:
        text: Plain text content from the document
        section_map: Optional section structure from document processing

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """You are an expert PhD timeline analyst. Your task is to analyze academic documents (research proposals, thesis plans, dissertation outlines) and extract structured timeline information.

You MUST return valid JSON only. No markdown, no explanations, no extra text.

## Output Format

Return a JSON object with exactly two top-level keys:

```json
{
  "stages": [...],
  "milestones": [...]
}
```

## Stage Requirements

Extract 4-8 stages that represent major phases of the PhD journey. Each stage must have:

- **stage_type**: MUST be exactly one of: "coursework", "literature_review", "methodology", "data_collection", "analysis", "writing", "submission", "defense", "publication", "other"
- **title**: Human-readable title (e.g., "Literature Review", "Data Collection Phase")
- **description**: 1-2 sentence description of what this stage involves
- **confidence**: Float 0.0-1.0 indicating how confident you are this stage exists in the document
- **order_hint**: Integer 1-10 indicating chronological order (1=earliest, 10=latest)
- **keywords**: Array of 3-5 keywords found in the document that indicate this stage
- **evidence_quotes**: Array of 1-3 actual quotes from the document that support this stage (max 100 chars each)

Stage ordering guide:
1. coursework
2. literature_review
3. methodology
4. data_collection
5. analysis
6. writing
7. submission
8. defense
9. publication
10. other

## Milestone Requirements

Extract 2-5 milestones PER stage. Each milestone must have:

- **name**: Concise milestone name (e.g., "Complete Literature Survey", "Pass Qualifying Exam")
- **description**: 1-2 sentence description
- **stage**: MUST exactly match one of the stage titles you defined above
- **milestone_type**: MUST be exactly one of: "deliverable", "exam", "review", "publication", "presentation", "submission", "defense", "approval"
- **evidence_snippet**: Quote from the document supporting this milestone (MUST NOT be empty, max 150 chars)
- **keywords**: Array of 1-3 relevant keywords
- **is_critical**: Boolean. Set to true ONLY for: qualifying exams, comprehensive exams, proposal defense, dissertation defense, IRB/ethics approval, final submission
- **confidence**: Float 0.0-1.0

## Critical Rules

1. Every stage must have at least 2 milestones
2. Every milestone's "stage" field must exactly match a stage "title"
3. evidence_snippet must never be empty - use actual text from the document
4. Only use the exact stage_type and milestone_type values listed above
5. If the document doesn't clearly indicate a stage, don't invent it - use lower confidence
6. Quotes must be actual text from the document, not paraphrased

Respond with ONLY valid JSON, no markdown fences, no preamble."""

    # Build user prompt with document content
    user_prompt_parts = [
        "Analyze the following PhD-related document and extract stages and milestones.\n",
    ]

    # Include section map if available
    if section_map and section_map.get("sections"):
        user_prompt_parts.append("## Document Structure\n")
        user_prompt_parts.append("The document has the following sections:\n")
        for section in section_map["sections"]:
            title = section.get("title", "Untitled")
            level = section.get("level", 1)
            indent = "  " * (level - 1)
            user_prompt_parts.append(f"{indent}- {title}\n")
        user_prompt_parts.append("\n")

    user_prompt_parts.append("## Document Content\n\n")
    user_prompt_parts.append(text)
    user_prompt_parts.append("\n\n---\n")
    user_prompt_parts.append("Return the JSON object with 'stages' and 'milestones' arrays.")

    user_prompt = "".join(user_prompt_parts)

    return system_prompt, user_prompt


def build_durations_and_dependencies_prompt(
    text: str,
    stages_json: List[Dict[str, Any]],
    milestones_json: List[Dict[str, Any]],
    section_map: Optional[Dict[str, Any]] = None,
    discipline: Optional[str] = None
) -> tuple[str, str]:
    """
    Build prompts for estimating durations and mapping dependencies.

    Takes already-detected stages and milestones as context to ensure
    consistency in naming.

    Args:
        text: Plain text content from the document
        stages_json: List of stage dictionaries from first LLM call
        milestones_json: List of milestone dictionaries from first LLM call
        section_map: Optional section structure from document processing
        discipline: Optional field of study for calibrated estimates

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Extract stage titles and milestone names for reference
    stage_titles = [s.get("title", "") for s in stages_json]
    milestone_names = [m.get("name", "") for m in milestones_json]
    all_items = stage_titles + milestone_names

    system_prompt = """You are an expert PhD timeline analyst specializing in duration estimation and dependency mapping.

You MUST return valid JSON only. No markdown, no explanations, no extra text.

## Output Format

Return a JSON object with exactly two top-level keys:

```json
{
  "durations": [...],
  "dependencies": [...]
}
```

## Duration Requirements

Provide ONE duration estimate for EACH stage AND EACH milestone. Each duration must have:

- **item_description**: MUST exactly match a stage title or milestone name from the provided list
- **item_type**: Either "stage" or "milestone"
- **duration_weeks_min**: Minimum duration in weeks (must be > 0)
- **duration_weeks_max**: Maximum duration in weeks (must be >= duration_weeks_min)
- **duration_months_min**: Minimum duration in months (approximately weeks/4, must be > 0)
- **duration_months_max**: Maximum duration in months (must be >= duration_months_min)
- **confidence**: One of: "low", "medium", "high"
- **basis**: "explicit" if the document mentions specific timing, otherwise "llm_estimate"
- **source_text**: If basis is "explicit", include the quote mentioning timing (max 100 chars). Otherwise null.

## Duration Guidelines by Stage Type

Typical PhD stage durations (adjust based on discipline and document context):
- coursework: 12-24 months
- literature_review: 3-9 months
- methodology: 2-6 months
- data_collection: 6-18 months (longer for experimental sciences)
- analysis: 3-9 months
- writing: 6-15 months
- submission: 1-2 months
- defense: 1-3 months
- publication: 3-12 months

Typical milestone durations:
- exam: 2-4 weeks
- proposal/defense preparation: 4-8 weeks
- review: 1-2 weeks
- publication process: 12-24 weeks
- deliverable: 2-6 weeks

## Dependency Requirements

Map dependencies between stages and milestones. Each dependency must have:

- **dependent_item**: The item that depends on another (MUST exactly match a stage title or milestone name)
- **depends_on_item**: The item that must complete first (MUST exactly match a stage title or milestone name)
- **dependency_type**: One of: "sequential", "prerequisite", "parallel", "blocks"
- **confidence**: Float 0.0-1.0
- **reason**: Brief explanation of why this dependency exists (max 100 chars)

## Dependency Type Definitions

- **sequential**: B naturally follows A in the timeline (most common)
- **prerequisite**: B requires specific output/approval from A
- **parallel**: A and B can occur simultaneously
- **blocks**: A must complete before B can even begin (strong dependency)

## Critical Rules

1. **DAG Required**: Dependencies must form a Directed Acyclic Graph - NO CYCLES allowed
   - If A depends on B, B cannot depend on A (directly or indirectly)
   - Validate: follow dependency chains, they must not loop back

2. **Exact Name Matching**: dependent_item and depends_on_item must EXACTLY match the provided stage titles or milestone names

3. **Complete Coverage**: Every stage and milestone must have a duration estimate

4. **Logical Flow**: Dependencies should reflect realistic PhD workflow:
   - Stages follow logical order (coursework → literature_review → methodology → ...)
   - Milestones within a stage have sequential dependencies
   - Cross-stage milestones may have prerequisites

5. **No Self-Dependencies**: An item cannot depend on itself

Respond with ONLY valid JSON, no markdown fences, no preamble."""

    # Build user prompt with context
    user_prompt_parts = []

    # Add discipline context if available
    if discipline:
        user_prompt_parts.append(f"## Discipline Context\n")
        user_prompt_parts.append(f"This is a {discipline} PhD program. Adjust duration estimates accordingly.\n\n")

        # Add discipline-specific guidance
        discipline_lower = discipline.lower()
        if any(d in discipline_lower for d in ["biology", "chemistry", "physics", "engineering"]):
            user_prompt_parts.append("Note: Experimental sciences typically have longer data collection phases.\n\n")
        elif any(d in discipline_lower for d in ["computer science", "mathematics", "statistics"]):
            user_prompt_parts.append("Note: Theoretical/computational fields may have shorter data collection but longer analysis/writing.\n\n")
        elif any(d in discipline_lower for d in ["psychology", "sociology", "anthropology"]):
            user_prompt_parts.append("Note: Social sciences often require extensive data collection and IRB approval.\n\n")
        elif any(d in discipline_lower for d in ["history", "literature", "philosophy"]):
            user_prompt_parts.append("Note: Humanities typically have longer literature review and writing phases.\n\n")

    # Add the stages and milestones for reference
    user_prompt_parts.append("## Detected Stages (from previous analysis)\n\n")
    user_prompt_parts.append("You must use these EXACT titles for item_description and dependency items:\n\n")
    for i, stage in enumerate(stages_json, 1):
        title = stage.get("title", f"Stage {i}")
        stage_type = stage.get("stage_type", "other")
        user_prompt_parts.append(f"{i}. **{title}** (type: {stage_type})\n")
    user_prompt_parts.append("\n")

    user_prompt_parts.append("## Detected Milestones (from previous analysis)\n\n")
    user_prompt_parts.append("You must use these EXACT names for item_description and dependency items:\n\n")

    # Group milestones by stage for clarity
    milestones_by_stage: Dict[str, List[Dict]] = {}
    for milestone in milestones_json:
        stage = milestone.get("stage", "Unknown")
        if stage not in milestones_by_stage:
            milestones_by_stage[stage] = []
        milestones_by_stage[stage].append(milestone)

    for stage_title in stage_titles:
        stage_milestones = milestones_by_stage.get(stage_title, [])
        if stage_milestones:
            user_prompt_parts.append(f"### {stage_title}\n")
            for m in stage_milestones:
                name = m.get("name", "Unknown")
                mtype = m.get("milestone_type", "deliverable")
                critical = " [CRITICAL]" if m.get("is_critical") else ""
                user_prompt_parts.append(f"- {name} (type: {mtype}){critical}\n")
            user_prompt_parts.append("\n")

    # Add document content for context
    user_prompt_parts.append("## Original Document Content\n\n")
    user_prompt_parts.append("Use this to find explicit timing mentions:\n\n")
    # Truncate if too long to save tokens
    max_doc_length = 8000
    if len(text) > max_doc_length:
        user_prompt_parts.append(text[:max_doc_length])
        user_prompt_parts.append("\n\n[Document truncated...]\n")
    else:
        user_prompt_parts.append(text)

    user_prompt_parts.append("\n\n---\n")
    user_prompt_parts.append("## Summary of Items to Process\n\n")
    user_prompt_parts.append(f"**Stages ({len(stage_titles)}):** {', '.join(stage_titles)}\n\n")
    user_prompt_parts.append(f"**Milestones ({len(milestone_names)}):** {', '.join(milestone_names)}\n\n")
    user_prompt_parts.append("Return the JSON object with 'durations' and 'dependencies' arrays.\n")
    user_prompt_parts.append(f"Ensure you have {len(stage_titles) + len(milestone_names)} duration entries (one per item).")

    user_prompt = "".join(user_prompt_parts)

    return system_prompt, user_prompt


def get_stage_types() -> List[str]:
    """Return list of valid stage types."""
    return VALID_STAGE_TYPES.copy()


def get_milestone_types() -> List[str]:
    """Return list of valid milestone types."""
    return VALID_MILESTONE_TYPES.copy()


def get_dependency_types() -> List[str]:
    """Return list of valid dependency types."""
    return VALID_DEPENDENCY_TYPES.copy()

#!/usr/bin/env python3
"""Test script for the LLM-powered TimelineIntelligenceEngine with direct Groq client."""

import sys
import os
import json
import re
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load API key directly from .env file
def load_env_file(filepath: str) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

# Load .env from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
env_vars = load_env_file(os.path.join(script_dir, '.env'))

# LLM Configuration - loaded directly from .env
LLM_API_KEY = env_vars.get('LLM_API_KEY', '')
LLM_MODEL = env_vars.get('LLM_MODEL', 'llama-3.3-70b-versatile')
LLM_TEMPERATURE = float(env_vars.get('LLM_TEMPERATURE', '0.15'))
LLM_MAX_TOKENS = int(env_vars.get('LLM_MAX_TOKENS', '4096'))
LLM_TIMEOUT = int(env_vars.get('LLM_TIMEOUT_SECONDS', '60'))

print(f"Loaded config: model={LLM_MODEL}, temperature={LLM_TEMPERATURE}, max_tokens={LLM_MAX_TOKENS}")
print(f"API Key: {LLM_API_KEY[:20]}..." if LLM_API_KEY else "API Key: NOT SET")

# ============================================================================
# Inline dataclasses (copied from timeline_intelligence_engine.py)
# ============================================================================

class StageType(str, Enum):
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
class EvidenceSnippet:
    text: str
    source: str
    location: str

@dataclass
class DetectedStage:
    stage_type: StageType
    title: str
    description: str
    confidence: float
    keywords_matched: List[str] = field(default_factory=list)
    source_segments: List[int] = field(default_factory=list)
    evidence: List[EvidenceSnippet] = field(default_factory=list)
    order_hint: int = 0

@dataclass
class ExtractedMilestone:
    name: str
    description: str
    stage: str
    milestone_type: str
    evidence_snippet: str
    keywords: List[str] = field(default_factory=list)
    source_segment: Optional[int] = None
    is_critical: bool = False
    confidence: float = 0.5

@dataclass
class DurationEstimate:
    item_description: str
    item_type: str
    duration_weeks_min: int
    duration_weeks_max: int
    duration_months_min: int
    duration_months_max: int
    confidence: str
    basis: str
    source_text: Optional[str] = None

@dataclass
class Dependency:
    dependent_item: str
    depends_on_item: str
    dependency_type: str
    confidence: float
    reason: str = ""

# ============================================================================
# Direct Groq Client (standalone, no app.config dependency)
# ============================================================================

class DirectGroqClient:
    """Direct Groq client for testing without app dependencies."""

    def __init__(self):
        if not LLM_API_KEY:
            raise ValueError("LLM_API_KEY not set in .env file")

        from groq import Groq
        self.client = Groq(api_key=LLM_API_KEY, timeout=float(LLM_TIMEOUT))
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS
        print(f"Groq client initialized: model={self.model}")

    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = None) -> Dict[str, Any]:
        """Call Groq API and return parsed JSON."""
        max_tokens = max_tokens or self.max_tokens

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        text = response.choices[0].message.content

        # Strip markdown fences if present
        text = text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)

        return json.loads(text)

# ============================================================================
# Prompts (inline versions)
# ============================================================================

def build_stages_and_milestones_prompt(text: str, section_map: Optional[Dict] = None) -> Tuple[str, str]:
    """Build prompts for extracting stages and milestones."""
    system_prompt = """You are an expert PhD timeline analyst. Your task is to analyze academic documents and extract structured timeline information.

Return a JSON object with exactly two top-level keys: "stages" and "milestones".

## Stage Requirements
Extract 4-8 stages. Each stage must have:
- stage_type: One of: coursework, literature_review, methodology, data_collection, analysis, writing, submission, defense, publication, other
- title: Human-readable title
- description: 1-2 sentence description
- confidence: Float 0.0-1.0
- order_hint: Integer 1-10 (1=earliest)
- keywords: Array of 3-5 keywords
- evidence_quotes: Array of 1-3 quotes from the document (max 100 chars each)

## Milestone Requirements
Extract 2-5 milestones PER stage. Each milestone must have:
- name: Concise name
- description: 1-2 sentence description
- stage: MUST exactly match one of the stage titles
- milestone_type: One of: deliverable, exam, review, publication, presentation, submission, defense, approval
- evidence_snippet: Quote from document (max 150 chars, MUST NOT be empty)
- keywords: Array of 1-3 keywords
- is_critical: Boolean (true for qualifying exams, proposal defense, dissertation defense, IRB approval, final submission)
- confidence: Float 0.0-1.0

Respond with ONLY valid JSON, no markdown fences, no preamble."""

    user_prompt = f"""Analyze the following PhD-related document and extract stages and milestones.

## Document Content

{text}

---
Return the JSON object with 'stages' and 'milestones' arrays."""

    return system_prompt, user_prompt


def build_durations_and_dependencies_prompt(
    text: str,
    stages_json: List[Dict],
    milestones_json: List[Dict],
    discipline: Optional[str] = None
) -> Tuple[str, str]:
    """Build prompts for durations and dependencies."""

    stage_titles = [s.get("title", "") for s in stages_json]
    milestone_names = [m.get("name", "") for m in milestones_json]

    system_prompt = """You are an expert PhD timeline analyst specializing in duration estimation and dependency mapping.

Return a JSON object with exactly two top-level keys: "durations" and "dependencies".

## Duration Requirements
Provide ONE duration estimate for EACH stage AND EACH milestone:
- item_description: MUST exactly match a stage title or milestone name
- item_type: "stage" or "milestone"
- duration_weeks_min: Minimum weeks (must be > 0)
- duration_weeks_max: Maximum weeks (>= min)
- duration_months_min: Minimum months (must be > 0)
- duration_months_max: Maximum months (>= min)
- confidence: "low", "medium", or "high"
- basis: "explicit" if doc mentions timing, else "llm_estimate"
- source_text: Quote if explicit, else null

## Dependency Requirements
- dependent_item: Item that depends on another (exact match required)
- depends_on_item: Item that must complete first (exact match required)
- dependency_type: "sequential", "prerequisite", "parallel", or "blocks"
- confidence: Float 0.0-1.0
- reason: Brief explanation (max 100 chars)

CRITICAL: Dependencies must form a valid DAG (no cycles).

Respond with ONLY valid JSON, no markdown fences, no preamble."""

    user_prompt = f"""## Discipline
{discipline or "General PhD program"}

## Stages to estimate (use EXACT titles):
{json.dumps(stage_titles, indent=2)}

## Milestones to estimate (use EXACT names):
{json.dumps(milestone_names, indent=2)}

## Document Content
{text[:6000]}

---
Return JSON with 'durations' (one per item = {len(stage_titles) + len(milestone_names)} total) and 'dependencies' arrays."""

    return system_prompt, user_prompt

# ============================================================================
# Parsers (inline versions)
# ============================================================================

def parse_stages(data: Dict) -> List[DetectedStage]:
    """Parse LLM output into DetectedStage objects."""
    stages = []
    for i, s in enumerate(data.get("stages", [])):
        try:
            stage_type = StageType(s.get("stage_type", "other").lower())
        except ValueError:
            stage_type = StageType.OTHER

        evidence = []
        for q in s.get("evidence_quotes", []):
            if isinstance(q, str):
                evidence.append(EvidenceSnippet(text=q[:200], source="llm_extraction", location="document"))

        stages.append(DetectedStage(
            stage_type=stage_type,
            title=s.get("title", f"Stage {i+1}"),
            description=s.get("description", "")[:500],
            confidence=min(1.0, max(0.0, float(s.get("confidence", 0.5)))),
            keywords_matched=s.get("keywords", [])[:10],
            source_segments=[],
            evidence=evidence,
            order_hint=int(s.get("order_hint", i+1))
        ))

    stages.sort(key=lambda x: x.order_hint)
    return stages


def parse_milestones(data: Dict) -> List[ExtractedMilestone]:
    """Parse LLM output into ExtractedMilestone objects."""
    milestones = []
    for i, m in enumerate(data.get("milestones", [])):
        evidence = m.get("evidence_snippet", "") or m.get("description", "") or f"Milestone {i+1}"
        milestones.append(ExtractedMilestone(
            name=m.get("name", f"Milestone {i+1}")[:100],
            description=m.get("description", "")[:300],
            stage=m.get("stage", "Unknown"),
            milestone_type=m.get("milestone_type", "deliverable"),
            evidence_snippet=evidence[:200],
            keywords=m.get("keywords", [])[:5],
            source_segment=None,
            is_critical=bool(m.get("is_critical", False)),
            confidence=min(1.0, max(0.0, float(m.get("confidence", 0.5))))
        ))
    return milestones


def parse_durations(data: Dict) -> List[DurationEstimate]:
    """Parse LLM output into DurationEstimate objects."""
    durations = []
    for d in data.get("durations", []):
        weeks_min = max(1, int(d.get("duration_weeks_min", 4)))
        weeks_max = max(weeks_min, int(d.get("duration_weeks_max", weeks_min)))
        months_min = max(1, int(d.get("duration_months_min", 1)))
        months_max = max(months_min, int(d.get("duration_months_max", months_min)))

        durations.append(DurationEstimate(
            item_description=d.get("item_description", "Unknown"),
            item_type=d.get("item_type", "stage"),
            duration_weeks_min=weeks_min,
            duration_weeks_max=weeks_max,
            duration_months_min=months_min,
            duration_months_max=months_max,
            confidence=d.get("confidence", "medium"),
            basis=d.get("basis", "llm_estimate"),
            source_text=d.get("source_text")
        ))
    return durations


def parse_dependencies(data: Dict) -> List[Dependency]:
    """Parse LLM output into Dependency objects."""
    deps = []
    for d in data.get("dependencies", []):
        dep_item = d.get("dependent_item", "").strip()
        on_item = d.get("depends_on_item", "").strip()
        if dep_item and on_item and dep_item != on_item:
            deps.append(Dependency(
                dependent_item=dep_item,
                depends_on_item=on_item,
                dependency_type=d.get("dependency_type", "sequential"),
                confidence=min(1.0, max(0.0, float(d.get("confidence", 0.7)))),
                reason=d.get("reason", "")[:150]
            ))
    return deps

# ============================================================================
# Sample Text
# ============================================================================

SAMPLE_TEXT = """
PhD Research Proposal: Machine Learning for Climate Change Prediction

1. Introduction and Background

This research aims to develop novel machine learning approaches for improving
climate change predictions. The project will span approximately 4 years and
involves multiple phases of work.

2. Literature Review

The first phase involves a comprehensive literature review of existing climate
models and machine learning techniques. This review will cover approximately
200 papers and will take 6 months to complete. Key areas include:
- Deep learning for time series prediction
- Physics-informed neural networks
- Ensemble methods for uncertainty quantification

3. Research Methodology

Following the literature review, we will develop our methodology over 4 months.
The research design includes:
- Development of a hybrid physics-ML model architecture
- Creation of custom loss functions incorporating physical constraints
- Design of validation experiments

Ethics approval will be obtained before any data collection begins.

4. Data Collection Phase

Data collection will span 12 months and include:
- Historical climate data from NOAA and ECMWF
- Satellite imagery from NASA Earth observations
- Ground-based sensor networks

The qualifying exam must be passed before beginning primary data collection.

5. Analysis and Model Development

After data collection, analysis will take approximately 9 months:
- Feature engineering and preprocessing
- Model training and hyperparameter optimization
- Cross-validation and error analysis
- Comparison with baseline models

6. Dissertation Writing

The writing phase will require 8 months:
- Draft individual chapters
- Incorporate advisor feedback
- Final revisions and formatting

7. Defense and Publication

The final phase includes:
- Dissertation defense preparation (2 months)
- Oral defense examination
- Publication of results in peer-reviewed journals

Timeline Summary:
- Year 1: Literature review, methodology, coursework
- Year 2: Data collection, preliminary analysis
- Year 3: Full analysis, initial writing
- Year 4: Complete writing, defense, publication
"""

# ============================================================================
# Test Functions
# ============================================================================

def print_separator(title: str = ""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def test_with_groq():
    """Test the timeline extraction with direct Groq API calls."""
    print_separator("Direct Groq LLM Test")

    # Initialize client
    print("\n1. Initializing Groq client...")
    try:
        client = DirectGroqClient()
    except Exception as e:
        print(f"   ERROR: Failed to initialize Groq client: {e}")
        print("   Make sure 'groq' package is installed: pip install groq")
        return None

    # Test 1: Extract stages and milestones
    print_separator("2. Extracting Stages and Milestones (LLM Call 1)")
    print("   Calling Groq API...")

    system_prompt, user_prompt = build_stages_and_milestones_prompt(SAMPLE_TEXT)

    try:
        response1 = client.call(system_prompt, user_prompt)
        print(f"   Response received: {len(json.dumps(response1))} chars")
    except Exception as e:
        print(f"   ERROR: LLM call failed: {e}")
        return None

    # Parse results
    stages = parse_stages(response1)
    milestones = parse_milestones(response1)

    print(f"\n   Found {len(stages)} stages:")
    for i, stage in enumerate(stages, 1):
        print(f"   {i}. {stage.title} ({stage.stage_type.value})")
        print(f"      Confidence: {stage.confidence:.2f}, Order: {stage.order_hint}")

    print(f"\n   Found {len(milestones)} milestones:")
    by_stage = {}
    for m in milestones:
        if m.stage not in by_stage:
            by_stage[m.stage] = []
        by_stage[m.stage].append(m)

    for stage_name, stage_ms in by_stage.items():
        print(f"   [{stage_name}]")
        for m in stage_ms:
            critical = " [CRITICAL]" if m.is_critical else ""
            print(f"      - {m.name}{critical} ({m.milestone_type})")

    # Test 2: Extract durations and dependencies
    print_separator("3. Extracting Durations and Dependencies (LLM Call 2)")
    print("   Calling Groq API...")

    stages_json = [{"title": s.title, "stage_type": s.stage_type.value} for s in stages]
    milestones_json = [{"name": m.name, "stage": m.stage, "milestone_type": m.milestone_type} for m in milestones]

    system_prompt2, user_prompt2 = build_durations_and_dependencies_prompt(
        SAMPLE_TEXT, stages_json, milestones_json, "Computer Science"
    )

    try:
        response2 = client.call(system_prompt2, user_prompt2)
        print(f"   Response received: {len(json.dumps(response2))} chars")
    except Exception as e:
        print(f"   ERROR: LLM call failed: {e}")
        return None

    # Parse results
    durations = parse_durations(response2)
    dependencies = parse_dependencies(response2)

    print(f"\n   Found {len(durations)} duration estimates:")
    stage_durations = [d for d in durations if d.item_type == "stage"]
    for d in stage_durations:
        print(f"      - {d.item_description}: {d.duration_months_min}-{d.duration_months_max} months ({d.basis})")

    milestone_durations = [d for d in durations if d.item_type == "milestone"]
    print(f"   + {len(milestone_durations)} milestone durations")

    print(f"\n   Found {len(dependencies)} dependencies:")
    for d in dependencies[:8]:
        print(f"      {d.depends_on_item} -> {d.dependent_item} ({d.dependency_type})")
    if len(dependencies) > 8:
        print(f"      ... and {len(dependencies) - 8} more")

    # Summary
    print_separator("4. Summary")
    total_min = sum(d.duration_months_min for d in stage_durations)
    total_max = sum(d.duration_months_max for d in stage_durations)

    print(f"""
   Stages:        {len(stages)}
   Milestones:    {len(milestones)}
   Durations:     {len(durations)}
   Dependencies:  {len(dependencies)}
   Total Duration: {total_min}-{total_max} months ({total_min/12:.1f}-{total_max/12:.1f} years)
""")

    print_separator("Test Complete")
    return {
        "stages": stages,
        "milestones": milestones,
        "durations": durations,
        "dependencies": dependencies
    }


if __name__ == "__main__":
    try:
        result = test_with_groq()
        if result:
            print("\nSUCCESS: LLM test completed!")
            sys.exit(0)
        else:
            print("\nFAILED: Could not complete LLM test")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

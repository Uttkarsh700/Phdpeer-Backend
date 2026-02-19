#!/usr/bin/env python3
"""
Comprehensive test suite for LLM-powered TimelineIntelligenceEngine.
Tests 30 different document types and validates output quality.
"""

import sys
import os
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from difflib import SequenceMatcher

# ============================================================================
# Configuration - Load directly from .env
# ============================================================================

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

script_dir = os.path.dirname(os.path.abspath(__file__))
env_vars = load_env_file(os.path.join(script_dir, '.env'))

LLM_API_KEY = env_vars.get('LLM_API_KEY', '')
LLM_MODEL = env_vars.get('LLM_MODEL', 'llama-3.3-70b-versatile')
LLM_TEMPERATURE = float(env_vars.get('LLM_TEMPERATURE', '0.15'))
LLM_MAX_TOKENS = int(env_vars.get('LLM_MAX_TOKENS', '4096'))
LLM_TIMEOUT = int(env_vars.get('LLM_TIMEOUT_SECONDS', '60'))

# ============================================================================
# Dataclasses (inline)
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
# Groq Client
# ============================================================================

class GroqClient:
    def __init__(self):
        if not LLM_API_KEY:
            raise ValueError("LLM_API_KEY not set")
        from groq import Groq
        self.client = Groq(api_key=LLM_API_KEY, timeout=float(LLM_TIMEOUT))
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS

    def call(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        text = response.choices[0].message.content.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        return json.loads(text)

# ============================================================================
# Prompts
# ============================================================================

STAGES_MILESTONES_SYSTEM = """You are an expert PhD timeline analyst. Analyze academic documents and extract structured timeline information.

Return a JSON object with exactly two keys: "stages" and "milestones".

## Stages (4-8 required)
Each stage:
- stage_type: coursework, literature_review, methodology, data_collection, analysis, writing, submission, defense, publication, or other
- title: Human-readable title
- description: 1-2 sentences
- confidence: 0.0-1.0
- order_hint: 1-10 (chronological)
- keywords: 3-5 keywords
- evidence_quotes: 1-3 quotes from document (max 100 chars each)

## Milestones (2-5 per stage)
Each milestone:
- name: Concise name
- description: 1-2 sentences
- stage: MUST exactly match a stage title
- milestone_type: deliverable, exam, review, publication, presentation, submission, defense, or approval
- evidence_snippet: Quote from document (max 150 chars, NOT empty)
- keywords: 1-3 keywords
- is_critical: true for qualifying exams, proposal defense, dissertation defense, IRB approval, final submission
- confidence: 0.0-1.0

Respond with ONLY valid JSON, no markdown fences, no preamble."""

DURATIONS_DEPS_SYSTEM = """You are an expert PhD timeline analyst. Estimate durations and map dependencies.

Return a JSON object with exactly two keys: "durations" and "dependencies".

## Durations (one per stage AND milestone)
- item_description: MUST exactly match stage title or milestone name
- item_type: "stage" or "milestone"
- duration_weeks_min: > 0
- duration_weeks_max: >= min
- duration_months_min: > 0
- duration_months_max: >= min
- confidence: "low", "medium", or "high"
- basis: "explicit" if doc mentions timing, else "llm_estimate"
- source_text: Quote if explicit, else null

## Dependencies (must form valid DAG - no cycles)
- dependent_item: Exact match to stage/milestone name
- depends_on_item: Exact match to stage/milestone name
- dependency_type: sequential, prerequisite, parallel, or blocks
- confidence: 0.0-1.0
- reason: Brief explanation (max 100 chars)

Respond with ONLY valid JSON, no markdown fences, no preamble."""

# ============================================================================
# Parsers
# ============================================================================

def parse_stages(data: Dict) -> List[DetectedStage]:
    stages = []
    for i, s in enumerate(data.get("stages", [])):
        try:
            stage_type = StageType(s.get("stage_type", "other").lower())
        except ValueError:
            stage_type = StageType.OTHER
        evidence = [EvidenceSnippet(text=q[:200], source="llm", location="doc")
                    for q in s.get("evidence_quotes", []) if isinstance(q, str)]
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
# Fuzzy Matching for Milestone-Stage Validation
# ============================================================================

def fuzzy_match_stage(milestone_stage: str, stage_titles: Set[str], stages: List[DetectedStage]) -> Tuple[str, bool]:
    """
    Find the closest matching stage title using fuzzy matching.

    Returns:
        Tuple of (best_match_title, is_exact_match)
    """
    # Exact match
    if milestone_stage in stage_titles:
        return milestone_stage, True

    target_lower = milestone_stage.lower().strip()

    # Substring containment
    for stage in stages:
        stage_lower = stage.title.lower()
        if target_lower in stage_lower or stage_lower in target_lower:
            return stage.title, True

    # Token overlap - match individual words
    target_tokens = set(_tokenize(target_lower))
    best_token_match = None
    best_token_score = 0.0

    for stage in stages:
        stage_tokens = set(_tokenize(stage.title.lower()))
        intersection = len(target_tokens & stage_tokens)
        union = len(target_tokens | stage_tokens)
        if union > 0:
            score = intersection / union
            if intersection > 0:
                score += 0.1 * intersection
            if score > best_token_score:
                best_token_score = score
                best_token_match = stage.title

    if best_token_score >= 0.3:
        return best_token_match, True

    # Character-level fuzzy matching using SequenceMatcher
    best_match = stages[0].title if stages else milestone_stage
    best_ratio = 0.0

    for stage in stages:
        ratio = SequenceMatcher(None, target_lower, stage.title.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = stage.title

    if best_ratio >= 0.4:
        return best_match, True

    # Partial token matching - if any significant word matches
    significant_target_tokens = {t for t in target_tokens if len(t) > 3}
    for stage in stages:
        stage_tokens = set(_tokenize(stage.title.lower()))
        significant_stage_tokens = {t for t in stage_tokens if len(t) > 3}
        if significant_target_tokens & significant_stage_tokens:
            return stage.title, True

    # Fallback
    if best_ratio >= 0.25:
        return best_match, True

    return stages[0].title if stages else milestone_stage, False


def _tokenize(text: str) -> List[str]:
    """Tokenize text into words."""
    import re
    tokens = re.split(r'[^a-z0-9]+', text.lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    return [t for t in tokens if t and len(t) > 1 and t not in stop_words]


def validate_milestones_fuzzy(milestones: List[ExtractedMilestone], stages: List[DetectedStage]) -> Tuple[List[ExtractedMilestone], List[str]]:
    """
    Validate milestones using fuzzy matching for stage names.

    Returns:
        Tuple of (fixed_milestones, list_of_unfixable_milestone_names)
    """
    if not stages:
        return milestones, []

    stage_titles = {s.title for s in stages}
    fixed_milestones = []
    unfixable = []

    for m in milestones:
        if m.stage in stage_titles:
            fixed_milestones.append(m)
        else:
            best_match, matched = fuzzy_match_stage(m.stage, stage_titles, stages)
            if matched:
                # Create new milestone with fixed stage
                fixed_milestones.append(ExtractedMilestone(
                    name=m.name,
                    description=m.description,
                    stage=best_match,
                    milestone_type=m.milestone_type,
                    evidence_snippet=m.evidence_snippet,
                    keywords=m.keywords,
                    source_segment=m.source_segment,
                    is_critical=m.is_critical,
                    confidence=m.confidence
                ))
            else:
                unfixable.append(m.name)
                # Still add with best guess
                fixed_milestones.append(ExtractedMilestone(
                    name=m.name,
                    description=m.description,
                    stage=best_match,
                    milestone_type=m.milestone_type,
                    evidence_snippet=m.evidence_snippet,
                    keywords=m.keywords,
                    source_segment=m.source_segment,
                    is_critical=m.is_critical,
                    confidence=m.confidence
                ))

    return fixed_milestones, unfixable


# ============================================================================
# DAG Validation
# ============================================================================

def check_dag_valid(dependencies: List[Dependency]) -> Tuple[bool, str]:
    """Check if dependencies form a valid DAG (no cycles)."""
    if not dependencies:
        return True, "No dependencies"

    graph = defaultdict(set)
    all_nodes = set()

    for dep in dependencies:
        graph[dep.dependent_item].add(dep.depends_on_item)
        all_nodes.add(dep.dependent_item)
        all_nodes.add(dep.depends_on_item)

    # DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in all_nodes}

    def has_cycle(node: str) -> bool:
        color[node] = GRAY
        for neighbor in graph.get(node, set()):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and has_cycle(neighbor):
                return True
        color[node] = BLACK
        return False

    for node in all_nodes:
        if color[node] == WHITE:
            if has_cycle(node):
                return False, f"Cycle detected involving {node}"

    return True, "Valid DAG"

# ============================================================================
# Test Cases
# ============================================================================

TEST_CASES = {
    "1_cs_nlp_proposal": {
        "name": "Standard CS PhD - NLP Research",
        "text": """
PhD Research Proposal: Deep Learning for Multilingual Sentiment Analysis

1. Literature Review (6 months)
The first phase involves a comprehensive literature review of existing sentiment analysis
models and multilingual NLP techniques. This will cover transformer architectures,
cross-lingual embeddings, and low-resource language processing. Expected duration: 6 months.

2. Methodology Development (4 months)
Following the literature review, I will develop a novel cross-lingual sentiment analysis
framework using adapter-based transfer learning. This phase includes:
- Architecture design for multilingual transformers
- Custom loss functions for sentiment preservation across languages
- Validation protocol development
Timeline: 4 months for methodology development.

3. Data Collection (8 months)
Data collection will span 8 months and include:
- Twitter data from 15 languages using API
- Reddit multilingual sentiment corpus
- Amazon reviews in European languages
The qualifying exam must be passed before beginning primary data collection.

4. Model Training and Analysis (10 months)
After data collection, analysis will take approximately 10 months:
- Model training on GPU cluster
- Hyperparameter optimization using Bayesian methods
- Cross-validation across language pairs
- Ablation studies and error analysis

5. Dissertation Writing (8 months)
The writing phase requires 8 months:
- Draft methodology and results chapters
- Incorporate advisor feedback
- Final revisions and formatting

6. Defense and Publication
- Dissertation defense preparation: 2 months
- Oral defense examination
- Publication in ACL/EMNLP venues
"""
    },

    "2_biology_cancer": {
        "name": "Biology PhD - Cancer Research",
        "text": """
PhD Research Proposal: Immunotherapy Resistance Mechanisms in Triple-Negative Breast Cancer

Abstract: This research investigates the molecular mechanisms underlying resistance to
immune checkpoint inhibitors in triple-negative breast cancer (TNBC).

Phase 1: Literature Review and Preliminary Analysis (8 months)
Comprehensive review of TNBC biology, immunotherapy mechanisms, and resistance pathways.
Analysis of existing datasets from TCGA and GEO to identify candidate resistance genes.

Phase 2: Cell Line Development (6 months)
Generation of immunotherapy-resistant TNBC cell lines through:
- Sequential treatment with anti-PD-1 antibodies
- Development of resistant clones
- Validation of resistance phenotype
IRB exemption required for cell line work.

Phase 3: Molecular Characterization (12 months)
- Whole transcriptome RNA sequencing
- Single-cell RNA-seq of tumor-immune interactions
- CRISPR screening for resistance genes
- Proteomics analysis of signaling pathways

Phase 4: In Vivo Validation (14 months)
- Mouse xenograft models with humanized immune system
- Treatment studies with combination therapies
- Tissue collection and histopathology
- Flow cytometry analysis of immune infiltrates
IACUC approval required before animal studies begin.

Phase 5: Patient Sample Analysis (8 months)
Analysis of patient tumor samples:
- Tissue microarray construction
- Immunohistochemistry validation
- Correlation with clinical outcomes

Phase 6: Dissertation and Publications (10 months)
Writing and publication of findings in Cancer Cell, Nature Medicine.
Dissertation defense preparation.
"""
    },

    "3_psychology_child_dev": {
        "name": "Psychology PhD - Child Development",
        "text": """
PhD Dissertation Proposal: Executive Function Development in Bilingual Children

Department of Developmental Psychology

This research examines how bilingualism influences executive function development in
children ages 3-8 across diverse socioeconomic backgrounds.

Year 1: Foundation
Coursework in developmental psychology, statistics, and bilingualism.
Literature review of executive function theories and bilingual cognition.
Qualifying examination on developmental cognitive neuroscience.

Year 2: Study Design and IRB Approval
Design of longitudinal study protocol with three cohorts:
- Monolingual English speakers
- Simultaneous bilinguals (Spanish-English)
- Sequential bilinguals (Spanish dominant, English L2)
IRB approval for child participant research - critical milestone.
Pilot testing of assessment battery with 30 children.

Year 3: Data Collection (Primary Phase)
Recruitment of 200 children across three elementary schools.
Assessment battery every 6 months including:
- Dimensional Change Card Sort
- Flanker task
- Working memory span tasks
- Parent and teacher questionnaires
Home visits for naturalistic language sampling.

Year 4: Analysis and Writing
Longitudinal growth curve modeling in R.
Mediation analysis of SES effects.
Dissertation writing with chapter deadlines:
- Introduction: Month 1-2
- Method: Month 2-3
- Results (3 chapters): Month 3-8
- Discussion: Month 8-10
Defense in spring semester.
"""
    },

    "4_engineering_robotics": {
        "name": "Engineering PhD - Robotics",
        "text": """
PhD Research Proposal: Adaptive Manipulation for Unstructured Environments

Department of Mechanical Engineering, Robotics Laboratory

Abstract: Development of robot manipulation systems capable of handling novel objects
in unstructured real-world environments using reinforcement learning and tactile sensing.

Semester 1-2: Coursework and Literature Review
Required coursework in robotics, machine learning, and control theory.
Comprehensive review of manipulation learning, tactile sensing, and sim-to-real transfer.

Semester 3-4: Hardware Development (12 months)
Design and fabrication of tactile sensing array:
- Capacitive pressure sensors
- Slip detection system
- ROS2 integration
Custom end-effector design for Franka Emika robot.
Hardware validation and calibration.

Semester 5-6: Simulation Environment (8 months)
Development of realistic simulation in Isaac Sim:
- Tactile feedback modeling
- Object physics randomization
- Domain randomization for sim-to-real

Semester 7-8: Learning Algorithm Development (10 months)
Reinforcement learning framework development:
- Proximal Policy Optimization baseline
- Tactile feature learning
- Curriculum learning for complex manipulations
Qualifying exam must be passed before this phase.

Semester 9-10: Real-World Experiments (8 months)
Transfer to physical robot system:
- Household object manipulation dataset
- 1000+ manipulation trials
- Human study for teleoperation comparison

Final Year: Dissertation
Writing (6 months), defense preparation (2 months).
Target publications: RSS, ICRA, Science Robotics.
"""
    },

    "5_humanities_history": {
        "name": "Humanities PhD - History",
        "text": """
Dissertation Proposal: Colonial Archives and Indigenous Resistance in 18th Century Peru

This dissertation examines indigenous resistance movements through the lens of colonial
administrative records in the Archivo General de Indias.

Chapter 1: Historiographical Review (12 months)
A comprehensive survey of existing scholarship on colonial Latin America, subaltern
studies, and archive theory. Intensive reading and synthesis of secondary sources in
Spanish, English, and Quechua.

Chapter 2: Archival Research - Seville (8 months)
Extended research stay at the Archivo General de Indias in Seville, Spain.
Examination of viceregal correspondence, tributary records, and judicial proceedings.
Paleography training for 18th-century Spanish documents.

Chapter 3: Fieldwork - Peru (6 months)
Fieldwork in Lima and Cusco examining local archives:
- Archivo Regional del Cusco
- Biblioteca Nacional del Perú
- Parish records and notarial documents
Oral history interviews with descendant communities.
IRB approval required for oral history component.

Chapter 4: Theoretical Framework Development (4 months)
Integration of postcolonial theory with archival practice.
Development of methodological approach for reading colonial documents "against the grain."

Chapter 5: Writing and Revision (18 months)
Dissertation writing with regular chapter submissions to committee.
Incorporation of feedback and revision cycles.
Translation of key primary source documents.

Defense Preparation and Examination (3 months)
Final preparation for oral defense.
Revisions based on committee feedback.
"""
    },

    "6_very_short_vague": {
        "name": "Very Short and Vague Document",
        "text": """
I want to do a PhD about machine learning. I will study neural networks and do some
experiments. Then I will write my dissertation and defend it.
"""
    },

    "7_no_research_plan": {
        "name": "No Research Plan at All",
        "text": """
Thoughts on Artificial Intelligence and Society

Artificial intelligence is transforming our world in unprecedented ways. Machine learning
algorithms now power everything from recommendation systems to autonomous vehicles. The
implications for society are profound and far-reaching.

Deep learning has achieved remarkable success in computer vision, natural language
processing, and game playing. AlphaGo's victory over Lee Sedol marked a watershed moment
in AI history. GPT models have demonstrated surprising emergent capabilities.

The ethical implications deserve careful consideration. Bias in training data leads to
biased predictions. Privacy concerns arise from large-scale data collection. Job
displacement threatens traditional employment patterns.

Regulation of AI remains challenging. Different jurisdictions take varying approaches.
The EU's AI Act represents one framework. The US relies more on sector-specific rules.

Future developments may include artificial general intelligence, though timelines remain
uncertain. Brain-computer interfaces offer another frontier. Quantum machine learning
could provide computational advantages.

These are important topics that merit serious academic study and public discourse.
"""
    },

    "8_explicit_monthly_timeline": {
        "name": "Document with Explicit Month-by-Month Timeline",
        "text": """
PhD Timeline: Computational Neuroscience Research

Starting January 2026, I will begin my doctoral research on neural network models of
memory consolidation.

January 2026 - June 2026 (6 months): Literature Review
Comprehensive review of hippocampal memory models and deep learning architectures.
Monthly deliverables: annotated bibliography, literature map, gap analysis paper.

July 2026 - October 2026 (4 months): Methodology Development
Design of novel recurrent neural network architecture inspired by hippocampal replay.
Month-by-month: architecture design, implementation, validation, documentation.

November 2026 - June 2027 (8 months): Data Collection
Collection of neural recording data from collaborating neuroscience labs.
EEG and fMRI data acquisition following IRB-approved protocols.

July 2027 - February 2028 (8 months): Model Development and Training
Implementation and training of computational models.
Validation against experimental data.

March 2028 - October 2028 (8 months): Analysis and Iteration
Detailed analysis of model behavior.
Iterative refinement based on findings.
Comparison with alternative architectures.

November 2028 - June 2029 (8 months): Dissertation Writing
Writing of dissertation chapters with advisor feedback cycles.
Target completion: June 2029.

July 2029 - September 2029 (3 months): Defense Preparation
Final preparation and dissertation defense.
Expected graduation: Fall 2029.
"""
    },

    "9_interdisciplinary": {
        "name": "Interdisciplinary Proposal",
        "text": """
Interdisciplinary PhD Proposal: Computational Models of Human Decision-Making

Department of Computer Science and Department of Psychology Joint Program

This research bridges computational modeling with experimental psychology to understand
human decision-making under uncertainty.

COMPUTER SCIENCE COMPONENT:

Technical Methodology (Year 1-2)
- Development of Bayesian inference algorithms for modeling choice behavior
- Implementation of reinforcement learning models with bounded rationality
- Creation of computational cognitive architectures
- Programming in Python, Stan, and custom simulation frameworks

PSYCHOLOGY COMPONENT:

Experimental Design (Year 2-3)
- Design of behavioral experiments testing model predictions
- IRB approval for human subjects research (critical milestone)
- Recruitment of 500+ participants through Prolific and campus recruitment
- Eye-tracking studies of attention during decision-making
- EEG recording for neural correlates of uncertainty

INTEGRATION PHASE (Year 3-4)

Computational-Experimental Synthesis
- Fitting computational models to behavioral data
- Neural network decoders for EEG signals
- Validation of theoretical predictions
- Cross-validation across experimental paradigms

Writing and Defense (Year 4)
- Joint dissertation satisfying both department requirements
- Publication in both venues (NeurIPS, Psychological Review)
- Defense before combined committee

The qualifying exam will cover both computational methods and psychological theory.
Students must pass requirements from both departments.
"""
    },

    "10_parallel_complex": {
        "name": "Parallel Stages and Complex Dependencies",
        "text": """
PhD Research Plan: Sustainable Urban Transportation

Note: Several phases of this research will occur simultaneously to maximize efficiency.

YEAR 1 (Parallel Activities):
- Literature Review and Coursework will happen simultaneously during the first year
- While completing required doctoral courses, I will conduct the systematic literature
  review on sustainable transportation systems
- Additionally, preliminary data collection from public transit APIs will begin
- These three activities run in parallel throughout Year 1

YEAR 2 (Overlapping Phases):
- Methodology development continues while data collection expands
- Survey design and IRB approval happen concurrently with technical system development
- Field observations begin before survey deployment is complete
- Analysis of preliminary data overlaps with continued data collection

YEAR 3 (Concurrent Streams):
- Final data collection
- Ongoing analysis
- Begin dissertation writing (introduction and literature review chapters)
- Publication of initial findings runs parallel to continued research

YEAR 4:
- Complete analysis while continuing to write
- Finish all dissertation chapters
- Defense preparation occurs alongside final revisions
- Post-defense: Simultaneous journal submissions and graduation preparation

Key Dependencies:
- IRB approval must precede human subjects research
- Qualifying exam must pass before advancing to candidacy
- All coursework must complete before defense scheduling
- Literature review informs methodology development
"""
    },

    "11_poorly_written": {
        "name": "Poorly Written Document with Errors",
        "text": """
my phd reserch propsal

so basically i want too study the thing about computers and how they learns stuff.
machine lerning is very intresting topic and i think it will be good for phd.

first i will read some papers about machine lerning. maybe like 6 month or something
idk exactly. there are alot of papers out there so it will take time.

then i need to do some experimants. i will use python probly and maybe tensorflow or
pytorch. the experimants will show if my idea works or not. this part is importent.

after that i will rite my thesis. writing is hard but i will do my best. my advisor
will help me fix the mistakes and make it better.

at the end there is defence where professors ask questions. i am nervous about this
but everyone says it will be fine if you prepare good.

i dont have exact timeline because things might change. flexability is importent in
reserch i think. sometimes experimants fail and you have to try again.

the main goal is to contribute to sciense and get the phd degree. this is my dream
since i was young and now i have the chance to make it happen.

thankyou for considering my proposal i hope you will give me the oportunity.
"""
    },

    "12_medical_clinical": {
        "name": "Medical/Clinical PhD",
        "text": """
MD-PhD Research Proposal: Novel Biomarkers for Early Alzheimer's Detection

Department of Neurology and Graduate School of Biomedical Sciences

Abstract: This research aims to identify and validate blood-based biomarkers for
pre-symptomatic Alzheimer's disease detection, enabling earlier intervention.

Phase 1: Clinical Training and Literature Review (Year 1)
- Complete required clinical rotations in neurology
- Comprehensive literature review on AD biomarkers, proteomics, and early detection
- Coursework in clinical research methodology and biostatistics
- CITI training and Good Clinical Practice certification

Phase 2: Study Protocol Development (6 months)
- Design longitudinal cohort study
- IRB full board review for human subjects research (critical milestone)
- Establish recruitment partnerships with memory clinics
- Develop biobanking protocols

Phase 3: Patient Recruitment and Sample Collection (18 months)
- Enroll 500 participants across three risk categories:
  * Cognitively normal APOE4 carriers
  * Mild cognitive impairment
  * Healthy controls
- Baseline blood draws, cognitive testing, MRI imaging
- 6-month follow-up assessments

Phase 4: Biomarker Discovery (12 months)
- High-throughput proteomics on Olink platform
- Metabolomics profiling
- Machine learning for biomarker panel selection
- Validation in independent cohort

Phase 5: Clinical Validation (10 months)
- Head-to-head comparison with CSF biomarkers
- Correlation with amyloid PET imaging
- Sensitivity/specificity analysis
- Regulatory pathway assessment for clinical translation

Phase 6: Dissertation and Career Transition (8 months)
- Dissertation writing following IMRAD structure
- Defense and final revisions
- Preparation for residency match
- Publication in JAMA Neurology, Nature Medicine

Total anticipated duration: 5 years (including clinical requirements)
"""
    },

    "13_economics_behavioral": {
        "name": "Economics PhD - Behavioral Economics",
        "text": """This dissertation investigates how cognitive biases influence retirement savings decisions among gig economy workers. The literature review phase covers behavioral economics theory, prospect theory, nudge frameworks, and gig economy labor research spanning 6 months. Methodology involves designing three randomized controlled experiments testing different choice architecture interventions on a custom-built retirement savings platform. Platform development takes 4 months. IRB approval for human subjects research is required before any experiments, estimated at 3 months. Experiment 1 tests default enrollment framing effects with 500 Uber and Lyft drivers over 3 months. Experiment 2 tests social comparison nudges with 500 DoorDash and Instacart workers over 3 months. Experiment 3 tests temporal framing of future self with 500 freelancers from Upwork over 3 months. Each experiment requires separate recruitment, consent, and debriefing. Data analysis uses regression discontinuity design, instrumental variables, and Bayesian hierarchical models. Analysis takes 4 months. Three papers target American Economic Review, Journal of Behavioral Economics, and Quarterly Journal of Economics. Qualifying exam is after the first experiment. Proposal defense in year 2. Final defense in year 5."""
    },

    "14_environmental_climate": {
        "name": "Environmental Science PhD - Climate Change",
        "text": """Research focuses on modeling permafrost thaw feedback loops and their contribution to atmospheric methane emissions in the Siberian Arctic. Year 1 involves comprehensive review of permafrost dynamics literature, climate modeling approaches, and remote sensing of Arctic regions, lasting 7 months. Simultaneously, the student completes coursework in climate science, geophysics, and advanced numerical methods. Fieldwork planning requires permits from Russian research authorities which take approximately 5 months to obtain. Two field campaigns to Yakutsk and surrounding regions are planned: summer field campaign 1 in year 2 lasting 3 months collecting soil cores, installing temperature sensors, and measuring methane flux using eddy covariance towers. Lab analysis of soil samples for carbon content and microbial community analysis takes 4 months. Summer field campaign 2 in year 3 lasting 2 months for follow-up measurements and equipment maintenance. Climate model development using CESM2 framework with custom permafrost module takes 6 months. Model calibration against field data and satellite observations from MODIS and Sentinel-1 takes 3 months. Model projection runs under SSP scenarios take 2 months. Writing targets include papers in Nature Climate Change and Global Biogeochemical Cycles. Comprehensive exam after field campaign 1. Defense in year 5."""
    },

    "15_law_constitutional": {
        "name": "Law PhD - Constitutional Law",
        "text": """This doctoral thesis examines the evolution of free speech protections in digital public forums across five constitutional democracies: the United States, Germany, India, South Africa, and Brazil. The research begins with extensive doctrinal analysis of constitutional texts, landmark court decisions, and legislative frameworks in each jurisdiction. This comparative legal analysis phase spans 8 months. Theoretical framework development draws on Habermas public sphere theory, Balkins digital constitutionalism, and Lessigs code as law, requiring 3 months. Empirical component involves qualitative interviews with 40 constitutional law scholars, 20 tech policy makers, and 15 judges across the five countries. Ethics approval, interview scheduling, and travel arrangements take 4 months to coordinate. Interview data collection requires 6 months of international travel. Qualitative coding and thematic analysis using NVivo takes 3 months. Case study writing for each jurisdiction takes 2 months each, totaling 10 months. Comparative analysis chapter takes 3 months. The student presents at Law and Society Association annual meeting and submits articles to Harvard Law Review and International Journal of Constitutional Law. Comprehensive exams in year 2. Dissertation defense in year 5."""
    },

    "16_mathematics_pure": {
        "name": "Mathematics PhD - Pure Math",
        "text": """This research extends the Langlands program by establishing new cases of functoriality for automorphic forms on exceptional groups. The first 10 months are dedicated to mastering prerequisite material: representation theory of p-adic groups, automorphic forms, L-functions, and the trace formula. Regular seminar participation and reading courses with the advisor supplement this phase. The core research phase involves three main problems. Problem 1: Establishing the local Langlands correspondence for G2, building on work of Gan-Savin. Estimated 8 months. Problem 2: Proving functorial transfer from G2 to GL7 using the theta correspondence. Estimated 6 months. Problem 3: Applications to special values of L-functions attached to G2 automorphic forms. Estimated 5 months. These problems are sequential as each builds on results from the previous one. Writing is continuous, with results formalized as obtained. Three papers are expected, each corresponding to a problem. The qualifying exam includes both written and oral components in algebra and number theory, scheduled for end of year 1. Dissertation defense expected in year 5. Student will present at Joint Mathematics Meetings and submit to Annals of Mathematics and Inventiones Mathematicae."""
    },

    "17_education_stem": {
        "name": "Education PhD - STEM Education",
        "text": """This mixed-methods study investigates the impact of culturally responsive pedagogy on STEM identity development among first-generation college students of color. Phase 1 is a systematic literature review covering culturally responsive teaching, STEM identity theory, critical race theory in education, and community cultural wealth frameworks. Duration: 4 months. Phase 2 involves developing the intervention: a semester-long culturally responsive STEM seminar series co-designed with community partners. Curriculum development takes 3 months. Phase 3 is obtaining IRB approval and establishing partnerships with 4 minority-serving institutions. Duration: 3 months. Phase 4 quantitative strand: pre-post survey administration of the STEM Identity Scale and Science Motivation Questionnaire to 300 students across treatment and control groups over two semesters. Duration: 9 months. Phase 5 qualitative strand: conducting semi-structured interviews with 30 purposefully selected participants, classroom observations of 24 seminar sessions, and collecting student reflective journals. Runs concurrent with Phase 4 over 9 months. Phase 6 data integration: joint display analysis merging quantitative outcomes with qualitative themes using a convergent parallel design. Duration: 3 months. Phase 7 writing: five chapter dissertation plus two journal articles for Journal of Research in Science Teaching and Race Ethnicity and Education. Duration: 5 months. Qualifying exam after Phase 2. Proposal defense after Phase 3. Final defense in year 4."""
    },

    "18_sociology_urban": {
        "name": "Sociology PhD - Urban Sociology",
        "text": """This ethnographic study examines how immigrant communities navigate housing precarity in three gentrifying neighborhoods in Los Angeles. The research begins with 5 months of literature review on gentrification, immigrant incorporation, housing policy, and urban ethnography methods. The student will take courses in ethnographic methods, urban sociology, and immigration studies during year 1. Gaining community access and building trust with immigrant organizations takes approximately 4 months of volunteer work and attendance at community events. Full-time ethnographic fieldwork spans 14 months across three neighborhoods: Boyle Heights, Koreatown, and Historic Filipinotown. Data collection includes 60 in-depth life history interviews, 200 hours of participant observation, document analysis of housing policies and tenant organizing materials, and photography. All interviews will be conducted in English, Spanish, or Korean with the aid of research assistants. Analysis uses grounded theory with constant comparative method, producing approximately 2000 pages of field notes to code. Analysis takes 5 months. Writing the ethnographic monograph-style dissertation takes 8 months with the goal of eventual book publication with University of California Press. Articles target American Sociological Review and City and Community. Qualifying exam end of year 1. Proposal defense year 2. Final defense year 5."""
    },

    "19_chemistry_materials": {
        "name": "Chemistry PhD - Materials Science",
        "text": """This research develops novel perovskite-organic hybrid materials for next-generation solar cells with target efficiency above 30 percent. Literature review covers perovskite crystal chemistry, organic hole transport materials, interface engineering, and device physics over 4 months. Lab setup and safety training takes 2 months including certification for working with lead-based compounds. Synthesis phase 1 involves preparing 50 perovskite compositions varying the A-site, B-site, and halide components using solution processing and vapor deposition methods. Duration: 6 months. Characterization uses XRD, SEM, TEM, PL spectroscopy, and Hall effect measurements. Running parallel to synthesis: 6 months. Device fabrication: building solar cells in cleanroom facility using spin coating, thermal evaporation, and atomic layer deposition. 100 devices across 10 architectures. Duration: 5 months. Device testing: current-voltage measurements, external quantum efficiency, stability testing under accelerated aging conditions. Duration: 3 months. Computational work using DFT calculations to understand electronic structure runs parallel to experimental work from month 6 to month 18. Publications target Nature Energy, Advanced Materials, and ACS Energy Letters. Qualifying exam after synthesis phase. Proposal defense year 2. Patent application expected. Final defense year 4."""
    },

    "20_polisci_ir": {
        "name": "Political Science PhD - International Relations",
        "text": """This dissertation examines the effectiveness of economic sanctions regimes imposed by the European Union from 2000 to 2025 using a multi-method research design. The initial phase involves constructing a comprehensive dataset of all EU autonomous sanctions, requiring manual coding of 350 Council decisions and regulations. Database construction takes 7 months. Literature review on sanctions theory, compliance mechanisms, and EU foreign policy spans 5 months running parallel to data collection. Quantitative analysis employs panel data regression, synthetic control methods, and event study designs to estimate causal effects of sanctions on target state behavior. Statistical analysis takes 4 months. Qualitative component involves process tracing of 6 carefully selected case studies: Russia, Iran, Syria, Myanmar, Belarus, and Zimbabwe. Each case requires analyzing diplomatic cables obtained through FOIA requests, EU institutional documents, and media reporting. Case study research takes 8 months. Elite interviews with 25 EU foreign policy officials, sanctions coordinators, and diplomats in Brussels and national capitals. Interviews require 4 months of travel. Mixed-method integration using Bayesian process tracing to update quantitative findings with qualitative evidence. Duration: 3 months. Writing five substantive chapters plus introduction and conclusion takes 6 months. Target journals: International Organization, European Journal of Political Research, and Journal of Conflict Resolution. Comprehensive exams year 2. Defense year 5."""
    },

    "21_music_ethnomusicology": {
        "name": "Music PhD - Ethnomusicology",
        "text": """This research documents and analyzes the endangered musical traditions of the Sámi people in northern Norway, focusing on joik vocal practices and their role in cultural identity preservation. Preparatory phase includes learning Northern Sámi language to conversational level through intensive courses at the University of Tromsø, taking approximately 6 months. Literature review covers ethnomusicology methodology, Indigenous music studies, Sámi cultural history, and archival ethnography. Duration: 5 months. Building relationships with Sámi communities and obtaining consent from community elders and cultural organizations takes 4 months of preliminary visits. Primary fieldwork in Kautokeino and Karasjok communities spans 10 months of immersive participant observation. Data collection includes audio and video recording of joik performances, semi-structured interviews with 35 joik practitioners across three generations, documentation of teaching and learning practices, and attendance at cultural festivals. Archival research at the Sámi Archives in Karasjok and the National Library of Norway in Oslo takes 2 months. Musical analysis combines computational methods using MIR tools with traditional ethnomusicological transcription and analysis. Duration: 4 months. Community feedback sessions to validate interpretations take 2 months. Dissertation writing takes 7 months. A documentary film component accompanies the written dissertation. Target publications: Ethnomusicology and Popular Music. Comprehensive exam year 2. Defense year 5."""
    },

    "22_nursing_public_health": {
        "name": "Nursing PhD - Public Health",
        "text": """This study develops and tests a mobile health intervention for diabetes self-management among Hispanic adults in rural communities. Phase 1: Systematic review of mHealth diabetes interventions and health disparities literature. 4 months. Phase 2: Community-based participatory research with 3 community health centers to design the app. 8 focus groups with 48 participants. 3 months. Phase 3: App development with bilingual interface, medication reminders, glucose logging, and telehealth integration. Working with CS collaborators. 5 months. Phase 4: Usability testing with 15 participants using think-aloud protocol. Iterative refinement. 2 months. Phase 5: IRB approval and clinical trial registration at ClinicalTrials.gov. 3 months. Phase 6: Pilot RCT with 80 participants randomized to intervention versus usual care over 6 months. Primary outcome: HbA1c levels. Secondary outcomes: self-efficacy, medication adherence, quality of life. Data collection at baseline, 3 months, and 6 months. Phase 7: Statistical analysis using intention-to-treat with mixed-effects models. Mediation analysis for self-efficacy pathways. 3 months. Phase 8: Dissertation writing and preparation of manuscripts for Diabetes Care, Journal of Medical Internet Research, and Hispanic Health Care International. 5 months. Qualifying exam after Phase 3. Proposal defense after Phase 5. Final defense year 4."""
    },

    "23_philosophy_ethics": {
        "name": "Philosophy PhD - Ethics",
        "text": """This dissertation develops a novel ethical framework for artificial intelligence decision-making in healthcare, bridging analytic philosophy, bioethics, and computer science. The initial research phase involves deep engagement with existing ethical theories: consequentialism, deontology, virtue ethics, care ethics, and principlism as applied to medical AI. This reading and analysis phase takes 8 months. Conceptual analysis of key concepts including moral responsibility, algorithmic fairness, explainability, and patient autonomy in automated systems takes 4 months. Original philosophical argumentation constructing the proposed framework takes 6 months of intensive writing and revision. Empirical component: structured interviews with 30 physicians, 20 AI developers, and 20 medical ethicists about moral intuitions regarding AI clinical decision support. IRB approval and interviews take 5 months combined. Analysis of empirical data using reflective equilibrium methodology to test the framework against practitioner intuitions takes 3 months. Applied chapter examining three case studies: AI in radiology diagnosis, algorithmic triage in emergency departments, and predictive models for end-of-life care. Each case study takes approximately 2 months. Engagement with existing AI ethics proposals from IEEE, EU AI Act, and WHO guidelines takes 2 months. Writing and integrating the complete dissertation takes 6 months. Target publications: Philosophy and Public Affairs, Bioethics, and AI and Ethics. Qualifying paper submitted year 1. Comprehensive exam year 2. Defense year 5."""
    },

    "24_architecture_sustainable": {
        "name": "Architecture PhD - Sustainable Design",
        "text": """This practice-based research develops computational design tools for optimizing passive cooling strategies in affordable housing for tropical climates. Literature review spans vernacular architecture of tropical regions, computational fluid dynamics in building design, parametric design methods, and thermal comfort standards. Duration 5 months. Fieldwork phase involves documenting 40 existing naturally ventilated buildings across three tropical cities: Chennai, Dar es Salaam, and Manaus. On-site thermal measurements, airflow visualization, and occupant comfort surveys. Total fieldwork duration across three trips: 6 months. Development of parametric design tool using Grasshopper for Rhino with custom Python components for thermal simulation. Tool connects to EnergyPlus engine for validation. Development takes 7 months. Validation study comparing tool predictions against measured data from 10 fieldwork buildings. Duration: 3 months. Design exploration: using the tool to generate and evaluate 500 housing design variants optimizing for thermal comfort, construction cost, and daylight availability. Multi-objective optimization using genetic algorithms. Duration: 4 months. Expert evaluation: 12 architects and engineers review selected designs through structured workshops. Duration: 2 months. Building a full-scale prototype room at the university research facility. Construction and monitoring over 4 months. Dissertation integrates written analysis with design portfolio. Writing: 5 months. Publications target Building and Environment, Energy and Buildings, and Architectural Science Review. Annual review with committee each year. Defense year 5."""
    },

    "25_linguistics_computational": {
        "name": "Linguistics PhD - Computational Linguistics",
        "text": """This research creates the first comprehensive computational grammar and natural language processing toolkit for Quechua, an endangered Indigenous language spoken by 8 million people across South America. Phase 1 involves reviewing existing Quechua linguistic descriptions, computational approaches to low-resource languages, and morphological analysis frameworks. 4 months. Phase 2 fieldwork: traveling to Cusco, Peru and Cochabamba, Bolivia to collect text and speech data from native speakers. Recording 200 hours of speech, transcribing oral narratives, and eliciting grammatical judgments. Community consent protocols through Indigenous community organizations. Fieldwork duration: 5 months. Phase 3 corpus construction: digitizing, annotating, and formatting collected data into a machine-readable corpus with morphological, syntactic, and semantic annotation layers. Developing annotation guidelines with linguistic consultants. Duration: 6 months. Phase 4 computational grammar: implementing a finite-state morphological analyzer and a dependency parser for Quechua using neural methods adapted for agglutinative morphology. Duration: 5 months. Phase 5 NLP toolkit: building and releasing open-source tools including a tokenizer, POS tagger, lemmatizer, and a machine translation system between Quechua and Spanish. Duration: 4 months. Phase 6 evaluation: intrinsic evaluation against held-out test data and extrinsic evaluation through downstream tasks. Community evaluation by having native speakers assess tool quality. Duration: 3 months. All tools and data will be released under open licenses. Publications target Computational Linguistics and Language Resources and Evaluation. Qualifying exam year 1. Defense year 4."""
    },

    "26_empty_document": {
        "name": "Empty Document",
        "text": ""
    },

    "27_single_word": {
        "name": "Single Word Document",
        "text": "PhD"
    },

    "28_french_language": {
        "name": "Document in Another Language (French)",
        "text": """Cette thèse de doctorat examine les effets du changement climatique sur la biodiversité marine en Méditerranée. La première phase consiste en une revue de littérature approfondie de 6 mois. La collecte de données sur le terrain durera 8 mois, incluant des plongées de recherche et des analyses en laboratoire. Lanalyse statistique prendra 4 mois. La rédaction de la thèse est prévue sur 5 mois. La soutenance est prévue en cinquième année."""
    },

    "29_contradictory_info": {
        "name": "Document with Contradictory Information",
        "text": """This PhD research on quantum computing will begin with a 3 month literature review. The literature review is expected to take 12 months. Data collection starts before the methodology is designed. The defense happens in year 2 but the total program duration is 6 years. Writing begins at the start and also at the end. The qualifying exam is the last milestone but also must be completed before data collection. Coursework takes 24 months but only covers 2 courses. Analysis will be done in 1 week but requires processing 500 terabytes of data."""
    },

    "30_detailed_substages": {
        "name": "Extremely Detailed Proposal with Substages",
        "text": """This PhD investigates federated learning for privacy-preserving medical imaging diagnostics. Stage 1 Literature Review has three substages: 1a Survey of federated learning algorithms including FedAvg, FedProx, SCAFFOLD, and FedNova lasting 2 months, 1b Review of medical imaging deep learning covering CNN architectures, vision transformers, and foundation models for 2 months, 1c Analysis of privacy regulations HIPAA, GDPR, and institutional data sharing agreements for 1 month. Stage 2 System Design has substages: 2a Design the federated architecture supporting 10 hospital nodes with heterogeneous GPU resources for 2 months, 2b Implement secure aggregation protocol using homomorphic encryption for 3 months, 2c Develop differential privacy mechanisms with formal epsilon-delta guarantees for 2 months. Stage 3 Data Preparation: 3a Negotiate data use agreements with 10 partner hospitals taking 4 months, 3b Standardize DICOM imaging data across sites harmonizing acquisition protocols for 2 months, 3c Create train-validation-test splits maintaining patient privacy across sites for 1 month. Stage 4 Experiments: 4a Train baseline centralized models on each sites local data for 1 month, 4b Run federated training across all sites comparing 4 aggregation strategies for 3 months, 4c Evaluate on external test set from 2 holdout hospitals for 1 month, 4d Ablation studies on communication rounds, local epochs, and privacy budget for 2 months. Stage 5 Clinical Validation: 5a Reader study with 15 radiologists comparing AI-assisted versus unassisted diagnosis for 3 months, 5b Subgroup analysis across demographics, imaging equipment, and disease subtypes for 2 months. Stage 6 Writing and Defense: Write 6 chapters over 5 months. Publications target Nature Medicine, IEEE TPAMI, and MICCAI conference. First paper submitted month 18, second month 24, third month 30. Qualifying exam month 12. Proposal defense month 18. Final defense month 42."""
    }
}

# ============================================================================
# Test Runner
# ============================================================================

@dataclass
class TestResult:
    test_name: str
    success: bool
    num_stages: int
    stage_types: List[str]
    num_milestones: int
    milestones_match_stages: bool
    unmatched_milestones: List[str]
    num_durations: int
    all_durations_positive: bool
    invalid_durations: List[str]
    num_dependencies: int
    dag_valid: bool
    dag_message: str
    errors: List[str]
    warnings: List[str]
    llm_time_seconds: float

def run_single_test(client: GroqClient, test_id: str, test_data: Dict) -> TestResult:
    """Run a single test case and return results."""
    test_name = test_data["name"]
    text = test_data["text"]
    errors = []
    warnings = []

    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")

    start_time = time.time()

    # Call 1: Stages and Milestones
    try:
        print("  [1/2] Extracting stages and milestones...")
        user_prompt = f"Analyze this PhD document:\n\n{text}\n\nReturn JSON with 'stages' and 'milestones'."
        response1 = client.call(STAGES_MILESTONES_SYSTEM, user_prompt)
        stages = parse_stages(response1)
        milestones = parse_milestones(response1)
        print(f"        Found {len(stages)} stages, {len(milestones)} milestones")
    except Exception as e:
        errors.append(f"LLM Call 1 failed: {str(e)}")
        return TestResult(
            test_name=test_name, success=False, num_stages=0, stage_types=[],
            num_milestones=0, milestones_match_stages=False, unmatched_milestones=[],
            num_durations=0, all_durations_positive=False, invalid_durations=[],
            num_dependencies=0, dag_valid=False, dag_message="N/A",
            errors=errors, warnings=warnings, llm_time_seconds=time.time()-start_time
        )

    # Call 2: Durations and Dependencies
    try:
        print("  [2/2] Extracting durations and dependencies...")
        stage_titles = [s.title for s in stages]
        milestone_names = [m.name for m in milestones]
        user_prompt2 = f"""Stages: {json.dumps(stage_titles)}
Milestones: {json.dumps(milestone_names)}
Document: {text[:4000]}
Return JSON with 'durations' and 'dependencies'."""
        response2 = client.call(DURATIONS_DEPS_SYSTEM, user_prompt2)
        durations = parse_durations(response2)
        dependencies = parse_dependencies(response2)
        print(f"        Found {len(durations)} durations, {len(dependencies)} dependencies")
    except Exception as e:
        errors.append(f"LLM Call 2 failed: {str(e)}")
        durations = []
        dependencies = []

    llm_time = time.time() - start_time

    # Validation
    stage_titles_set = {s.title for s in stages}
    stage_types = [s.stage_type.value for s in stages]

    # Check milestones match stages using fuzzy matching
    milestones, unmatched = validate_milestones_fuzzy(milestones, stages)
    milestones_match = len(unmatched) == 0
    if unmatched:
        warnings.append(f"Unfixable milestone mappings: {unmatched[:3]}")

    # Check durations positive
    invalid_durations = []
    for d in durations:
        if d.duration_months_min <= 0 or d.duration_weeks_min <= 0:
            invalid_durations.append(d.item_description)
    all_durations_positive = len(invalid_durations) == 0

    # Check DAG
    dag_valid, dag_message = check_dag_valid(dependencies)
    if not dag_valid:
        warnings.append(f"DAG invalid: {dag_message}")

    # Additional warnings
    if len(stages) < 3:
        warnings.append(f"Few stages detected ({len(stages)})")
    if len(milestones) < len(stages):
        warnings.append(f"Fewer milestones ({len(milestones)}) than stages ({len(stages)})")

    success = len(errors) == 0 and milestones_match and all_durations_positive and dag_valid

    return TestResult(
        test_name=test_name,
        success=success,
        num_stages=len(stages),
        stage_types=stage_types,
        num_milestones=len(milestones),
        milestones_match_stages=milestones_match,
        unmatched_milestones=unmatched[:5],
        num_durations=len(durations),
        all_durations_positive=all_durations_positive,
        invalid_durations=invalid_durations[:5],
        num_dependencies=len(dependencies),
        dag_valid=dag_valid,
        dag_message=dag_message,
        errors=errors,
        warnings=warnings,
        llm_time_seconds=llm_time
    )

def print_result(result: TestResult):
    """Print formatted test result."""
    status = "✓ PASS" if result.success else "✗ FAIL"
    print(f"\n  Result: {status}")
    print(f"  Time: {result.llm_time_seconds:.2f}s")
    print(f"  ┌─────────────────────────────────────────────────────────────")
    print(f"  │ Stages:      {result.num_stages} detected")
    print(f"  │ Stage Types: {', '.join(result.stage_types[:5])}")
    print(f"  │ Milestones:  {result.num_milestones} detected")
    print(f"  │ Milestones Match Stages: {'Yes' if result.milestones_match_stages else 'NO - ' + str(result.unmatched_milestones)}")
    print(f"  │ Durations:   {result.num_durations} estimates")
    print(f"  │ All Durations > 0: {'Yes' if result.all_durations_positive else 'NO - ' + str(result.invalid_durations)}")
    print(f"  │ Dependencies: {result.num_dependencies}")
    print(f"  │ DAG Valid:   {'Yes' if result.dag_valid else 'NO'} ({result.dag_message})")
    print(f"  └─────────────────────────────────────────────────────────────")

    if result.errors:
        print(f"  ERRORS:")
        for e in result.errors:
            print(f"    ✗ {e}")
    if result.warnings:
        print(f"  WARNINGS:")
        for w in result.warnings:
            print(f"    ⚠ {w}")

def main():
    print("="*70)
    print("COMPREHENSIVE LLM TIMELINE ENGINE TEST SUITE")
    print("="*70)
    print(f"Model: {LLM_MODEL}")
    print(f"API Key: {LLM_API_KEY[:20]}..." if LLM_API_KEY else "API Key: NOT SET")
    print(f"Tests: {len(TEST_CASES)}")

    try:
        client = GroqClient()
    except Exception as e:
        print(f"\nFATAL: Could not initialize Groq client: {e}")
        sys.exit(1)

    results = []

    for test_id, test_data in TEST_CASES.items():
        try:
            result = run_single_test(client, test_id, test_data)
            results.append(result)
            print_result(result)
        except Exception as e:
            print(f"\n  EXCEPTION: {e}")
            results.append(TestResult(
                test_name=test_data["name"], success=False, num_stages=0, stage_types=[],
                num_milestones=0, milestones_match_stages=False, unmatched_milestones=[],
                num_durations=0, all_durations_positive=False, invalid_durations=[],
                num_dependencies=0, dag_valid=False, dag_message="Exception",
                errors=[str(e)], warnings=[], llm_time_seconds=0
            ))

        # Rate limiting pause
        time.sleep(1)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed = sum(1 for r in results if r.success)
    failed = len(results) - passed

    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print(f"\nFailed Tests:")
        for r in results:
            if not r.success:
                print(f"  ✗ {r.test_name}")
                for e in r.errors:
                    print(f"      Error: {e}")
                for w in r.warnings:
                    print(f"      Warning: {w}")

    print(f"\nTotal LLM time: {sum(r.llm_time_seconds for r in results):.2f}s")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

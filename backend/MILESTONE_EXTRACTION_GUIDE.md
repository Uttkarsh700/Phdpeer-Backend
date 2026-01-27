## Overview

The `extract_milestones()` method generates 2-5 milestone candidates for each detected PhD stage. Milestones are **generic and editable** - they serve as templates that users can customize, with no hard commitments.

## Output Format

### ExtractedMilestone Structure

```python
@dataclass
class ExtractedMilestone:
    name: str                  # Concise milestone name (≤60 chars)
    description: str           # Detailed description (≤200 chars)
    stage: str                 # Associated stage name
    milestone_type: str        # deliverable, exam, review, publication
    evidence_snippet: str      # Evidence from document (≤150 chars)
    keywords: List[str]        # Matched keywords
    source_segment: int        # Segment index (None for generic)
    is_critical: bool          # Critical milestone flag
    confidence: float          # 0.0 to 1.0
```

### Example Output

```python
ExtractedMilestone(
    name="Complete Literature Survey",
    description="Review and synthesize existing research in the field",
    stage="Literature Review",
    milestone_type="deliverable",
    evidence_snippet="...comprehensive literature review to survey existing work...",
    keywords=["literature review", "survey"],
    source_segment=2,
    is_critical=False,
    confidence=0.7
)
```

## Extraction Methods

### Method 1: Explicit Mentions

Extracts milestones explicitly mentioned in the text.

**Example Text:**

```
The research will begin with a comprehensive literature review.
Ethics approval must be obtained before data collection.
The dissertation defense will be scheduled after final revisions.
```

**Extracted Milestones:**
- "Comprehensive Literature Review" (from explicit mention)
- "Ethics Approval" (from explicit mention, marked critical)
- "Dissertation Defense" (from explicit mention, marked critical)

**Characteristics:**
- Higher confidence (0.6-0.8)
- Linked to source segments
- Evidence snippets from actual text

### Method 2: Generic Templates

Generates generic milestones when explicit mentions are insufficient (< 2 per stage).

**Example for Literature Review Stage:**

```python
[
    {
        "name": "Complete Literature Survey",
        "description": "Review and synthesize existing research in the field",
        "type": "deliverable",
        "critical": False
    },
    {
        "name": "Identify Research Gaps",
        "description": "Analyze literature to identify knowledge gaps",
        "type": "deliverable",
        "critical": False
    },
    {
        "name": "Compile Bibliography",
        "description": "Create comprehensive reference list",
        "type": "deliverable",
        "critical": False
    }
]
```

**Characteristics:**
- Lower confidence (0.4-0.5)
- No source segment (generic)
- Template-based evidence

## Milestone Counts

**Per Stage:** 2-5 milestones

**Logic:**
1. Extract explicit mentions from text
2. If < 2 explicit, add generic milestones
3. Cap at 5 total per stage

**Examples:**

| Explicit Mentions | Generic Added | Total |
|-------------------|---------------|-------|
| 0                 | 2-4           | 2-4   |
| 1                 | 1-4           | 2-5   |
| 2                 | 0-3           | 2-5   |
| 3+                | 0             | 3-5   |
| 5+                | 0             | 5     |

## Generic Milestone Templates

### Coursework Stage

1. **Complete Required Courses** (critical)
   - Finish all mandatory coursework modules
2. **Pass Comprehensive Exams** (critical)
   - Successfully complete qualifying examinations
3. **Achieve Minimum Credit Requirements** (critical)
   - Accumulate required credit hours

### Literature Review Stage

1. **Complete Literature Survey**
   - Review and synthesize existing research
2. **Identify Research Gaps**
   - Analyze literature to identify opportunities
3. **Compile Bibliography**
   - Create comprehensive reference list
4. **Draft Literature Review Chapter**
   - Write initial draft of literature section

### Methodology Stage

1. **Finalize Research Design** (critical)
   - Complete and validate methodology approach
2. **Develop Data Collection Instruments**
   - Create surveys, guides, or protocols
3. **Obtain Ethics Approval** (critical)
   - Secure ethical clearances
4. **Pilot Test Methods**
   - Conduct pilot study to validate methods

### Data Collection Stage

1. **Begin Data Collection** (critical)
   - Initiate data gathering
2. **Complete Primary Data Collection** (critical)
   - Finish collecting all primary data
3. **Validate Data Quality**
   - Review and verify data completeness
4. **Organize and Store Data**
   - Structure and securely store data

### Analysis Stage

1. **Complete Data Analysis** (critical)
   - Finish statistical or qualitative analysis
2. **Interpret Findings** (critical)
   - Analyze results and draw conclusions
3. **Validate Results**
   - Verify analysis results for consistency
4. **Prepare Figures and Tables**
   - Create visual representations

### Writing Stage

1. **Complete First Draft** (critical)
   - Finish initial draft of full dissertation
2. **Revise Based on Feedback** (critical)
   - Incorporate supervisor feedback
3. **Finalize All Chapters** (critical)
   - Complete and polish all chapters
4. **Proofread and Format**
   - Final proofreading and formatting

### Submission Stage

1. **Submit Draft to Committee** (critical)
   - Provide draft to committee for review
2. **Final Submission** (critical)
   - Submit final dissertation to graduate school

### Defense Stage

1. **Schedule Defense Date** (critical)
   - Set and confirm defense date
2. **Prepare Defense Presentation** (critical)
   - Create slides and practice presentation
3. **Successfully Defend Dissertation** (critical)
   - Pass oral defense examination
4. **Address Committee Feedback** (critical)
   - Make required revisions

### Publication Stage

1. **Prepare Manuscript**
   - Convert chapters into journal format
2. **Submit to Journal**
   - Submit manuscript to peer-reviewed journal
3. **Address Reviewer Comments**
   - Revise based on peer review feedback
4. **Publish Research Findings**
   - Achieve publication in peer-reviewed venue

## Critical Milestones

Milestones are marked as critical based on:

1. **Milestone Type:**
   - Exam (always critical)
   - Defense (always critical)
   - Proposal (always critical)

2. **Keywords in Context:**
   - "required", "mandatory", "must", "critical", "essential"

3. **Generic Templates:**
   - Pre-defined in templates (e.g., "Pass Comprehensive Exams")

**Critical Milestone Examples:**
- Pass Comprehensive Exams
- Obtain Ethics Approval
- Successfully Defend Dissertation
- Final Submission

## Confidence Scores

### High Confidence (0.6-0.8)

**Source:** Explicit mentions in text

**Indicators:**
- Direct mention of milestone
- Clear keyword match
- Linked to source segment

**Example:**
```
Text: "Ethics approval must be obtained before data collection"
Milestone: "Ethics Approval" (confidence: 0.7)
```

### Medium Confidence (0.5-0.6)

**Source:** Partial mentions or implied milestones

**Example:**
```
Text: "Following review of the literature..."
Milestone: "Complete Literature Survey" (confidence: 0.55)
```

### Low Confidence (0.4-0.5)

**Source:** Generic templates

**Indicators:**
- No explicit mention
- Template-based
- No source segment

**Example:**
```
Milestone: "Identify Research Gaps" (confidence: 0.4)
Evidence: "Generic milestone for Literature Review stage"
```

## Usage Examples

### Basic Usage

```python
from app.services.timeline_intelligence_engine import TimelineIntelligenceEngine

engine = TimelineIntelligenceEngine()

text = """
Year 1: Complete coursework and pass comprehensive exam
Year 2: Conduct literature review and finalize methodology
Year 3: Collect data and analyze results
Year 4: Write dissertation and defend
"""

milestones = engine.extract_milestones(text)

for milestone in milestones:
    print(f"{milestone.name} ({milestone.stage})")
    print(f"  Type: {milestone.milestone_type}")
    print(f"  Critical: {milestone.is_critical}")
    print(f"  Confidence: {milestone.confidence:.2f}")
```

### With Section Map

```python
# Get document with section map
doc = document_service.get_document(document_id)

# Extract milestones using both text and section map
milestones = engine.extract_milestones(
    text=doc.document_text,
    section_map=doc.section_map_json
)

# Group by stage
by_stage = {}
for m in milestones:
    if m.stage not in by_stage:
        by_stage[m.stage] = []
    by_stage[m.stage].append(m)

# Display by stage
for stage, stage_milestones in by_stage.items():
    print(f"\n{stage}:")
    for milestone in stage_milestones:
        print(f"  - {milestone.name}")
```

### Filtering Milestones

```python
milestones = engine.extract_milestones(text, section_map)

# Critical milestones only
critical = [m for m in milestones if m.is_critical]

# High confidence milestones
high_confidence = [m for m in milestones if m.confidence >= 0.6]

# Explicit (non-generic) milestones
explicit = [m for m in milestones if m.source_segment is not None]

# By stage
lit_review_milestones = [
    m for m in milestones 
    if "literature review" in m.stage.lower()
]

# By type
exams = [m for m in milestones if m.milestone_type == "exam"]
deliverables = [m for m in milestones if m.milestone_type == "deliverable"]
```

### Examining Evidence

```python
milestones = engine.extract_milestones(text, section_map)

for milestone in milestones:
    print(f"\n{milestone.name}")
    print(f"Stage: {milestone.stage}")
    print(f"Evidence: {milestone.evidence_snippet}")
    
    if milestone.source_segment is not None:
        print(f"Source: Segment {milestone.source_segment} (explicit)")
    else:
        print(f"Source: Generic template")
    
    if milestone.keywords:
        print(f"Keywords: {', '.join(milestone.keywords)}")
```

### Complete Pipeline

```python
# 1. Upload document
document_id = document_service.upload_document(
    user_id=user.id,
    file_content=pdf_bytes,
    filename="proposal.pdf"
)

# 2. Get processed document
doc = document_service.get_document(document_id)

# 3. Extract milestones
engine = TimelineIntelligenceEngine()
milestones = engine.extract_milestones(
    text=doc.document_text,
    section_map=doc.section_map_json
)

# 4. Create draft timeline with milestones
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator

orchestrator = TimelineOrchestrator(db)
draft_timeline = orchestrator.create_draft_timeline(
    baseline_id=baseline.id,
    user_context={"milestones": [m.__dict__ for m in milestones]}
)
```

## Editability and Genericity

### Design Principles

1. **No Hard Dates**
   - Generic milestones have no specific dates
   - Users add dates during timeline editing

2. **No Specific Names**
   - Avoid "Dr. Smith's approval"
   - Use "Obtain supervisor approval"

3. **Flexible Descriptions**
   - "Complete data collection" (flexible)
   - Not "Collect data from 100 participants in Boston" (too specific)

4. **Template-Based**
   - Milestones serve as starting points
   - Users customize to their needs

### Good Generic Milestones

✅ "Complete Literature Survey"  
✅ "Finalize Research Design"  
✅ "Begin Data Collection"  
✅ "Successfully Defend Dissertation"  

### Bad Generic Milestones (Too Specific)

❌ "Complete Literature Survey by December 2024"  
❌ "Get approval from Dr. Johnson"  
❌ "Collect data from 50 participants in London"  
❌ "Defend on March 15th at 2pm"  

## Best Practices

### 1. Always Use Section Map

```python
# GOOD: Use section map when available
doc = document_service.get_document(doc_id)
milestones = engine.extract_milestones(doc.document_text, doc.section_map_json)

# LESS IDEAL: Without section map
milestones = engine.extract_milestones(text_only)
```

### 2. Validate Milestone Counts

```python
# Check that each stage has 2-5 milestones
by_stage = {}
for m in milestones:
    if m.stage not in by_stage:
        by_stage[m.stage] = []
    by_stage[m.stage].append(m)

for stage, stage_milestones in by_stage.items():
    count = len(stage_milestones)
    if not (2 <= count <= 5):
        print(f"Warning: {stage} has {count} milestones (expected 2-5)")
```

### 3. Prioritize High-Confidence Milestones

```python
# Sort by confidence
milestones_sorted = sorted(milestones, key=lambda m: m.confidence, reverse=True)

# Present high-confidence first
for milestone in milestones_sorted[:10]:
    print(f"{milestone.name}: {milestone.confidence:.2f}")
```

### 4. Mark Critical Milestones Prominently

```python
for milestone in milestones:
    prefix = "[CRITICAL] " if milestone.is_critical else ""
    print(f"{prefix}{milestone.name}")
```

### 5. Allow User Customization

```python
# In UI: Allow users to
# - Edit milestone names
# - Modify descriptions
# - Add/remove milestones
# - Change critical flag
# - Reorder milestones
```

## Limitations

### What This Does NOT Do

- ❌ **No date assignment** - Milestones have no dates
- ❌ **No duration estimation** - Use `estimate_durations()` separately
- ❌ **No dependency mapping** - Use `map_dependencies()` separately
- ❌ **No personalization** - Generic templates only
- ❌ **No ML-based extraction** - Pure pattern matching

### Known Edge Cases

1. **Overly Specific Text**
   - If text mentions specific dates, these are ignored
   - Milestone names are made generic

2. **Very Short Documents**
   - May only get generic milestones
   - Low confidence scores

3. **Non-Standard Terminology**
   - Custom milestone names may not be detected
   - Falls back to generic templates

4. **Overlapping Stages**
   - Milestones assigned to first matching stage
   - May need manual reassignment

## Performance

- **Speed**: ~10ms for typical proposal (5000 words, 5 stages)
- **Memory**: O(n) where n = document length + stages
- **Scalability**: Efficient up to 10 stages, 50 milestones

## Testing

```bash
# Run milestone extraction tests
pytest backend/tests/test_milestone_extraction.py -v

# Test specific scenarios
pytest backend/tests/test_milestone_extraction.py::TestMilestoneExtraction::test_milestones_per_stage -v
```

## Summary

✅ **2-5 milestones per stage** - Balanced milestone generation  
✅ **Generic and editable** - No hard commitments  
✅ **Two-method extraction** - Explicit + generic templates  
✅ **Evidence-backed** - Shows source of each milestone  
✅ **Critical flags** - Identifies mandatory milestones  
✅ **Confidence scores** - Based on extraction method  
✅ **Stage-linked** - Each milestone tied to a stage  

The `extract_milestones()` method provides a solid foundation for timeline creation, giving users editable templates that can be customized to their specific PhD journey.

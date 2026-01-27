# JourneyHealthEngine - Complete Scoring System

## Overview

The `JourneyHealthEngine` provides **transparent, repeatable, rule-based scoring** for PhD journey health assessments. It converts questionnaire responses into dimension scores (0-100), overall health bands, and structured recommendations.

## Core Capabilities

✅ **Dimension scoring** - Convert 1-5 scale to 0-100  
✅ **Status determination** - Excellent to Critical bands  
✅ **Weighted overall score** - Prioritize critical dimensions  
✅ **Structured recommendations** - Rule-based action items  
✅ **Strengths & concerns** - Identify high/low areas  
✅ **Transparent rules** - All formulas documented  
✅ **Repeatable** - Same inputs → same outputs  

## Key Principles

✅ **No ML** - Pure rule-based logic  
✅ **No free-text** - Structured templates only  
✅ **Transparent** - All formulas visible  
✅ **Deterministic** - Repeatable results  
✅ **No document access** - Questionnaire only  
✅ **No timeline access** - Responses only  

## Scoring System

### 1. Scale Conversion (1-5 → 0-100)

**Formula:**
```python
score = ((response_value - 1) / 4) * 100
```

**Conversion Table:**
| Response | Calculation | Score |
|----------|-------------|-------|
| 1        | (1-1)/4*100 | 0     |
| 2        | (2-1)/4*100 | 25    |
| 3        | (3-1)/4*100 | 50    |
| 4        | (4-1)/4*100 | 75    |
| 5        | (5-1)/4*100 | 100   |

**Example:**
```python
# Question: "How satisfied are you with research progress?"
# Response: 4 (on 1-5 scale)
# Score: ((4 - 1) / 4) * 100 = 75
```

### 2. Dimension Scoring

Each dimension is scored by averaging all its question responses.

**Formula:**
```python
dimension_score = sum(question_scores) / num_questions
```

**Example:**
```python
# Dimension: Research Progress
# Questions: q1=4, q2=3, q3=5
# Converted: 75, 50, 100
# Dimension Score: (75 + 50 + 100) / 3 = 75.0
```

### 3. Status Determination

Status is determined by score thresholds.

**Thresholds:**
```python
THRESHOLDS = {
    "excellent":    80,  # >= 80
    "good":         65,  # >= 65 and < 80
    "fair":         50,  # >= 50 and < 65
    "concerning":   35,  # >= 35 and < 50
    "critical":     0    # < 35
}
```

**Status Bands:**
| Score Range | Status       | Color  |
|-------------|--------------|--------|
| 80-100      | Excellent    | 🟢 Green |
| 65-79       | Good         | 🔵 Blue  |
| 50-64       | Fair         | 🟡 Yellow|
| 35-49       | Concerning   | 🟠 Orange|
| 0-34        | Critical     | 🔴 Red   |

**Example:**
```python
if score >= 80:
    status = "excellent"
elif score >= 65:
    status = "good"
elif score >= 50:
    status = "fair"
elif score >= 35:
    status = "concerning"
else:
    status = "critical"
```

### 4. Overall Score (Weighted Average)

Overall score is calculated using weighted average of dimensions.

**Dimension Weights:**
```python
DIMENSION_WEIGHTS = {
    "mental_wellbeing":         1.3,  # Highest priority
    "research_progress":        1.2,
    "supervisor_relationship":  1.1,
    "motivation":               1.1,
    "work_life_balance":        1.0,
    "academic_confidence":      1.0,
    "support_network":          1.0,
    "time_management":          0.9,  # Lowest priority
}
```

**Formula:**
```python
overall_score = sum(dimension_score * weight) / sum(weights)
```

**Example:**
```python
# Dimension Scores:
# Research Progress: 75 (weight 1.2)
# Mental Wellbeing: 50 (weight 1.3)

# Calculation:
# (75 * 1.2 + 50 * 1.3) / (1.2 + 1.3)
# = (90 + 65) / 2.5
# = 62.0
```

**Why Weights?**
- **Mental Wellbeing (1.3)** - Most critical for student health
- **Research Progress (1.2)** - Core PhD objective
- **Time Management (0.9)** - Important but can improve with practice

## Health Dimensions

### 1. Research Progress
**Weight:** 1.2  
**Low Score Threshold:** 40

**Questions typically include:**
- Satisfaction with research progress
- Meeting research milestones
- Clarity of research direction
- Progress towards publications

### 2. Mental Wellbeing
**Weight:** 1.3 (Highest)  
**Low Score Threshold:** 45

**Questions typically include:**
- Overall mental health rating
- Stress levels
- Anxiety/depression symptoms
- Access to mental health support

### 3. Supervisor Relationship
**Weight:** 1.1  
**Low Score Threshold:** 40

**Questions typically include:**
- Quality of supervisor feedback
- Communication frequency
- Feeling supported by supervisor
- Conflicts or concerns

### 4. Work-Life Balance
**Weight:** 1.0  
**Low Score Threshold:** 45

**Questions typically include:**
- Work hours satisfaction
- Time for personal life
- Burnout symptoms
- Ability to disconnect

### 5. Academic Confidence
**Weight:** 1.0  
**Low Score Threshold:** 40

**Questions typically include:**
- Confidence in research abilities
- Imposter syndrome symptoms
- Feeling qualified for PhD
- Comparison with peers

### 6. Time Management
**Weight:** 0.9 (Lowest)  
**Low Score Threshold:** 50

**Questions typically include:**
- Ability to meet deadlines
- Task prioritization
- Procrastination habits
- Productivity satisfaction

### 7. Motivation
**Weight:** 1.1  
**Low Score Threshold:** 40

**Questions typically include:**
- Enthusiasm for research
- Connection to research purpose
- Energy levels
- Future outlook

### 8. Support Network
**Weight:** 1.0  
**Low Score Threshold:** 45

**Questions typically include:**
- Peer support availability
- Social connections
- Family support
- Departmental community

## Strengths & Concerns

### Strengths (High Scores)

**Rule:** ≥60% of responses are 4 or 5

```python
if high_responses >= 0.6 * total_responses:
    strengths.append(f"Strong {dimension_name}")
```

**Example:**
```python
# Dimension: Academic Confidence
# Responses: 5, 4, 4, 5, 3
# High responses (≥4): 4 out of 5 = 80%
# Result: Identified as strength
```

### Concerns (Low Scores)

**Rule:** ≥40% of responses are 1 or 2

```python
if low_responses >= 0.4 * total_responses:
    concerns.append(f"Low {dimension_name}")
```

**Example:**
```python
# Dimension: Work-Life Balance
# Responses: 2, 1, 3, 2, 1
# Low responses (≤2): 4 out of 5 = 80%
# Result: Identified as concern
```

## Recommendation Generation

### Priority Assignment

**Rules:**
- **High Priority:** Critical status (score < 35)
- **Medium Priority:** Concerning status (35 ≤ score < 50)
- **Low Priority:** Fair status (50 ≤ score < 65)
- **No Recommendation:** Good/Excellent (score ≥ 65)

```python
if status == "critical":
    priority = "high"
elif status == "concerning":
    priority = "medium"
elif status == "fair":
    priority = "low"
else:
    priority = None  # No recommendation
```

### Recommendation Templates

Each dimension has a structured recommendation template:

```python
{
    "title": "Action Title",
    "description": "Why this matters",
    "actions": [
        "Specific action item 1",
        "Specific action item 2",
        "Specific action item 3"
    ]
}
```

### Example Recommendations

#### Research Progress (Critical)
```python
{
    "priority": "high",
    "title": "Improve Research Progress",
    "description": "Your research progress scores indicate room for improvement.",
    "actions": [
        "Break down research goals into smaller, achievable tasks",
        "Schedule regular check-ins with your supervisor",
        "Review and update your research timeline",
        "Identify and address any blockers or obstacles"
    ]
}
```

#### Mental Wellbeing (Critical)
```python
{
    "priority": "high",
    "title": "Prioritize Mental Well-being",
    "description": "Your mental well-being needs attention.",
    "actions": [
        "Consider speaking with a counselor or therapist",
        "Establish regular self-care routines",
        "Practice stress management techniques",
        "Connect with university mental health resources"
    ]
}
```

#### Work-Life Balance (Concerning)
```python
{
    "priority": "medium",
    "title": "Improve Work-Life Balance",
    "description": "Your work-life balance could be better managed.",
    "actions": [
        "Set clear boundaries for work hours",
        "Schedule regular breaks and time off",
        "Engage in hobbies and social activities",
        "Practice saying no to non-essential commitments"
    ]
}
```

## Complete Example

### Input: Questionnaire Responses

```python
from app.services.journey_health_engine import (
    JourneyHealthEngine,
    QuestionResponse,
    HealthDimension
)

responses = [
    # Research Progress (3 questions)
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_1", 4),  # 75
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_2", 3),  # 50
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_3", 5),  # 100
    # Average: 75.0 → Status: Good
    
    # Mental Wellbeing (2 questions)
    QuestionResponse(HealthDimension.MENTAL_WELLBEING, "wb_1", 2),   # 25
    QuestionResponse(HealthDimension.MENTAL_WELLBEING, "wb_2", 1),   # 0
    # Average: 12.5 → Status: Critical
    
    # Work-Life Balance (2 questions)
    QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "wlb_1", 3), # 50
    QuestionResponse(HealthDimension.WORK_LIFE_BALANCE, "wlb_2", 3), # 50
    # Average: 50.0 → Status: Fair
]
```

### Output: Health Report

```python
engine = JourneyHealthEngine()
report = engine.assess_health(responses, assessment_date="2024-01-15")

print(report.overall_score)  # ~42.5 (weighted average)
print(report.overall_status)  # HealthStatus.CONCERNING
print(len(report.dimension_scores))  # 3 dimensions
print(len(report.recommendations))  # 3 recommendations

# Dimension Scores
for dimension, score in report.dimension_scores.items():
    print(f"{dimension.value}: {score.score} ({score.status.value})")

# Output:
# research_progress: 75.0 (good)
# mental_wellbeing: 12.5 (critical)
# work_life_balance: 50.0 (fair)

# Recommendations (sorted by priority)
for rec in report.recommendations:
    print(f"[{rec.priority.upper()}] {rec.title}")

# Output:
# [HIGH] Prioritize Mental Well-being
# [LOW] Improve Work-Life Balance
```

### Calculation Breakdown

**Dimension Scores:**
```
Research Progress: (75 + 50 + 100) / 3 = 75.0
Mental Wellbeing: (25 + 0) / 2 = 12.5
Work-Life Balance: (50 + 50) / 2 = 50.0
```

**Overall Score (Weighted):**
```
Weights:
- Research Progress: 1.2
- Mental Wellbeing: 1.3
- Work-Life Balance: 1.0

Calculation:
(75.0 * 1.2 + 12.5 * 1.3 + 50.0 * 1.0) / (1.2 + 1.3 + 1.0)
= (90 + 16.25 + 50) / 3.5
= 156.25 / 3.5
= 44.6
```

**Status:**
```
44.6 is >= 35 and < 50 → CONCERNING
```

**Recommendations:**
```
Mental Wellbeing (12.5, critical) → HIGH priority
Work-Life Balance (50.0, fair) → LOW priority
Research Progress (75.0, good) → None
```

## API Usage

### Basic Assessment

```python
from app.services.journey_health_engine import (
    JourneyHealthEngine,
    QuestionResponse,
    HealthDimension
)

engine = JourneyHealthEngine()

responses = [
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "q1", 4),
    QuestionResponse(HealthDimension.MENTAL_WELLBEING, "q2", 2),
    # ... more responses
]

report = engine.assess_health(responses)

# Access results
print(f"Overall Score: {report.overall_score}")
print(f"Status: {report.overall_status.value}")

for dimension, score in report.dimension_scores.items():
    print(f"{dimension.value}: {score.score} ({score.status.value})")

for recommendation in report.recommendations:
    print(f"\n[{recommendation.priority.upper()}] {recommendation.title}")
    print(f"{recommendation.description}")
    for action in recommendation.action_items:
        print(f"  - {action}")
```

### Get Critical Dimensions

```python
report = engine.assess_health(responses)

# Get dimensions needing attention
critical_dims = report.get_critical_dimensions()

for dim_score in critical_dims:
    print(f"⚠️ {dim_score.dimension.value}: {dim_score.score}")
    print(f"   Status: {dim_score.status.value}")
    if dim_score.concerns:
        print(f"   Concerns: {', '.join(dim_score.concerns)}")
```

### Get Healthy Dimensions

```python
report = engine.assess_health(responses)

# Get dimensions doing well
healthy_dims = report.get_healthy_dimensions()

for dim_score in healthy_dims:
    print(f"✅ {dim_score.dimension.value}: {dim_score.score}")
    if dim_score.strengths:
        print(f"   Strengths: {', '.join(dim_score.strengths)}")
```

## Testing

Run comprehensive tests:
```bash
cd backend
pytest tests/test_journey_health_engine.py -v
```

**Test Coverage:**
- ✅ Scale conversion (1-5 → 0-100)
- ✅ Dimension scoring
- ✅ Status determination
- ✅ Overall score calculation
- ✅ Weighted averages
- ✅ Recommendation generation
- ✅ Priority assignment
- ✅ Strengths & concerns
- ✅ Edge cases
- ✅ Deterministic behavior

## Validation Rules

### Input Validation

```python
# Must have at least one response
if not responses:
    raise ValueError("No questionnaire responses provided")

# Response values must be 1-5
assert 1 <= response.response_value <= 5
```

### Output Guarantees

```python
# Dimension scores are 0-100
assert 0 <= dimension_score.score <= 100

# Overall score is 0-100
assert 0 <= report.overall_score <= 100

# Status matches score
if score >= 80:
    assert status == HealthStatus.EXCELLENT

# Recommendations are sorted by priority
priorities = [r.priority for r in report.recommendations]
assert priorities == sorted(priorities, key=priority_order)
```

## Transparency & Repeatability

### Same Inputs → Same Outputs

```python
engine1 = JourneyHealthEngine()
engine2 = JourneyHealthEngine()

responses = [...]  # Same responses

report1 = engine1.assess_health(responses)
report2 = engine2.assess_health(responses)

assert report1.overall_score == report2.overall_score
assert report1.overall_status == report2.overall_status
```

### All Formulas Documented

```python
# Scale conversion
score = ((value - 1) / 4) * 100

# Dimension average
dimension_score = sum(scores) / count

# Weighted overall
overall = sum(score * weight) / sum(weights)

# Status determination
if score >= 80: status = "excellent"
# ... (see thresholds section)
```

### Thresholds Accessible

```python
engine = JourneyHealthEngine()

print(engine.THRESHOLDS)
# {
#     HealthStatus.EXCELLENT: 80,
#     HealthStatus.GOOD: 65,
#     HealthStatus.FAIR: 50,
#     HealthStatus.CONCERNING: 35,
#     HealthStatus.CRITICAL: 0
# }

print(engine.DIMENSION_RULES[HealthDimension.MENTAL_WELLBEING])
# {
#     "weight": 1.3,
#     "low_score_threshold": 45
# }
```

## Integration

### With PhD Doctor Orchestrator

```python
from app.orchestrators.phd_doctor_orchestrator import PhDDoctorOrchestrator

orchestrator = PhDDoctorOrchestrator(db)

# Orchestrator internally uses JourneyHealthEngine
result = orchestrator.submit_questionnaire(
    user_id=user.id,
    responses=[...]  # Questionnaire responses
)

# Result includes health report
print(result['overall_status'])
print(result['dimension_scores'])
print(result['recommendations'])
```

### With Questionnaire Draft Service

```python
from app.services.questionnaire_draft_service import QuestionnaireDraftService

# User completes draft
draft_service = QuestionnaireDraftService(db)
draft = draft_service.get_draft(draft_id, user.id)

# Convert draft responses to QuestionResponse objects
responses = []
for section_id, section_responses in draft['responses'].items():
    for question_id, value in section_responses.items():
        dimension = get_dimension_for_question(question_id)
        responses.append(
            QuestionResponse(dimension, question_id, value)
        )

# Score with engine
engine = JourneyHealthEngine()
report = engine.assess_health(responses)
```

## Summary

The `JourneyHealthEngine` provides **transparent, repeatable, rule-based scoring** for PhD journey health with:

- ✅ Clear scale conversion (1-5 → 0-100)
- ✅ Documented thresholds (5 status bands)
- ✅ Weighted dimension scoring (8 dimensions)
- ✅ Structured recommendations (no free-text)
- ✅ Deterministic behavior (same in → same out)
- ✅ Full test coverage (50+ tests)
- ✅ Complete documentation

**No ML. No free-text. Pure rules.** 📊

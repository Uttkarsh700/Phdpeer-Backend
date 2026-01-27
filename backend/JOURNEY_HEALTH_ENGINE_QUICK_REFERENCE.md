# JourneyHealthEngine - Quick Reference

## Scale Conversion

### Formula
```python
score = ((response_value - 1) / 4) * 100
```

### Table
| Response | Score |
|----------|-------|
| 1        | 0     |
| 2        | 25    |
| 3        | 50    |
| 4        | 75    |
| 5        | 100   |

## Status Thresholds

| Score    | Status      |
|----------|-------------|
| 80-100   | Excellent   |
| 65-79    | Good        |
| 50-64    | Fair        |
| 35-49    | Concerning  |
| 0-34     | Critical    |

## Dimension Weights

| Dimension                  | Weight |
|----------------------------|--------|
| Mental Wellbeing           | 1.3    |
| Research Progress          | 1.2    |
| Supervisor Relationship    | 1.1    |
| Motivation                 | 1.1    |
| Work-Life Balance          | 1.0    |
| Academic Confidence        | 1.0    |
| Support Network            | 1.0    |
| Time Management            | 0.9    |

## Overall Score Formula

```python
overall_score = sum(dimension_score * weight) / sum(weights)
```

## Recommendation Priority

| Status      | Priority | Generated? |
|-------------|----------|------------|
| Critical    | High     | Yes        |
| Concerning  | Medium   | Yes        |
| Fair        | Low      | Yes        |
| Good        | None     | No         |
| Excellent   | None     | No         |

## Strengths & Concerns

### Strengths
```python
≥60% of responses are 4 or 5
```

### Concerns
```python
≥40% of responses are 1 or 2
```

## Usage

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
]

report = engine.assess_health(responses)

print(f"Overall: {report.overall_score} ({report.overall_status.value})")
```

### Get Critical Dimensions
```python
critical_dims = report.get_critical_dimensions()
for dim in critical_dims:
    print(f"⚠️ {dim.dimension.value}: {dim.score}")
```

### Get Recommendations
```python
for rec in report.recommendations:
    print(f"[{rec.priority.upper()}] {rec.title}")
    for action in rec.action_items:
        print(f"  - {action}")
```

## Example Calculation

### Input
```python
# Research Progress: 4, 3, 5
# Mental Wellbeing: 2, 1

responses = [
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_1", 4),  # 75
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_2", 3),  # 50
    QuestionResponse(HealthDimension.RESEARCH_PROGRESS, "rp_3", 5),  # 100
    QuestionResponse(HealthDimension.MENTAL_WELLBEING, "wb_1", 2),   # 25
    QuestionResponse(HealthDimension.MENTAL_WELLBEING, "wb_2", 1),   # 0
]
```

### Calculation
```
Research Progress: (75 + 50 + 100) / 3 = 75.0 → GOOD
Mental Wellbeing: (25 + 0) / 2 = 12.5 → CRITICAL

Overall (weighted):
(75.0 * 1.2 + 12.5 * 1.3) / (1.2 + 1.3)
= (90 + 16.25) / 2.5
= 42.5 → CONCERNING
```

### Output
```
Overall Score: 42.5
Overall Status: concerning

Dimension Scores:
- research_progress: 75.0 (good)
- mental_wellbeing: 12.5 (critical)

Recommendations:
[HIGH] Prioritize Mental Well-being
  - Consider speaking with a counselor or therapist
  - Establish regular self-care routines
  - Practice stress management techniques
  - Connect with university mental health resources
```

## Key Principles

✅ Transparent formulas  
✅ Repeatable results  
✅ No ML  
✅ No free-text  
✅ Rule-based only  

## Files

- `backend/app/services/journey_health_engine.py` - Implementation
- `backend/tests/test_journey_health_engine.py` - Tests
- `backend/JOURNEY_HEALTH_ENGINE_COMPLETE.md` - Full documentation

---

**Status:** ✅ Production Ready

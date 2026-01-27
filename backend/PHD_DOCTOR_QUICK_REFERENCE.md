# PhD Doctor Orchestrator - Quick Reference

## Basic Usage

```python
from app.orchestrators.phd_doctor_orchestrator import PhDDoctorOrchestrator

orchestrator = PhDDoctorOrchestrator(db, user_id)

result = orchestrator.submit(
    request_id="unique_request_id",
    user_id=user_id,
    responses=[
        {"dimension": "RESEARCH_PROGRESS", "question_id": "q1", "response_value": 4},
        {"dimension": "MENTAL_WELLBEING", "question_id": "q2", "response_value": 3},
        # ... minimum 5 responses
    ],
    draft_id=optional_draft_id,
    assessment_type="self_assessment",
    notes="Optional notes"
)
```

## Response Format

### Input

```python
{
    "dimension": str,          # Required: Valid HealthDimension enum
    "question_id": str,        # Required: Unique identifier
    "response_value": int,     # Required: 1-5
    "question_text": str       # Optional
}
```

**Valid Dimensions**: `RESEARCH_PROGRESS`, `MENTAL_WELLBEING`, `WORK_LIFE_BALANCE`, `TIME_MANAGEMENT`, `SUPERVISOR_RELATIONSHIP`, `PEER_SUPPORT`, `MOTIVATION`, `WRITING_PROGRESS`

**Response Values**: 1 (Strongly Disagree) → 5 (Strongly Agree)

### Output

```python
{
    "assessment_id": str,
    "overall_score": float,         # 0-100
    "overall_status": str,          # "excellent", "good", "fair", "concerning", "critical"
    "dimensions": {...},            # Dimension scores
    "critical_areas": [...],        # Low-scoring dimensions
    "healthy_areas": [...],         # High-scoring dimensions
    "recommendations": [...],       # Actionable recommendations
    "summary": str                  # Human-readable summary
}
```

## Validation Rules

| Rule | Requirement |
|------|-------------|
| **User** | Must exist and be active |
| **Response Count** | Minimum 5 responses |
| **Response Fields** | `dimension`, `question_id`, `response_value` required |
| **Response Values** | Integer 1-5 only |
| **Draft** | Must exist, belong to user, not already submitted |

## Error Handling

```python
from app.orchestrators.phd_doctor_orchestrator import (
    PhDDoctorOrchestratorError,
    IncompleteSubmissionError
)

try:
    result = orchestrator.submit(...)
except IncompleteSubmissionError as e:
    # Validation failed - show to user
    print(f"Incomplete: {e}")
except PhDDoctorOrchestratorError as e:
    # Other error - log and retry
    print(f"Error: {e}")
```

## Common Methods

### Submit Assessment

```python
result = orchestrator.submit(
    request_id="req_123",
    user_id=user_id,
    responses=responses,
    draft_id=draft_id,      # Optional
    assessment_type="self", # Optional
    notes="Notes"           # Optional
)
```

### Get Assessment

```python
assessment = orchestrator.get_assessment(assessment_id)
```

### Get Latest Assessment

```python
latest = orchestrator.get_latest_assessment(user_id)
```

### Get User Assessments

```python
assessments = orchestrator.get_user_assessments(
    user_id=user_id,
    assessment_type="self_assessment",  # Optional filter
    limit=10
)
```

### Compare Assessments

```python
comparison = orchestrator.compare_assessments(
    assessment_id_1=old_id,
    assessment_id_2=new_id
)

# Returns: change, improvement, percentage_change
```

## Pipeline Steps

1. **validate_submission** - User exists, responses complete
2. **convert_responses** - Convert to QuestionResponse objects
3. **compute_scores** - JourneyHealthEngine scoring
4. **store_assessment** - Save to database
5. **mark_draft_submitted** - Mark draft (if provided)
6. **generate_summary** - Format output

## Score Calculation

### Overall Score

```
overall_score = weighted_average(dimension_scores)

Weights:
- Research Progress: 25%
- Mental Wellbeing: 20%
- Time Management: 15%
- Work-Life Balance: 15%
- Supervisor Relationship: 10%
- Motivation: 10%
- Writing Progress: 5%
```

### Dimension Score

```
dimension_score = (average_response_value - 1) * 25

Examples:
- Average 5.0 → Score 100
- Average 3.0 → Score 50
- Average 1.0 → Score 0
```

### Health Status

| Score | Status |
|-------|--------|
| 85-100 | excellent |
| 70-84 | good |
| 50-69 | fair |
| 30-49 | concerning |
| 0-29 | critical |

## Recommendation Priorities

| Priority | Criteria |
|----------|----------|
| **High** | Score < 30, Mental wellbeing concerns, Supervisor issues |
| **Medium** | Score 30-50, Work-life balance, Time management |
| **Low** | Score 50-70, General improvements |

## Idempotency

```python
# Same request_id returns cached result
result1 = orchestrator.submit(request_id="req_123", ...)
result2 = orchestrator.submit(request_id="req_123", ...)

assert result1["assessment_id"] == result2["assessment_id"]

# Only 1 assessment created
```

## Decision Tracing

### Access Trace

```python
from app.models.idempotency import DecisionTrace

trace = db.query(DecisionTrace).filter(
    DecisionTrace.event_id == request_id
).first()

# Trace includes:
# - All pipeline steps
# - Execution times
# - Step details
```

### Access Evidence

```python
from app.models.idempotency import EvidenceBundle

evidence = db.query(EvidenceBundle).filter(
    EvidenceBundle.event_id == request_id
).first()

# Evidence includes:
# - Validation results
# - Converted responses
# - Computed scores
# - Stored assessment
```

## Integration Example

### API Endpoint

```python
@router.post("/api/assessments/submit")
def submit_assessment(request: SubmitRequest, db: Session = Depends(get_db)):
    orchestrator = PhDDoctorOrchestrator(db, request.user_id)
    
    try:
        return orchestrator.submit(
            request_id=request.request_id,
            user_id=request.user_id,
            responses=request.responses,
            draft_id=request.draft_id
        )
    except IncompleteSubmissionError as e:
        raise HTTPException(400, detail=str(e))
```

### Frontend

```typescript
const submitAssessment = async (responses: Response[]) => {
  const result = await api.post('/api/assessments/submit', {
    request_id: `submit_${Date.now()}`,
    responses
  });
  
  return result.data;
};
```

## Testing

```bash
# Run all tests
pytest tests/test_phd_doctor_orchestrator.py -v

# Run specific test class
pytest tests/test_phd_doctor_orchestrator.py::TestSubmissionValidation -v

# Run with coverage
pytest tests/test_phd_doctor_orchestrator.py --cov=app.orchestrators.phd_doctor_orchestrator
```

## Common Patterns

### Submit with Draft

```python
# Create draft
draft_id = create_draft(user_id)

# Save responses
save_section(draft_id, "section1", responses1)
save_section(draft_id, "section2", responses2)

# Submit and mark draft
result = orchestrator.submit(
    request_id=f"draft_submit_{draft_id}",
    user_id=user_id,
    responses=all_responses,
    draft_id=draft_id  # Marks draft as submitted
)

# Draft is now immutable
```

### Periodic Assessments

```python
from datetime import datetime

# Monthly assessment
request_id = f"monthly_{user_id}_{datetime.now().strftime('%Y%m')}"

result = orchestrator.submit(
    request_id=request_id,
    user_id=user_id,
    responses=responses,
    assessment_type="monthly_check_in"
)
```

### Progress Tracking

```python
# Get all assessments
assessments = orchestrator.get_user_assessments(user_id, limit=100)

# Track score over time
scores = [a["overall_progress_rating"] for a in assessments]
dates = [a["assessment_date"] for a in assessments]

# Plot progress
plt.plot(dates, scores)
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "User not found" | Invalid user_id | Verify user exists |
| "Insufficient responses" | < 5 responses | Add more responses |
| "invalid value 6" | Value out of range | Ensure 1-5 only |
| "Draft already submitted" | Reusing submitted draft | Create new draft |
| "missing 'dimension' field" | Incomplete response | Add required fields |

## Performance

- **Validation**: < 10ms
- **Scoring**: < 50ms
- **Database**: < 100ms
- **Total**: < 200ms
- **Queries**: 3-4 per submission

## Key Features

✅ Validation - Comprehensive completeness checks  
✅ Scoring - Rule-based health assessment  
✅ Storage - Immutable snapshots  
✅ Recommendations - Actionable guidance  
✅ Tracing - Full audit trail  
✅ Idempotency - Duplicate protection  
✅ Draft Integration - Automatic marking  

## Status

**Implementation**: ✅ Complete  
**Tests**: ✅ Passing (30+ tests)  
**Documentation**: ✅ Comprehensive  
**Production Ready**: ✅ Yes

---

For full documentation, see `PHD_DOCTOR_COMPLETE.md`

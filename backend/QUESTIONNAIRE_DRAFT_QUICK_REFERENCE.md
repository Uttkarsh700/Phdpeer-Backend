# Questionnaire Draft System - Quick Reference

## Core Methods

### Create Draft
```python
draft_id = service.create_draft(
    user_id=user.id,
    draft_name="My Assessment",  # Optional
    metadata={"device": "mobile"}  # Optional
)
```

### Save Section
```python
result = service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="research_progress",
    responses={"q1": 4, "q2": 3},
    is_section_complete=True  # Mark section as done
)
```

### Get Draft
```python
draft = service.get_draft(draft_id, user.id)
# Returns: dict with responses, progress, etc.
```

### Get User Drafts
```python
drafts = service.get_user_drafts(
    user_id=user.id,
    include_submitted=False,  # Exclude submitted
    limit=10
)
```

### Delete Draft
```python
success = service.delete_draft(draft_id, user.id)
# Returns: True if deleted, False if not found
```

### Mark as Submitted
```python
result = service.mark_as_submitted(
    draft_id=draft_id,
    user_id=user.id,
    submission_id=assessment_id
)
```

## Version Management

### Create Version
```python
version_id = service.create_version(
    version_number="1.0",
    title="PhD Assessment v1.0",
    schema=questionnaire_schema,
    is_active=True
)
```

### Get Active Version
```python
version = service.get_active_version()
```

### Get All Versions
```python
versions = service.get_all_versions(
    include_deprecated=False
)
```

### Deprecate Version
```python
service.deprecate_version(version_id)
```

## Response Structure

### Draft Dictionary
```json
{
  "id": "uuid",
  "draft_name": "My Assessment",
  "responses": {
    "section_1": {"q1": 4, "q2": 3},
    "section_2": {"q3": 5}
  },
  "completed_sections": ["section_1"],
  "progress_percentage": 60,
  "is_submitted": false,
  "last_section_edited": "section_2",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:45:00"
}
```

## Schema Format

```python
schema = {
    "sections": [
        {
            "id": "research_progress",
            "title": "Research Progress",
            "questions": [
                {
                    "id": "rp_1",
                    "text": "Question text",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5
                }
            ]
        }
    ]
}
```

## Progress Calculation

```
progress = (answered_questions / total_questions) * 100
```

**Rules:**
- Empty responses not counted
- Updates automatically on save
- Stored in database

## Immutability Rules

### Before Submission
✅ Can edit freely  
✅ Can delete draft  
✅ Can save multiple times  

### After Submission
❌ Cannot edit  
❌ Cannot delete  
❌ Cannot resubmit  

## Common Workflows

### Create and Save
```python
draft_id = service.create_draft(user.id)
service.save_section(draft_id, user.id, "section_1", {...})
```

### Resume Draft
```python
draft = service.get_draft(draft_id, user.id)
last_section = draft['last_section_edited']
previous_responses = draft['responses'].get(last_section, {})
```

### Submit Draft
```python
# After orchestrator.submit_questionnaire()
service.mark_as_submitted(draft_id, user.id, assessment_id)
```

### Incremental Saving
```python
# Save question by question
service.save_section(draft_id, user.id, "sec1", {"q1": 4})
service.save_section(draft_id, user.id, "sec1", {"q2": 3})
service.save_section(draft_id, user.id, "sec1", {"q3": 5}, is_section_complete=True)
```

## Error Handling

```python
from app.services.questionnaire_draft_service import QuestionnaireDraftError

try:
    service.save_section(draft_id, user_id, section_id, responses)
except QuestionnaireDraftError as e:
    if "not found or not owned" in str(e):
        # Handle access error
    elif "Cannot edit submitted draft" in str(e):
        # Handle immutability error
```

## Key Principles

✅ No premature scoring  
✅ Section-by-section saving  
✅ Resumable anytime  
✅ Versioned schemas  
✅ Immutable after submission  

## Files

- `backend/app/models/questionnaire_draft.py` - Models
- `backend/app/services/questionnaire_draft_service.py` - Service
- `backend/tests/test_questionnaire_draft_service.py` - Tests
- `backend/QUESTIONNAIRE_DRAFT_COMPLETE.md` - Full documentation

---

**Status:** ✅ Production Ready

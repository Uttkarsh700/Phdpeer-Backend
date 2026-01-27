# Timeline Commit - Quick Reference

## Core Methods

### apply_edits()
Accept and track user edits to draft timeline.

```python
orchestrator.apply_edits(
    draft_timeline_id=draft_id,
    user_id=user_id,
    edits=[
        {
            "operation": "update" | "add" | "delete",
            "entity_type": "timeline" | "stage" | "milestone",
            "entity_id": "uuid",  # For update/delete
            "data": {...}         # New/updated values
        }
    ]
)
```

### commit()
Commit draft to immutable committed timeline.

```python
orchestrator.commit(
    request_id="uuid",           # Idempotency key
    draft_timeline_id=draft_id,
    user_id=user_id,
    title="Optional Override",
    description="Optional Override"
)
```

## Edit Operations

### Update Timeline
```python
{"operation": "update", "entity_type": "timeline", "data": {"title": "New Title"}}
```

### Update Stage
```python
{"operation": "update", "entity_type": "stage", "entity_id": "uuid", "data": {"duration_months": 9}}
```

### Add Stage
```python
{"operation": "add", "entity_type": "stage", "data": {"title": "New Stage", "duration_months": 6}}
```

### Delete Stage
```python
{"operation": "delete", "entity_type": "stage", "entity_id": "uuid"}
```

### Update Milestone
```python
{"operation": "update", "entity_type": "milestone", "entity_id": "uuid", "data": {"is_critical": true}}
```

### Add Milestone
```python
{"operation": "add", "entity_type": "milestone", "data": {"timeline_stage_id": "uuid", "title": "New Milestone"}}
```

### Delete Milestone
```python
{"operation": "delete", "entity_type": "milestone", "entity_id": "uuid"}
```

## Response Structure

```json
{
  "committed_timeline": {
    "id": "uuid",
    "status": "COMMITTED",
    "is_immutable": true
  },
  "draft_timeline": {
    "frozen": true,
    "is_active": false
  },
  "stages": [...],
  "edit_history": {
    "total_edits": 5,
    "edit_types": {"added": 2, "modified": 2, "deleted": 1}
  },
  "metadata": {
    "total_stages": 5,
    "total_milestones": 15
  }
}
```

## Errors

- `TimelineOrchestratorError` - Validation error
- `TimelineAlreadyCommittedError` - Already committed
- `TimelineImmutableError` - Cannot edit frozen draft
- `DuplicateRequestError` - Concurrent request

## Workflow

```
1. Generate Draft → DraftTimeline (is_active=True)
2. User Edits → TimelineEditHistory records
3. Commit → CommittedTimeline + freeze draft (is_active=False)
4. Cannot Edit → TimelineImmutableError
5. Cannot Re-commit → TimelineAlreadyCommittedError
```

## Key Rules

✅ Draft must exist and belong to user  
✅ Draft must have at least one stage  
✅ Draft must be active to edit  
✅ Commit freezes draft (`is_active = False`)  
✅ Cannot edit frozen draft  
✅ Cannot commit twice (different `request_id`)  
✅ Same `request_id` returns cached response  
✅ Version increments on commit  
✅ All edits tracked in `timeline_edit_history`  

## Quick Example

```python
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator
from uuid import uuid4

orchestrator = TimelineOrchestrator(db, user_id=user.id)

# Apply edits
edits = [
    {"operation": "update", "entity_type": "timeline", "data": {"title": "Final"}},
    {"operation": "update", "entity_type": "stage", "entity_id": str(stage_id), "data": {"duration_months": 9}}
]
orchestrator.apply_edits(draft_id, user.id, edits)

# Commit
response = orchestrator.commit(str(uuid4()), draft_id, user.id)
print(f"Committed: {response['committed_timeline']['id']}")
print(f"Frozen: {response['draft_timeline']['frozen']}")
print(f"Edits: {response['edit_history']['total_edits']}")
```

## Database Tables

### timeline_edit_history
- `draft_timeline_id` - Which draft
- `user_id` - Who edited
- `edit_type` - added, modified, deleted
- `entity_type` - timeline, stage, milestone
- `entity_id` - Which entity
- `changes_json` - Before/after values
- `description` - Human-readable

### idempotency_keys
- `key` - Request ID
- `response_data` - Cached response
- `status` - PENDING, COMPLETED, FAILED

### decision_traces
- `event_id` - Trace ID
- `trace_json` - Step-by-step execution

### evidence_bundles
- `event_id` - Bundle ID
- `evidence_json` - Context snapshots

## Testing

```bash
pytest tests/test_timeline_commit.py -v
```

**Coverage:**
- Draft validation
- Edit operations
- Commit success
- Immutability
- Idempotency
- Complete workflows

## Files

- `backend/app/models/timeline_edit_history.py` - Model
- `backend/app/orchestrators/timeline_orchestrator.py` - Logic
- `backend/tests/test_timeline_commit.py` - Tests
- `backend/TIMELINE_COMMIT_COMPLETE.md` - Full docs
- `backend/TIMELINE_COMMIT_IMPLEMENTATION_SUMMARY.md` - Summary

---

**Status:** ✅ Production Ready  
**Next:** Create API endpoints and frontend integration

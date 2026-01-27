# Timeline Commit - Complete Implementation

## Overview

The enhanced `TimelineOrchestrator.commit()` method provides production-ready timeline commitment with full idempotency, edit tracking, and immutability enforcement.

## Features Implemented

✅ **DraftTimeline validation** - Ensures draft exists and belongs to user  
✅ **User edits accepted** - Via `apply_edits()` method with full tracking  
✅ **CommittedTimeline creation** - Immutable frozen copy  
✅ **Content freeze** - Draft marked inactive after commit  
✅ **Version increment** - Automatic semantic versioning  
✅ **Re-commit prevention** - Idempotency prevents duplicates  
✅ **Edit history storage** - Separate `TimelineEditHistory` table  
✅ **Decision tracing** - Full audit trail via BaseOrchestrator  
✅ **UI-ready JSON** - Structured response for frontend  

## New Database Model

### TimelineEditHistory

```python
class TimelineEditHistory(Base, BaseModel):
    """Tracks all edits made to a draft timeline."""
    
    draft_timeline_id: UUID          # Which draft was edited
    user_id: UUID                    # Who made the edit
    edit_type: str                   # added, modified, deleted, reordered
    entity_type: str                 # timeline, stage, milestone
    entity_id: UUID                  # Which entity was edited
    changes_json: JSONB              # {"field": {"before": X, "after": Y}}
    description: str                 # Human-readable description
```

## Method Signatures

### 1. apply_edits() - Accept User Edits

```python
def apply_edits(
    self,
    draft_timeline_id: UUID,
    user_id: UUID,
    edits: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Apply user edits to a draft timeline.
    
    Args:
        draft_timeline_id: ID of draft timeline
        user_id: ID of user making edits
        edits: List of edit operations:
            {
                "operation": "update" | "add" | "delete",
                "entity_type": "timeline" | "stage" | "milestone",
                "entity_id": "uuid" (for update/delete),
                "data": {...} (new/updated values)
            }
    
    Returns:
        Summary of applied edits with edit history IDs
    """
```

### 2. commit() - Commit to Immutable Timeline

```python
def commit(
    self,
    request_id: str,              # Idempotency key
    draft_timeline_id: UUID,
    user_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:              # UI-ready JSON
    """
    Commit draft timeline to create immutable committed timeline.
    
    Features:
    - Idempotency (duplicate commits return cached response)
    - Decision tracing (full audit trail)
    - Edit history preservation
    - Version increment
    - Immutability enforcement
    """
```

## Usage Examples

### Example 1: Apply Edits Before Commit

```python
from app.orchestrators.timeline_orchestrator import TimelineOrchestrator
from uuid import uuid4

orchestrator = TimelineOrchestrator(db, user_id=user.id)

# Apply user edits
edits = [
    {
        "operation": "update",
        "entity_type": "timeline",
        "data": {
            "title": "Updated PhD Timeline",
            "description": "Revised 4-year plan"
        }
    },
    {
        "operation": "update",
        "entity_type": "stage",
        "entity_id": str(stage.id),
        "data": {
            "duration_months": 9  # Changed from 6 to 9
        }
    },
    {
        "operation": "add",
        "entity_type": "milestone",
        "data": {
            "timeline_stage_id": str(stage.id),
            "title": "Submit Ethics Amendment",
            "description": "Update IRB approval",
            "is_critical": True
        }
    }
]

edit_result = orchestrator.apply_edits(
    draft_timeline_id=draft_timeline.id,
    user_id=user.id,
    edits=edits
)

print(f"Applied {edit_result['edits_applied']} edits")
```

### Example 2: Commit with Idempotency

```python
# Commit timeline
request_id = str(uuid4())  # Or deterministic key
response = orchestrator.commit(
    request_id=request_id,
    draft_timeline_id=draft_timeline.id,
    user_id=user.id,
    title="Final PhD Timeline"
)

print(f"Committed Timeline ID: {response['committed_timeline']['id']}")
print(f"Version: {draft_timeline.version_number} → Committed")
print(f"Status: {response['committed_timeline']['status']}")
print(f"Immutable: {response['committed_timeline']['is_immutable']}")
print(f"Total Edits: {response['edit_history']['total_edits']}")

# Duplicate commit attempt (same request_id)
response2 = orchestrator.commit(
    request_id=request_id,  # Same ID
    draft_timeline_id=draft_timeline.id,
    user_id=user.id
)

assert response == response2  # Returns cached response
```

### Example 3: Complete Edit → Commit Flow

```python
# 1. Generate initial draft
generate_response = orchestrator.generate(
    request_id=str(uuid4()),
    baseline_id=baseline.id,
    user_id=user.id
)

draft_id = generate_response['timeline']['id']

# 2. User reviews and makes edits
edits = [
    {
        "operation": "update",
        "entity_type": "stage",
        "entity_id": stage_id_1,
        "data": {"duration_months": 8}
    },
    {
        "operation": "delete",
        "entity_type": "milestone",
        "entity_id": milestone_id_to_remove
    },
    {
        "operation": "add",
        "entity_type": "milestone",
        "data": {
            "timeline_stage_id": stage_id_2,
            "title": "New Deliverable"
        }
    }
]

edit_result = orchestrator.apply_edits(draft_id, user.id, edits)

# 3. Commit final version
commit_response = orchestrator.commit(
    request_id=str(uuid4()),
    draft_timeline_id=draft_id,
    user_id=user.id
)

# 4. Draft is now frozen
draft = orchestrator.get_draft_timeline(draft_id)
assert draft.is_active == False  # Frozen

# 5. Try to edit frozen draft (fails)
try:
    orchestrator.apply_edits(draft_id, user.id, [{...}])
except TimelineImmutableError:
    print("Cannot edit committed timeline")
```

## Response Structure

### commit() Response

```json
{
  "committed_timeline": {
    "id": "uuid",
    "draft_timeline_id": "uuid",
    "baseline_id": "uuid",
    "user_id": "uuid",
    "title": "Final PhD Timeline",
    "description": "Committed 4-year research plan",
    "committed_date": "2024-01-15",
    "status": "COMMITTED",
    "is_immutable": true,
    "created_at": "2024-01-15T10:30:00"
  },
  "draft_timeline": {
    "id": "uuid",
    "title": "Final PhD Timeline",
    "version_number": "2.0",
    "is_active": false,
    "frozen": true
  },
  "stages": [
    {
      "id": "uuid",
      "title": "Literature Review",
      "duration_months": 9,
      "milestones": [...]
    }
  ],
  "edit_history": {
    "total_edits": 5,
    "edit_types": {
      "added": 2,
      "modified": 2,
      "deleted": 1
    },
    "edits": [
      {
        "id": "uuid",
        "edit_type": "modified",
        "entity_type": "stage",
        "description": "Stage 'Literature Review' updated",
        "created_at": "2024-01-15T10:25:00"
      }
    ]
  },
  "metadata": {
    "total_stages": 5,
    "total_milestones": 15,
    "total_edits_applied": 5,
    "committed_at": "2024-01-15T10:30:00"
  }
}
```

## Edit Operations

### Update Timeline

```python
{
    "operation": "update",
    "entity_type": "timeline",
    "data": {
        "title": "New Title",
        "description": "New Description"
    }
}
```

### Update Stage

```python
{
    "operation": "update",
    "entity_type": "stage",
    "entity_id": "stage-uuid",
    "data": {
        "title": "Updated Stage Title",
        "duration_months": 12,
        "status": "in_progress"
    }
}
```

### Add Stage

```python
{
    "operation": "add",
    "entity_type": "stage",
    "data": {
        "title": "New Stage",
        "description": "Additional phase",
        "duration_months": 6,
        "status": "not_started"
    }
}
```

### Delete Stage

```python
{
    "operation": "delete",
    "entity_type": "stage",
    "entity_id": "stage-uuid"
}
```

### Update Milestone

```python
{
    "operation": "update",
    "entity_type": "milestone",
    "entity_id": "milestone-uuid",
    "data": {
        "title": "Updated Milestone",
        "is_critical": true,
        "is_completed": false
    }
}
```

### Add Milestone

```python
{
    "operation": "add",
    "entity_type": "milestone",
    "data": {
        "timeline_stage_id": "stage-uuid",
        "title": "New Milestone",
        "description": "New deliverable",
        "is_critical": false,
        "deliverable_type": "deliverable"
    }
}
```

### Delete Milestone

```python
{
    "operation": "delete",
    "entity_type": "milestone",
    "entity_id": "milestone-uuid"
}
```

## Commit Pipeline (10 Steps)

### Step 1: Validate Draft Timeline

```python
with self._trace_step("validate_draft_timeline") as step:
    draft_timeline = self.db.query(DraftTimeline).filter(
        DraftTimeline.id == draft_timeline_id
    ).first()
    
    if not draft_timeline:
        raise TimelineOrchestratorError("Draft timeline not found")
```

### Step 2: Check Commit Status

```python
with self._trace_step("check_commit_status") as step:
    existing_commit = self.db.query(CommittedTimeline).filter(
        CommittedTimeline.draft_timeline_id == draft_timeline_id
    ).first()
    
    if existing_commit:
        raise TimelineAlreadyCommittedError("Already committed")
```

### Step 3: Load Draft Content

```python
with self._trace_step("load_draft_content") as step:
    draft_stages = self.db.query(TimelineStage).filter(
        TimelineStage.draft_timeline_id == draft_timeline_id
    ).all()
    
    if not draft_stages:
        raise TimelineOrchestratorError("Cannot commit empty timeline")
```

### Step 4: Capture Edit History

```python
with self._trace_step("capture_edit_history") as step:
    edit_history = self.db.query(TimelineEditHistory).filter(
        TimelineEditHistory.draft_timeline_id == draft_timeline_id
    ).all()
```

### Step 5: Increment Version

```python
with self._trace_step("increment_version") as step:
    new_version = self._increment_version(draft_timeline.version_number)
    # "1.0" → "2.0", "2.0" → "3.0"
```

### Step 6: Create Committed Timeline

```python
with self._trace_step("create_committed_timeline") as step:
    committed_timeline = CommittedTimeline(
        user_id=user_id,
        baseline_id=draft_timeline.baseline_id,
        draft_timeline_id=draft_timeline.id,
        title=title or draft_timeline.title,
        description=description or draft_timeline.description,
        committed_date=date.today()
    )
```

### Step 7: Copy Stages and Milestones

```python
with self._trace_step("copy_stages_and_milestones") as step:
    stage_mapping = self._copy_stages_to_committed(
        draft_stages, committed_timeline.id
    )
    self._copy_milestones_to_committed(draft_stages, stage_mapping)
```

### Step 8: Freeze Draft Timeline

```python
with self._trace_step("freeze_draft_timeline") as step:
    draft_timeline.is_active = False  # Freeze
    draft_timeline.notes += f"\nStatus: COMMITTED on {date.today()}"
```

### Step 9: Commit Transaction

```python
with self._trace_step("commit_transaction"):
    self.db.commit()
    self.db.refresh(committed_timeline)
```

### Step 10: Build UI Response

```python
response = self._build_commit_response(
    committed_timeline, draft_timeline, stage_mapping, edit_history
)
```

## Edit History Tracking

Every edit is recorded in the `timeline_edit_history` table:

```json
{
  "id": "uuid",
  "draft_timeline_id": "uuid",
  "user_id": "uuid",
  "edit_type": "modified",
  "entity_type": "stage",
  "entity_id": "stage-uuid",
  "changes_json": {
    "duration_months": {
      "before": 6,
      "after": 9
    },
    "title": {
      "before": "Literature Review",
      "after": "Comprehensive Literature Review"
    }
  },
  "description": "Stage 'Literature Review' updated",
  "created_at": "2024-01-15T10:25:00"
}
```

### Query Edit History

```python
from app.models.timeline_edit_history import TimelineEditHistory

# Get all edits for a draft
edits = db.query(TimelineEditHistory).filter(
    TimelineEditHistory.draft_timeline_id == draft_id
).order_by(TimelineEditHistory.created_at).all()

# Get edits by type
modifications = [e for e in edits if e.edit_type == "modified"]
additions = [e for e in edits if e.edit_type == "added"]
deletions = [e for e in edits if e.edit_type == "deleted"]

# Get edits by entity
stage_edits = [e for e in edits if e.entity_type == "stage"]
milestone_edits = [e for e in edits if e.entity_type == "milestone"]

# Analyze changes
for edit in modifications:
    for field, change in edit.changes_json.items():
        print(f"{field}: {change['before']} → {change['after']}")
```

## Immutability Enforcement

### After Commit

```python
# Draft timeline is frozen
draft = db.query(DraftTimeline).get(draft_id)
assert draft.is_active == False

# Committed timeline is immutable
committed = db.query(CommittedTimeline).get(committed_id)
# All fields are read-only in database

# Edit attempts fail
try:
    orchestrator.apply_edits(draft_id, user_id, [{...}])
except TimelineImmutableError as e:
    print("Cannot edit committed timeline")

# Re-commit attempts return cached response (idempotency)
response1 = orchestrator.commit(request_id, draft_id, user_id)
response2 = orchestrator.commit(request_id, draft_id, user_id)
assert response1 == response2
```

## Version Management

```python
# Initial draft
draft.version_number = "1.0"

# After first commit
committed1.version = "2.0"

# If user creates new draft from baseline
draft2.version_number = "1.0"

# After second commit
committed2.version = "2.0"

# Versions increment per commit, not globally
```

## Error Handling

```python
try:
    response = orchestrator.commit(
        request_id=request_id,
        draft_timeline_id=draft_id,
        user_id=user_id
    )
except TimelineOrchestratorError as e:
    # Draft not found, empty timeline, etc.
    print(f"Validation error: {e}")
except TimelineAlreadyCommittedError as e:
    # Draft already committed
    print(f"Already committed: {e}")
except TimelineImmutableError as e:
    # Trying to edit frozen timeline
    print(f"Timeline immutable: {e}")
except IdempotencyError as e:
    # Concurrent commit with same ID
    print(f"Idempotency error: {e}")
```

## Integration with Frontend

### TypeScript Interface

```typescript
interface ApplyEditsRequest {
  draft_timeline_id: string;
  edits: Array<{
    operation: 'update' | 'add' | 'delete';
    entity_type: 'timeline' | 'stage' | 'milestone';
    entity_id?: string;
    data?: Record<string, any>;
  }>;
}

interface CommitRequest {
  request_id: string;
  draft_timeline_id: string;
  title?: string;
  description?: string;
}

interface CommitResponse {
  committed_timeline: {
    id: string;
    status: 'COMMITTED';
    is_immutable: boolean;
  };
  draft_timeline: {
    frozen: boolean;
  };
  edit_history: {
    total_edits: number;
  };
  metadata: {
    total_stages: number;
    total_milestones: number;
  };
}
```

### API Usage

```typescript
// Apply edits
async function applyEdits(draftId: string, edits: any[]) {
  const response = await fetch('/api/timelines/apply-edits', {
    method: 'POST',
    body: JSON.stringify({
      draft_timeline_id: draftId,
      edits: edits
    })
  });
  return await response.json();
}

// Commit timeline
async function commitTimeline(draftId: string) {
  const response = await fetch('/api/timelines/commit', {
    method: 'POST',
    body: JSON.stringify({
      request_id: crypto.randomUUID(),
      draft_timeline_id: draftId
    })
  });
  return await response.json();
}

// Complete flow
const edits = userEdits;  // From UI
await applyEdits(draftId, edits);
const result = await commitTimeline(draftId);
console.log(`Committed with ${result.edit_history.total_edits} edits`);
```

## Summary

✅ **Complete Implementation**  
✅ **Edit Tracking** - Full history in separate table  
✅ **Idempotent Commit** - Duplicate requests handled safely  
✅ **Immutability** - Draft frozen after commit  
✅ **Version Management** - Automatic increment  
✅ **Decision Tracing** - Complete audit trail  
✅ **Re-commit Prevention** - Built-in via idempotency  
✅ **UI-Ready** - Structured JSON responses  
✅ **Production-Ready** - Tested, documented, scalable  

The `TimelineOrchestrator.commit()` method is now complete with full edit tracking and immutability enforcement! 🚀

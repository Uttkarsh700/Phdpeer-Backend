# ProgressService - Quick Reference

## Core Methods

### Mark Milestone Completed
```python
service.mark_milestone_completed(
    milestone_id=milestone.id,
    user_id=user.id,
    completion_date=date.today(),  # Optional, defaults to today
    notes="Completion notes"       # Optional
)
```

### Log Progress Event
```python
service.log_progress_event(
    user_id=user.id,
    event_type="achievement",      # or "blocker", "update", etc.
    title="Event Title",
    description="Event description",
    event_date=date.today(),       # Optional
    milestone_id=milestone.id,     # Optional
    impact_level="high",           # Optional: low, medium, high
    tags="tag1,tag2"               # Optional
)
```

### Calculate Milestone Delay
```python
delay_info = service.calculate_milestone_delay(milestone.id)
# Returns: delay_days, status, is_completed, etc.
```

### Get Stage Progress
```python
progress = service.get_stage_progress(stage.id)
# Returns: completion_percentage, overdue_milestones, etc.
```

### Get Timeline Progress
```python
progress = service.get_timeline_progress(timeline.id)
# Returns: total metrics, completion %, delays, etc.
```

### Get Delayed Milestones
```python
delayed = service.get_all_delayed_milestones(
    timeline.id,
    include_completed=False  # Optional
)
# Returns: List of delayed milestones, sorted by delay
```

### Get Progress Summary
```python
summary = service.get_progress_summary(user.id, timeline.id)
# Returns: Complete health status and risk indicators
```

### Get User Events
```python
events = service.get_user_progress_events(
    user_id=user.id,
    milestone_id=milestone.id,  # Optional filter
    event_type="achievement",   # Optional filter
    limit=100                   # Optional, default 100
)
```

## Constants

### Event Types
```python
EVENT_TYPE_MILESTONE_COMPLETED = "milestone_completed"
EVENT_TYPE_MILESTONE_DELAYED = "milestone_delayed"
EVENT_TYPE_STAGE_STARTED = "stage_started"
EVENT_TYPE_STAGE_COMPLETED = "stage_completed"
EVENT_TYPE_ACHIEVEMENT = "achievement"
EVENT_TYPE_BLOCKER = "blocker"
EVENT_TYPE_UPDATE = "update"
```

### Impact Levels
```python
IMPACT_LOW = "low"
IMPACT_MEDIUM = "medium"
IMPACT_HIGH = "high"
```

## Delay Calculation

```
delay_days = actual_date - target_date

Positive = Delayed (overdue)
Negative = Early (ahead of schedule)
Zero = On time
```

### Status Values
- `overdue` - Incomplete and past target
- `on_track` - Incomplete and before target
- `due_today` - Target date is today
- `completed_on_time` - Completed on/before target
- `completed_delayed` - Completed after target
- `no_target_date` - No target set

## Impact Level Logic

### Critical Milestones
- `delay > 7 days` → HIGH
- `delay > 0 days` → MEDIUM
- `delay ≤ 0 days` → LOW

### Regular Milestones
- `delay > 30 days` → HIGH
- `delay > 7 days` → MEDIUM
- `delay ≤ 0 days` → LOW

## Health Status

- `early_stage` - <10% complete
- `on_track` - No critical overdue, <20% overdue
- `needs_attention` - >20% overdue
- `at_risk` - Critical milestones overdue

## Quick Examples

### Complete a Milestone
```python
service = ProgressService(db)
event_id = service.mark_milestone_completed(
    milestone.id, user.id, notes="Done!"
)
```

### Check for Delays
```python
delayed = service.get_all_delayed_milestones(timeline.id)
for m in delayed:
    print(f"{m['milestone_title']}: {m['delay_days']} days")
```

### Get Health Status
```python
summary = service.get_progress_summary(user.id, timeline.id)
print(f"Health: {summary['health_status']}")
print(f"Overdue: {summary['risk_indicators']['overdue_milestones']}")
```

### Track Stage Progress
```python
progress = service.get_stage_progress(stage.id)
print(f"Completion: {progress['completion_percentage']}%")
print(f"Overdue: {progress['overdue_milestones']}")
```

## Error Handling

```python
from app.services.progress_service import ProgressServiceError

try:
    service.mark_milestone_completed(milestone_id, user_id)
except ProgressServiceError as e:
    print(f"Error: {e}")
```

## Key Principles

✅ No prediction  
✅ No ML  
✅ Pure date arithmetic  
✅ Deterministic calculations  
✅ Full audit trail  

## Files

- `backend/app/services/progress_service.py` - Implementation
- `backend/tests/test_progress_service.py` - Tests
- `backend/PROGRESS_SERVICE_COMPLETE.md` - Full documentation

---

**Status:** ✅ Production Ready

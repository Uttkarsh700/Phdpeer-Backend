# ProgressService - Complete Implementation

## Overview

The `ProgressService` provides **pure deterministic tracking** for milestone completion and timeline progress. It computes delay flags based on planned vs actual dates with **no prediction, no ML, only date-based calculations**.

## Core Capabilities

✅ **Mark milestones as completed** - Set completion date and log event  
✅ **Append ProgressEvent records** - Full audit trail of progress  
✅ **Compute delay flags** - Planned vs actual date comparison  
✅ **Stage progress tracking** - Completion percentage per stage  
✅ **Timeline progress tracking** - Overall timeline metrics  
✅ **Delayed milestone detection** - Identify overdue items  
✅ **Progress summary** - Comprehensive health indicators  

## Key Features

### Pure Tracking
- No predictions or forecasts
- No ML models or algorithms
- Simple date arithmetic
- Deterministic calculations

### Delay Calculation
- **Positive** = Delayed (overdue)
- **Negative** = Early (ahead of schedule)
- **Zero** = On time

### Impact Levels
- **High** - Critical milestone delayed >7 days OR regular milestone >30 days
- **Medium** - Critical milestone delayed 1-7 days OR regular milestone 7-30 days
- **Low** - On time or early

## API Methods

### 1. mark_milestone_completed()

Mark a milestone as completed and automatically log a progress event.

```python
def mark_milestone_completed(
    self,
    milestone_id: UUID,
    user_id: UUID,
    completion_date: Optional[date] = None,  # Defaults to today
    notes: Optional[str] = None
) -> UUID  # Returns ProgressEvent ID
```

**Example:**
```python
from app.services.progress_service import ProgressService

service = ProgressService(db)

event_id = service.mark_milestone_completed(
    milestone_id=milestone.id,
    user_id=user.id,
    completion_date=date.today(),
    notes="Completed literature review chapter"
)

print(f"Progress event created: {event_id}")
```

**What it does:**
1. Validates milestone exists and is not already completed
2. Sets `is_completed = True`
3. Sets `actual_completion_date`
4. Appends notes to milestone
5. Calculates delay (target_date vs actual_date)
6. Determines impact level (based on delay and criticality)
7. Creates ProgressEvent with type `milestone_completed`
8. Commits to database

**Error handling:**
- Raises `ProgressServiceError` if milestone not found
- Raises `ProgressServiceError` if user not found
- Raises `ProgressServiceError` if already completed

### 2. log_progress_event()

Log any progress event (achievement, blocker, update, etc.).

```python
def log_progress_event(
    self,
    user_id: UUID,
    event_type: str,           # milestone_completed, achievement, blocker, etc.
    title: str,
    description: str,
    event_date: Optional[date] = None,    # Defaults to today
    milestone_id: Optional[UUID] = None,
    impact_level: Optional[str] = None,   # low, medium, high
    tags: Optional[str] = None,
    notes: Optional[str] = None
) -> UUID  # Returns ProgressEvent ID
```

**Event Types:**
- `milestone_completed` - Milestone completion
- `milestone_delayed` - Milestone delayed
- `stage_started` - Stage started
- `stage_completed` - Stage completed
- `achievement` - General achievement
- `blocker` - Blocker or obstacle
- `update` - General update

**Example:**
```python
event_id = service.log_progress_event(
    user_id=user.id,
    event_type=service.EVENT_TYPE_ACHIEVEMENT,
    title="Paper Accepted",
    description="Research paper accepted to conference",
    impact_level=service.IMPACT_HIGH,
    tags="publication,conference"
)
```

### 3. calculate_milestone_delay()

Calculate delay for a specific milestone.

```python
def calculate_milestone_delay(
    self,
    milestone_id: UUID
) -> Optional[Dict]
```

**Returns:**
```python
{
    "milestone_id": UUID,
    "milestone_title": str,
    "is_completed": bool,
    "is_critical": bool,
    "target_date": date,
    "actual_completion_date": date,         # If completed
    "comparison_date": date,                # Actual or today
    "delay_days": int,                      # Positive=delayed, Negative=early
    "status": str,                          # overdue, on_track, completed_delayed, etc.
    "has_target_date": bool
}
```

**Status values:**
- `overdue` - Incomplete and past target date
- `due_today` - Incomplete and target date is today
- `on_track` - Incomplete and before target date
- `completed_on_time` - Completed on or before target date
- `completed_delayed` - Completed after target date
- `no_target_date` - No target date set

**Example:**
```python
delay_info = service.calculate_milestone_delay(milestone.id)

if delay_info["delay_days"] > 0:
    print(f"Milestone is {delay_info['delay_days']} days delayed")
elif delay_info["delay_days"] < 0:
    print(f"Milestone is {abs(delay_info['delay_days'])} days ahead")
else:
    print("Milestone is on time")
```

### 4. get_stage_progress()

Get completion metrics for a specific stage.

```python
def get_stage_progress(
    self,
    stage_id: UUID
) -> Optional[Dict]
```

**Returns:**
```python
{
    "stage_id": UUID,
    "stage_title": str,
    "stage_order": int,
    "total_milestones": int,
    "completed_milestones": int,
    "pending_milestones": int,
    "completion_percentage": float,
    "overdue_milestones": int,
    "average_delay_days": float,
    "has_milestones": bool
}
```

**Example:**
```python
progress = service.get_stage_progress(stage.id)

print(f"Stage: {progress['stage_title']}")
print(f"Completion: {progress['completion_percentage']}%")
print(f"Overdue: {progress['overdue_milestones']} milestones")
print(f"Avg Delay: {progress['average_delay_days']} days")
```

### 5. get_timeline_progress()

Get overall progress metrics for a committed timeline.

```python
def get_timeline_progress(
    self,
    committed_timeline_id: UUID
) -> Optional[Dict]
```

**Returns:**
```python
{
    "timeline_id": UUID,
    "timeline_title": str,
    "committed_date": date,
    "target_completion_date": date,
    "duration_progress_percentage": float,  # Time elapsed vs total
    "total_stages": int,
    "completed_stages": int,
    "total_milestones": int,
    "completed_milestones": int,
    "pending_milestones": int,
    "completion_percentage": float,
    "critical_milestones": int,
    "completed_critical_milestones": int,
    "overdue_milestones": int,
    "overdue_critical_milestones": int,
    "average_delay_days": float,
    "max_delay_days": int,
    "has_data": bool
}
```

**Example:**
```python
progress = service.get_timeline_progress(timeline.id)

print(f"Overall Completion: {progress['completion_percentage']}%")
print(f"Time Elapsed: {progress['duration_progress_percentage']}%")
print(f"Milestones: {progress['completed_milestones']}/{progress['total_milestones']}")
print(f"Overdue: {progress['overdue_milestones']}")
print(f"Critical Overdue: {progress['overdue_critical_milestones']}")
```

### 6. get_user_progress_events()

Retrieve progress events for a user.

```python
def get_user_progress_events(
    self,
    user_id: UUID,
    milestone_id: Optional[UUID] = None,
    event_type: Optional[str] = None,
    limit: int = 100
) -> List[ProgressEvent]
```

**Example:**
```python
# All events
events = service.get_user_progress_events(user.id)

# Filtered by milestone
events = service.get_user_progress_events(
    user.id,
    milestone_id=milestone.id
)

# Filtered by type
achievements = service.get_user_progress_events(
    user.id,
    event_type=service.EVENT_TYPE_ACHIEVEMENT
)
```

### 7. get_all_delayed_milestones()

Get all delayed milestones for a timeline, sorted by delay.

```python
def get_all_delayed_milestones(
    self,
    committed_timeline_id: UUID,
    include_completed: bool = False
) -> List[Dict]
```

**Returns list of:**
```python
{
    "milestone_id": UUID,
    "milestone_title": str,
    "is_critical": bool,
    "target_date": date,
    "delay_days": int,
    "status": str,
    "stage_id": UUID,
    "stage_title": str,
    "stage_order": int
}
```

**Example:**
```python
delayed = service.get_all_delayed_milestones(timeline.id)

print(f"Found {len(delayed)} delayed milestones:")
for m in delayed[:5]:  # Top 5 most delayed
    print(f"  - {m['milestone_title']}: {m['delay_days']} days delayed")
    if m['is_critical']:
        print(f"    ⚠️ CRITICAL MILESTONE")
```

### 8. get_progress_summary()

Get comprehensive progress summary with health indicators.

```python
def get_progress_summary(
    self,
    user_id: UUID,
    committed_timeline_id: UUID
) -> Dict
```

**Returns:**
```python
{
    "has_data": bool,
    "timeline_progress": {...},           # Full timeline progress
    "delayed_milestones": [...],          # Top 5 most delayed
    "recent_events": [...],               # Last 10 events
    "health_status": str,                 # on_track, needs_attention, at_risk
    "risk_indicators": {
        "overdue_milestones": int,
        "overdue_critical": int,
        "completion_below_expected": bool,
        "average_delay_positive": bool
    }
}
```

**Health Status:**
- `early_stage` - Less than 10% complete
- `on_track` - No critical overdue, <20% overdue
- `needs_attention` - >20% milestones overdue
- `at_risk` - Critical milestones overdue

**Example:**
```python
summary = service.get_progress_summary(user.id, timeline.id)

print(f"Health Status: {summary['health_status']}")
print(f"Completion: {summary['timeline_progress']['completion_percentage']}%")
print(f"Overdue: {summary['risk_indicators']['overdue_milestones']}")
print(f"Critical Overdue: {summary['risk_indicators']['overdue_critical']}")

if summary['health_status'] == 'at_risk':
    print("\n⚠️ ATTENTION NEEDED:")
    for milestone in summary['delayed_milestones']:
        print(f"  - {milestone['milestone_title']}: {milestone['delay_days']} days")
```

## Complete Workflow Examples

### Example 1: Track Milestone Completion

```python
from datetime import date
from app.services.progress_service import ProgressService

service = ProgressService(db)

# User completes a milestone
event_id = service.mark_milestone_completed(
    milestone_id=milestone.id,
    user_id=user.id,
    completion_date=date.today(),
    notes="Completed comprehensive literature review covering 150 papers"
)

# Check if it was delayed
delay_info = service.calculate_milestone_delay(milestone.id)
print(f"Completed: {delay_info['status']}")
print(f"Delay: {delay_info['delay_days']} days")

# Get updated stage progress
stage_progress = service.get_stage_progress(milestone.timeline_stage_id)
print(f"Stage completion: {stage_progress['completion_percentage']}%")
```

### Example 2: Monitor Timeline Progress

```python
# Get overall progress
progress = service.get_timeline_progress(timeline.id)

print(f"Timeline: {progress['timeline_title']}")
print(f"Overall Completion: {progress['completion_percentage']}%")
print(f"Time Elapsed: {progress['duration_progress_percentage']}%")
print(f"\nMilestones:")
print(f"  Total: {progress['total_milestones']}")
print(f"  Completed: {progress['completed_milestones']}")
print(f"  Pending: {progress['pending_milestones']}")
print(f"  Overdue: {progress['overdue_milestones']}")
print(f"\nCritical Milestones:")
print(f"  Total: {progress['critical_milestones']}")
print(f"  Completed: {progress['completed_critical_milestones']}")
print(f"  Overdue: {progress['overdue_critical_milestones']}")
print(f"\nDelay Metrics:")
print(f"  Average: {progress['average_delay_days']} days")
print(f"  Maximum: {progress['max_delay_days']} days")
```

### Example 3: Identify Delayed Milestones

```python
# Get all delayed milestones
delayed = service.get_all_delayed_milestones(timeline.id)

if delayed:
    print(f"⚠️ {len(delayed)} delayed milestones:\n")
    
    for milestone in delayed:
        status_icon = "🔴" if milestone['is_critical'] else "🟡"
        print(f"{status_icon} {milestone['milestone_title']}")
        print(f"   Stage: {milestone['stage_title']}")
        print(f"   Delay: {milestone['delay_days']} days")
        print(f"   Target: {milestone['target_date']}")
        print()
else:
    print("✅ All milestones on track!")
```

### Example 4: Log Custom Progress Events

```python
# Log achievement
service.log_progress_event(
    user_id=user.id,
    event_type=service.EVENT_TYPE_ACHIEVEMENT,
    title="Paper Published",
    description="First-author paper published in top-tier journal",
    impact_level=service.IMPACT_HIGH,
    tags="publication,first-author"
)

# Log blocker
service.log_progress_event(
    user_id=user.id,
    event_type=service.EVENT_TYPE_BLOCKER,
    title="Equipment Malfunction",
    description="Lab equipment malfunction delaying data collection",
    impact_level=service.IMPACT_HIGH,
    tags="blocker,equipment"
)

# Log general update
service.log_progress_event(
    user_id=user.id,
    milestone_id=milestone.id,
    event_type=service.EVENT_TYPE_UPDATE,
    title="Milestone Progress Update",
    description="50% complete with data analysis",
    impact_level=service.IMPACT_LOW,
    notes="On track to complete by target date"
)
```

### Example 5: Generate Progress Report

```python
# Get comprehensive summary
summary = service.get_progress_summary(user.id, timeline.id)

print("=" * 60)
print("PhD PROGRESS REPORT")
print("=" * 60)

progress = summary['timeline_progress']
print(f"\nTimeline: {progress['timeline_title']}")
print(f"Committed: {progress['committed_date']}")
print(f"Target Completion: {progress['target_completion_date']}")
print(f"\nOVERALL HEALTH: {summary['health_status'].upper()}")

print(f"\nCOMPLETION METRICS:")
print(f"  Milestones: {progress['completed_milestones']}/{progress['total_milestones']}")
print(f"  Percentage: {progress['completion_percentage']}%")
print(f"  Time Elapsed: {progress['duration_progress_percentage']}%")

risks = summary['risk_indicators']
if risks['overdue_critical'] > 0:
    print(f"\n⚠️ CRITICAL ISSUES:")
    print(f"  {risks['overdue_critical']} critical milestones overdue")

if summary['delayed_milestones']:
    print(f"\n🟡 DELAYED MILESTONES:")
    for m in summary['delayed_milestones'][:3]:
        print(f"  - {m['milestone_title']}: {m['delay_days']} days")

print(f"\n📊 RECENT ACTIVITY:")
for event in summary['recent_events'][:5]:
    print(f"  [{event['event_date']}] {event['title']}")

print("\n" + "=" * 60)
```

### Example 6: Stage-by-Stage Progress

```python
# Get all stages
stages = db.query(TimelineStage).filter(
    TimelineStage.committed_timeline_id == timeline.id
).order_by(TimelineStage.stage_order).all()

print("STAGE-BY-STAGE PROGRESS\n")

for stage in stages:
    progress = service.get_stage_progress(stage.id)
    
    status_icon = "✅" if progress['completion_percentage'] == 100 else "⏳"
    print(f"{status_icon} Stage {progress['stage_order']}: {progress['stage_title']}")
    print(f"   Completion: {progress['completion_percentage']}%")
    print(f"   Milestones: {progress['completed_milestones']}/{progress['total_milestones']}")
    
    if progress['overdue_milestones'] > 0:
        print(f"   ⚠️ Overdue: {progress['overdue_milestones']}")
    
    if progress['average_delay_days'] > 0:
        print(f"   Avg Delay: {progress['average_delay_days']} days")
    
    print()
```

## Delay Calculation Logic

### How Delays Are Calculated

```python
delay_days = actual_date - target_date

# Examples:
# Target: 2024-01-01, Actual: 2024-01-05 → delay_days = 4 (delayed)
# Target: 2024-01-01, Actual: 2023-12-28 → delay_days = -4 (early)
# Target: 2024-01-01, Actual: 2024-01-01 → delay_days = 0 (on time)
```

### For Incomplete Milestones

```python
delay_days = today - target_date

# Examples:
# Target: 2024-01-01, Today: 2024-01-05 → delay_days = 4 (overdue)
# Target: 2024-01-10, Today: 2024-01-05 → delay_days = -5 (upcoming)
```

### Impact Level Determination

**Critical Milestones:**
- `delay_days > 7` → HIGH impact
- `delay_days > 0` → MEDIUM impact
- `delay_days ≤ 0` → LOW impact

**Regular Milestones:**
- `delay_days > 30` → HIGH impact
- `delay_days > 7` → MEDIUM impact
- `delay_days ≤ 0` → LOW impact

## Error Handling

```python
from app.services.progress_service import ProgressServiceError

try:
    service.mark_milestone_completed(milestone_id, user_id)
except ProgressServiceError as e:
    if "not found" in str(e):
        print("Milestone or user not found")
    elif "already marked as completed" in str(e):
        print("Milestone already completed")
    else:
        print(f"Error: {e}")
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
pytest tests/test_progress_service.py -v
```

**Test Coverage:**
- ✅ Mark milestone completed
- ✅ Log progress events
- ✅ Calculate delays (overdue, on track, early, late)
- ✅ Stage progress tracking
- ✅ Timeline progress tracking
- ✅ Critical milestone tracking
- ✅ Duration progress calculation
- ✅ Event filtering
- ✅ Error handling

## Integration with Frontend

### TypeScript Interfaces

```typescript
interface MilestoneDelayInfo {
  milestone_id: string;
  milestone_title: string;
  is_completed: boolean;
  is_critical: boolean;
  target_date: string;
  actual_completion_date?: string;
  delay_days: number;
  status: 'overdue' | 'on_track' | 'completed_on_time' | 'completed_delayed';
}

interface StageProgress {
  stage_id: string;
  stage_title: string;
  total_milestones: number;
  completed_milestones: number;
  completion_percentage: number;
  overdue_milestones: number;
  average_delay_days: number;
}

interface TimelineProgress {
  timeline_id: string;
  timeline_title: string;
  completion_percentage: number;
  duration_progress_percentage: number;
  total_milestones: number;
  completed_milestones: number;
  overdue_milestones: number;
  overdue_critical_milestones: number;
}

interface ProgressSummary {
  health_status: 'early_stage' | 'on_track' | 'needs_attention' | 'at_risk';
  timeline_progress: TimelineProgress;
  delayed_milestones: MilestoneDelayInfo[];
  risk_indicators: {
    overdue_milestones: number;
    overdue_critical: number;
    completion_below_expected: boolean;
  };
}
```

### API Service

```typescript
// services/progressService.ts

export async function markMilestoneCompleted(
  milestoneId: string,
  completionDate?: string,
  notes?: string
): Promise<string> {
  const response = await api.post(`/milestones/${milestoneId}/complete`, {
    completion_date: completionDate,
    notes
  });
  return response.data.event_id;
}

export async function getTimelineProgress(
  timelineId: string
): Promise<TimelineProgress> {
  const response = await api.get(`/timelines/${timelineId}/progress`);
  return response.data;
}

export async function getProgressSummary(
  timelineId: string
): Promise<ProgressSummary> {
  const response = await api.get(`/timelines/${timelineId}/progress/summary`);
  return response.data;
}
```

## Key Principles

✅ **No Prediction** - Only tracks what has happened  
✅ **No ML** - Pure date arithmetic  
✅ **Deterministic** - Same inputs = same outputs  
✅ **Transparent** - All calculations visible  
✅ **Auditable** - Full event history  

## Summary

The `ProgressService` provides a **complete, production-ready solution** for tracking PhD timeline progress with:

- ✅ Milestone completion tracking
- ✅ Progress event logging
- ✅ Delay calculation and flagging
- ✅ Stage and timeline metrics
- ✅ Health indicators
- ✅ Comprehensive test coverage
- ✅ Full documentation

**Pure tracking. No ML. No prediction. Just facts.** 📊

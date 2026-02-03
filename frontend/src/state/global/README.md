# Global State Model

## Overview

The global state model mirrors backend state exactly. It stores the current state of user's resources (baseline, timeline, questionnaire, analytics) without any computed or derived fields.

## Quick Start

```typescript
import { useBaselineStatus, useGlobalStateActions } from '@/state/global';

function MyComponent() {
  const baselineStatus = useBaselineStatus();
  const { setBaselineStatus } = useGlobalStateActions();

  // Update state after API call
  const handleCreate = async () => {
    await baselineService.create(data);
    setBaselineStatus('EXISTS'); // Update from API response
  };

  return <div>Status: {baselineStatus}</div>;
}
```

See [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) for complete examples.

## Design Principles

1. **Backend is source of truth** - All state reflects actual backend data
2. **No computed fields** - Only store what comes from backend API
3. **No derived flags** - Do not compute status from other fields
4. **Direct mapping** - Each field maps directly to backend model/response

## State Fields

### baselineStatus: 'NONE' | 'EXISTS'

**Purpose:** Tracks whether user has a baseline record.

**Why it exists:**
- Baselines are required before creating timelines
- Determines which UI flows are available
- Avoids repeated API calls to check baseline existence

**Backend source:** `backend/app/models/baseline.py::Baseline`
- If user has >= 1 Baseline: `'EXISTS'`
- If user has 0 Baselines: `'NONE'`

**Update triggers:**
- User creates baseline → `'NONE'` → `'EXISTS'`
- User deletes baseline → `'EXISTS'` → `'NONE'`

---

### timelineStatus: 'NONE' | 'DRAFT' | 'COMMITTED'

**Purpose:** Tracks the current timeline state.

**Why it exists:**
- Backend has two separate models: DraftTimeline and CommittedTimeline
- Determines which timeline UI to show
- Controls workflow: create draft → commit draft → view committed

**Backend sources:**
- `backend/app/models/draft_timeline.py::DraftTimeline` (is_active field)
- `backend/app/models/committed_timeline.py::CommittedTimeline`

**State values:**
- `'NONE'`: No DraftTimeline and no CommittedTimeline
- `'DRAFT'`: Has DraftTimeline (is_active=true for active draft)
- `'COMMITTED'`: Has CommittedTimeline

**Note:** User can have both DRAFT and COMMITTED (different timelines). This represents the "current" state.

**Update triggers:**
- User creates draft timeline → `'NONE'` → `'DRAFT'`
- User commits draft → `'DRAFT'` → `'COMMITTED'`
- User deletes timeline → `'COMMITTED'` → `'NONE'`

---

### doctorStatus: 'DRAFT' | 'SUBMITTED'

**Purpose:** Tracks questionnaire draft/submission state.

**Why it exists:**
- Determines if user can resume draft or view submitted assessment
- Controls questionnaire UI flow

**Backend source:** `backend/app/models/questionnaire_draft.py::QuestionnaireDraft`
- `is_submitted: boolean` (false = DRAFT, true = SUBMITTED)

**State values:**
- `'DRAFT'`: Has QuestionnaireDraft with is_submitted=false
- `'SUBMITTED'`: Has QuestionnaireDraft with is_submitted=true

**Note:** When draft is submitted, is_submitted becomes true and draft becomes immutable.

**Update triggers:**
- User creates/saves draft → `'DRAFT'`
- User submits questionnaire → `'DRAFT'` → `'SUBMITTED'`

---

### analyticsStatus: 'AVAILABLE' | 'UNAVAILABLE'

**Purpose:** Tracks whether analytics can be generated/retrieved.

**Why it exists:**
- Backend requires CommittedTimeline to generate analytics
- Determines if analytics dashboard can be shown
- Reflects backend invariant: "No analytics without committed timeline"

**Backend sources:**
- `backend/app/models/committed_timeline.py::CommittedTimeline` (required)
- `backend/app/models/analytics_snapshot.py::AnalyticsSnapshot` (cached)
- `backend/app/utils/invariants.py::check_analytics_has_committed_timeline`

**State values:**
- `'AVAILABLE'`: User has CommittedTimeline (analytics can be generated)
- `'UNAVAILABLE'`: User has no CommittedTimeline (analytics cannot be generated)

**Update triggers:**
- User commits timeline → `'UNAVAILABLE'` → `'AVAILABLE'`
- User deletes committed timeline → `'AVAILABLE'` → `'UNAVAILABLE'`

---

## Usage

### Import Types

```typescript
import type { GlobalState, BaselineStatus, TimelineStatus, DoctorStatus, AnalyticsStatus } from '@/state/types';
```

### Initialize State

```typescript
import { initialGlobalState } from '@/state/types';

const state: GlobalState = { ...initialGlobalState };
```

### Update State from Backend

```typescript
// After fetching baseline
if (baseline) {
  state.baselineStatus = 'EXISTS';
} else {
  state.baselineStatus = 'NONE';
}

// After fetching timeline
if (committedTimeline) {
  state.timelineStatus = 'COMMITTED';
} else if (draftTimeline) {
  state.timelineStatus = 'DRAFT';
} else {
  state.timelineStatus = 'NONE';
}

// After fetching questionnaire draft
if (draft.is_submitted) {
  state.doctorStatus = 'SUBMITTED';
} else {
  state.doctorStatus = 'DRAFT';
}

// After checking analytics availability
if (committedTimeline) {
  state.analyticsStatus = 'AVAILABLE';
} else {
  state.analyticsStatus = 'UNAVAILABLE';
}
```

## What NOT to Include

❌ **Computed fields:**
- `canCreateTimeline` (computed from baselineStatus)
- `hasActiveDraft` (computed from timelineStatus)
- `canViewAnalytics` (computed from analyticsStatus)

❌ **Derived flags:**
- `isTimelineReady` (derived from multiple fields)
- `isWorkflowComplete` (derived from all fields)

❌ **UI state:**
- `isLoading`
- `error`
- `lastUpdated`

These should be in separate UI state, not global state.

## State Updates

State should be updated:
1. **After API calls** - When backend data is fetched
2. **After mutations** - When user creates/updates/deletes resources
3. **On login** - Fetch all state on user authentication
4. **On refresh** - Re-fetch state when app loads

State should NOT be updated:
- Based on UI interactions alone
- Based on computed values
- Based on assumptions

## Backend Mapping

| Frontend State | Backend Check | Backend Model/Field |
|----------------|---------------|---------------------|
| `baselineStatus: 'EXISTS'` | `user.baselines.count() > 0` | `Baseline` |
| `timelineStatus: 'DRAFT'` | `user.draft_timelines.filter(is_active=True).exists()` | `DraftTimeline.is_active` |
| `timelineStatus: 'COMMITTED'` | `user.committed_timelines.exists()` | `CommittedTimeline` |
| `doctorStatus: 'DRAFT'` | `user.questionnaire_drafts.filter(is_submitted=False).exists()` | `QuestionnaireDraft.is_submitted` |
| `doctorStatus: 'SUBMITTED'` | `user.questionnaire_drafts.filter(is_submitted=True).exists()` | `QuestionnaireDraft.is_submitted` |
| `analyticsStatus: 'AVAILABLE'` | `user.committed_timelines.exists()` | `CommittedTimeline` (required) |

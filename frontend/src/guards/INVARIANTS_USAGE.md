# Frontend Invariant Checks

## Overview

Frontend invariant checks enforce business rules based on backend state. These guards prevent invalid operations before API calls are made.

## Rules

1. **No timeline generation without baseline**
   - Invariant: `baselineStatus === 'EXISTS'`
   - Checked before: Timeline generation API calls

2. **No commit without draft**
   - Invariant: `timelineStatus === 'DRAFT'`
   - Checked before: Timeline commit API calls

3. **No progress without committed timeline**
   - Invariant: `timelineStatus === 'COMMITTED'`
   - Checked before: Progress tracking API calls

4. **No analytics without committed timeline**
   - Invariant: `analyticsStatus === 'AVAILABLE'`
   - Checked before: Analytics API calls

## Usage

### Direct Function Calls

```typescript
import { 
  checkTimelineGenerationRequiresBaseline,
  checkCommitRequiresDraft,
  checkProgressRequiresCommittedTimeline,
  checkAnalyticsRequiresCommittedTimeline 
} from '@/guards/invariants';
import { useGlobalStateStore } from '@/state/global';

function MyComponent() {
  const state = useGlobalStateStore();

  const handleGenerate = async () => {
    try {
      // Check invariant before API call
      checkTimelineGenerationRequiresBaseline(state);
      
      // Proceed with API call
      await timelineService.generate({ ... });
    } catch (error) {
      if (error.name === 'InvariantViolationError') {
        // Show error message from invariant
        setError(error.message);
      }
    }
  };
}
```

### Using InvariantGuard Component

```typescript
import { InvariantGuard } from '@/components/InvariantGuard';

function MyPage() {
  return (
    <InvariantGuard
      operation="timeline_generation"
      fallback={<Navigate to="/documents/upload" />}
    >
      <TimelineGenerationForm />
    </InvariantGuard>
  );
}
```

### Using checkInvariant Helper

```typescript
import { checkInvariant } from '@/guards/invariants';

const result = checkInvariant('timeline_generation', state);
if (!result.valid) {
  // Handle error
  console.error(result.error);
}
```

## Integration Points

### 1. Timeline Generation
- **File**: `frontend/src/pages/DraftTimelinePage.tsx`
- **Check**: `checkTimelineGenerationRequiresBaseline()`
- **Location**: Before `generateTimeline()` and `checkAndGenerate()`

### 2. Timeline Commit
- **File**: `frontend/src/pages/DraftTimelinePage.tsx`
- **Check**: `checkCommitRequiresDraft()`
- **Location**: Before `handleCommit()` and commit button click

### 3. Progress Tracking
- **File**: `frontend/src/pages/TimelineProgressPage.tsx`
- **Check**: `checkProgressRequiresCommittedTimeline()`
- **Location**: Before `loadTimeline()`

### 4. Analytics Dashboard
- **File**: `frontend/src/pages/DashboardPage.tsx`
- **Check**: `checkAnalyticsRequiresCommittedTimeline()`
- **Location**: Before `loadAnalytics()`

## Error Handling

All invariant checks throw `InvariantViolationError` with:
- `message`: Human-readable error message
- `invariant`: Invariant name (e.g., 'timeline_generation_requires_baseline')
- `currentState`: Current global state snapshot

```typescript
try {
  checkTimelineGenerationRequiresBaseline(state);
} catch (error) {
  if (error instanceof InvariantViolationError) {
    // Use backend state-based error message
    setError(error.message);
    // Optionally log invariant name
    console.log('Violated invariant:', error.invariant);
  }
}
```

## Important Notes

- **Guards rely only on backend state**: All checks use `GlobalState` from the store
- **No guessing**: Error messages come from invariant checks, not assumptions
- **Prevents invalid API calls**: Checks happen before API calls to avoid unnecessary requests
- **Type-safe**: TypeScript ensures correct usage

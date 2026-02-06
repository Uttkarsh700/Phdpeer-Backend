# Frontend State Guards

## Overview

Frontend guards that enforce business rules based on backend state only. These guards check the global state store that mirrors backend state.

## Rules Enforced

1. **No timeline generation without baseline**
   - Guard: `guardTimelineGenerationRequiresBaseline`
   - Checks: `baselineStatus === 'EXISTS'`

2. **No commit without draft**
   - Guard: `guardCommitRequiresDraft`
   - Checks: `timelineStatus === 'DRAFT'`

3. **No progress without committed timeline**
   - Guard: `guardProgressRequiresCommittedTimeline`
   - Checks: `timelineStatus === 'COMMITTED'`

4. **No analytics without committed timeline**
   - Guard: `guardAnalyticsRequiresCommittedTimeline`
   - Checks: `timelineStatus === 'COMMITTED'`

## Usage

### Basic Usage

```typescript
import { 
  guardTimelineGenerationRequiresBaseline,
  guardCommitRequiresDraft,
  guardProgressRequiresCommittedTimeline,
  guardAnalyticsRequiresCommittedTimeline,
  GuardViolationError 
} from '@/guards';
import { useGlobalStateStore } from '@/store/global-state';
import { toast } from '@/hooks/use-toast';

const MyComponent = () => {
  const state = useGlobalStateStore();
  
  const handleGenerateTimeline = async () => {
    try {
      // Check guard before API call
      guardTimelineGenerationRequiresBaseline(state);
      
      // Proceed with timeline generation
      await generateTimeline();
    } catch (error) {
      if (error instanceof GuardViolationError) {
        toast({
          title: "Cannot Generate Timeline",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      throw error;
    }
  };
  
  const handleCommitTimeline = async () => {
    try {
      guardCommitRequiresDraft(state);
      await commitTimeline();
    } catch (error) {
      if (error instanceof GuardViolationError) {
        toast({
          title: "Cannot Commit Timeline",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      throw error;
    }
  };
  
  const handleTrackProgress = async () => {
    try {
      guardProgressRequiresCommittedTimeline(state);
      await trackProgress();
    } catch (error) {
      if (error instanceof GuardViolationError) {
        toast({
          title: "Cannot Track Progress",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      throw error;
    }
  };
  
  const handleViewAnalytics = async () => {
    try {
      guardAnalyticsRequiresCommittedTimeline(state);
      await loadAnalytics();
    } catch (error) {
      if (error instanceof GuardViolationError) {
        toast({
          title: "Cannot Load Analytics",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      throw error;
    }
  };
};
```

### Using the Hook

```typescript
import { useStateGuards } from '@/guards';

const MyComponent = () => {
  const { state, checkGuard } = useStateGuards();
  
  const handleAction = () => {
    try {
      checkGuard(guardTimelineGenerationRequiresBaseline);
      // Proceed with action
    } catch (error) {
      // Handle guard violation
    }
  };
};
```

### Disable Button Based on Guard

```typescript
import { guardTimelineGenerationRequiresBaseline } from '@/guards';
import { useGlobalStateStore } from '@/store/global-state';

const MyComponent = () => {
  const state = useGlobalStateStore();
  
  // Check if action is allowed
  const canGenerateTimeline = () => {
    try {
      guardTimelineGenerationRequiresBaseline(state);
      return true;
    } catch {
      return false;
    }
  };
  
  return (
    <Button 
      disabled={!canGenerateTimeline()}
      onClick={handleGenerateTimeline}
    >
      Generate Timeline
    </Button>
  );
};
```

## Integration Points

### Timeline Generation
- **Page:** Draft Timeline Page or Timeline Generation Page
- **Guard:** `guardTimelineGenerationRequiresBaseline`
- **Location:** Before calling `POST /api/v1/timelines/draft/generate`

### Timeline Commit
- **Page:** Draft Timeline Page
- **Guard:** `guardCommitRequiresDraft`
- **Location:** Before calling `POST /api/v1/timelines/draft/{id}/commit`

### Progress Tracking
- **Page:** Progress Tracking Page
- **Guard:** `guardProgressRequiresCommittedTimeline`
- **Location:** Before calling `POST /api/v1/progress/milestones/{id}/complete` or loading progress page

### Analytics Dashboard
- **Page:** Analytics Dashboard Page
- **Guard:** `guardAnalyticsRequiresCommittedTimeline`
- **Location:** Before calling `GET /api/v1/analytics/summary` or loading dashboard

## Important Notes

1. **Backend State Only**: Guards rely ONLY on the global state store that mirrors backend state. No computed flags or frontend intelligence.

2. **State Updates**: State must be updated when API calls succeed:
   - `baselineStatus` → 'EXISTS' after `POST /baselines` succeeds
   - `timelineStatus` → 'DRAFT' after `POST /timelines/draft/generate` succeeds
   - `timelineStatus` → 'COMMITTED' after `POST /timelines/draft/{id}/commit` succeeds

3. **Error Handling**: Guards throw `GuardViolationError` which should be caught and displayed to the user.

4. **No Optimistic Updates**: Guards check state before API calls, but the backend is the final validator. If state is stale, the backend will reject the request.

## Example: Complete Integration

```typescript
import { 
  guardTimelineGenerationRequiresBaseline,
  GuardViolationError 
} from '@/guards';
import { useGlobalStateStore } from '@/store/global-state';
import { toast } from '@/hooks/use-toast';

const DraftTimelinePage = () => {
  const state = useGlobalStateStore();
  const setTimelineStatus = useGlobalStateStore((state) => state.setTimelineStatus);
  
  const handleGenerateTimeline = async () => {
    try {
      // Check guard before API call
      guardTimelineGenerationRequiresBaseline(state);
      
      // Call backend
      const response = await generateTimeline();
      
      // Update state after successful API call
      setTimelineStatus('DRAFT');
      
      toast({
        title: "Timeline Generated",
        description: "Your draft timeline has been created.",
      });
    } catch (error) {
      if (error instanceof GuardViolationError) {
        toast({
          title: "Cannot Generate Timeline",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      
      // Handle other errors
      toast({
        title: "Error",
        description: "Failed to generate timeline. Please try again.",
        variant: "destructive",
      });
    }
  };
  
  return (
    <Button 
      onClick={handleGenerateTimeline}
      disabled={state.baselineStatus !== 'EXISTS'}
    >
      Generate Timeline
    </Button>
  );
};
```

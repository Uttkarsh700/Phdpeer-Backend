# Global State Store - Usage Examples

## Overview

The global state store is a lightweight Zustand store that mirrors backend state. State updates **ONLY** come from API responses - no computed intelligence.

## Basic Usage

### Reading State

```typescript
import { useBaselineStatus, useTimelineStatus } from '@/state/global';

function MyComponent() {
  // Read individual status values
  const baselineStatus = useBaselineStatus();
  const timelineStatus = useTimelineStatus();

  return (
    <div>
      <p>Baseline: {baselineStatus}</p>
      <p>Timeline: {timelineStatus}</p>
    </div>
  );
}
```

### Reading All State

```typescript
import { useGlobalStateStore } from '@/state/global';

function MyComponent() {
  // Read entire state
  const state = useGlobalStateStore();

  return (
    <div>
      <p>Baseline: {state.baselineStatus}</p>
      <p>Timeline: {state.timelineStatus}</p>
      <p>Doctor: {state.doctorStatus}</p>
      <p>Analytics: {state.analyticsStatus}</p>
    </div>
  );
}
```

### Using Selector Hooks (Optimized)

```typescript
import { useBaselineStatus, useTimelineStatus } from '@/state/global';

function MyComponent() {
  // These hooks only re-render when their specific value changes
  const baselineStatus = useBaselineStatus();
  const timelineStatus = useTimelineStatus();

  // Component only re-renders when baselineStatus or timelineStatus changes
  // Not when doctorStatus or analyticsStatus changes
}
```

## Writing State (From API Responses)

### Update After API Call

```typescript
import { useGlobalStateActions } from '@/state/global';
import { baselineService } from '@/services/baseline.service';

function useBaselineData() {
  const { setBaselineStatus } = useGlobalStateActions();

  const fetchBaselines = async () => {
    try {
      const baselines = await baselineService.getUserBaselines();
      
      // Update state from API response
      if (baselines.length > 0) {
        setBaselineStatus('EXISTS');
      } else {
        setBaselineStatus('NONE');
      }
    } catch (error) {
      // Handle error - don't update state on error
      console.error('Failed to fetch baselines:', error);
    }
  };

  return { fetchBaselines };
}
```

### Update After Creating Baseline

```typescript
import { useGlobalStateActions } from '@/state/global';
import { baselineService } from '@/services/baseline.service';

function CreateBaselineForm() {
  const { setBaselineStatus } = useGlobalStateActions();

  const handleSubmit = async (data: CreateBaselineRequest) => {
    try {
      // Create baseline via API
      const result = await baselineService.create(data);
      
      // Update state from API response (baseline was created)
      setBaselineStatus('EXISTS');
      
      // Navigate or show success
    } catch (error) {
      // Handle error - state remains unchanged
      console.error('Failed to create baseline:', error);
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Update Timeline Status

```typescript
import { useGlobalStateActions } from '@/state/global';
import { timelineService } from '@/services/timeline.service';

function useTimelineData() {
  const { setTimelineStatus } = useGlobalStateActions();

  const checkTimelineStatus = async () => {
    try {
      // Check for committed timeline first
      const committed = await timelineService.getUserCommitted();
      if (committed.length > 0) {
        setTimelineStatus('COMMITTED');
        return;
      }

      // Check for draft timeline
      const drafts = await timelineService.getUserDrafts();
      if (drafts.length > 0) {
        setTimelineStatus('DRAFT');
        return;
      }

      // No timeline exists
      setTimelineStatus('NONE');
    } catch (error) {
      console.error('Failed to check timeline status:', error);
    }
  };

  return { checkTimelineStatus };
}
```

### Update After Committing Timeline

```typescript
import { useGlobalStateActions } from '@/state/global';
import { timelineService } from '@/services/timeline.service';

function CommitTimelineButton({ draftId }: { draftId: string }) {
  const { setTimelineStatus, setAnalyticsStatus } = useGlobalStateActions();

  const handleCommit = async () => {
    try {
      // Commit timeline via API
      const result = await timelineService.commit({ draftTimelineId: draftId });
      
      // Update state from API response
      setTimelineStatus('COMMITTED');
      setAnalyticsStatus('AVAILABLE'); // Analytics now available
      
      // Navigate or show success
    } catch (error) {
      console.error('Failed to commit timeline:', error);
    }
  };

  return <button onClick={handleCommit}>Commit Timeline</button>;
}
```

### Update Questionnaire Status

```typescript
import { useGlobalStateActions } from '@/state/global';
import { assessmentService } from '@/services/assessment.service';

function QuestionnaireForm() {
  const { setDoctorStatus } = useGlobalStateActions();

  const handleSubmit = async (responses: QuestionnaireResponse[]) => {
    try {
      // Submit questionnaire via API
      const result = await assessmentService.submitQuestionnaire({ responses });
      
      // Update state from API response (questionnaire was submitted)
      setDoctorStatus('SUBMITTED');
      
      // Navigate to results
    } catch (error) {
      console.error('Failed to submit questionnaire:', error);
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Update Multiple States at Once

```typescript
import { useGlobalStateActions } from '@/state/global';

function useAppInitialization() {
  const { setState } = useGlobalStateActions();

  const initializeApp = async () => {
    try {
      // Fetch all state from backend
      const [baselines, timelines, drafts, analytics] = await Promise.all([
        baselineService.getUserBaselines(),
        timelineService.getUserCommitted(),
        timelineService.getUserDrafts(),
        assessmentService.getLatest(),
      ]);

      // Update all state at once from API responses
      setState({
        baselineStatus: baselines.length > 0 ? 'EXISTS' : 'NONE',
        timelineStatus: timelines.length > 0 ? 'COMMITTED' : 
                        drafts.length > 0 ? 'DRAFT' : 'NONE',
        doctorStatus: drafts.some(d => d.is_submitted) ? 'SUBMITTED' : 'DRAFT',
        analyticsStatus: timelines.length > 0 ? 'AVAILABLE' : 'UNAVAILABLE',
      });
    } catch (error) {
      console.error('Failed to initialize app:', error);
    }
  };

  return { initializeApp };
}
```

## Reset State

### Reset on Logout

```typescript
import { useGlobalStateActions } from '@/state/global';

function LogoutButton() {
  const { reset } = useGlobalStateActions();

  const handleLogout = async () => {
    // Clear auth token
    localStorage.removeItem('auth_token');
    
    // Reset global state
    reset();
    
    // Navigate to login
    navigate('/login');
  };

  return <button onClick={handleLogout}>Logout</button>;
}
```

### Reset on App Reload

```typescript
import { useEffect } from 'react';
import { useGlobalStateActions } from '@/state/global';

function App() {
  const { reset } = useGlobalStateActions();

  useEffect(() => {
    // Reset state on app mount (fresh start)
    reset();
    
    // Then fetch current state from backend
    initializeApp();
  }, []);

  return <div>...</div>;
}
```

### Reset on Error Recovery

```typescript
import { useGlobalStateActions } from '@/state/global';

function ErrorRecovery() {
  const { reset } = useGlobalStateActions();

  const handleRecover = () => {
    // Reset to known good state
    reset();
    
    // Re-fetch from backend
    refetchAllData();
  };

  return <button onClick={handleRecover}>Reset & Retry</button>;
}
```

## Complete Example: Service Hook

```typescript
import { useGlobalStateActions, useBaselineStatus } from '@/state/global';
import { baselineService } from '@/services/baseline.service';
import { useEffect, useState } from 'react';

function useBaseline() {
  const baselineStatus = useBaselineStatus();
  const { setBaselineStatus } = useGlobalStateActions();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch baseline status from API
  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const baselines = await baselineService.getUserBaselines();
      
      // Update state from API response
      setBaselineStatus(baselines.length > 0 ? 'EXISTS' : 'NONE');
    } catch (err) {
      setError(err as Error);
      // Don't update state on error
    } finally {
      setLoading(false);
    }
  };

  // Create baseline
  const createBaseline = async (data: CreateBaselineRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      await baselineService.create(data);
      
      // Update state from API response (baseline created)
      setBaselineStatus('EXISTS');
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return {
    baselineStatus,
    loading,
    error,
    fetchStatus,
    createBaseline,
  };
}

// Usage in component
function BaselinePage() {
  const { baselineStatus, loading, createBaseline } = useBaseline();

  if (loading) return <Spinner />;
  if (baselineStatus === 'NONE') {
    return <CreateBaselineForm onSubmit={createBaseline} />;
  }
  return <BaselineView />;
}
```

## Rules to Follow

### ✅ DO

1. **Update state from API responses only**
   ```typescript
   const result = await api.get(...);
   setBaselineStatus(result.length > 0 ? 'EXISTS' : 'NONE');
   ```

2. **Reset state on logout/reload**
   ```typescript
   reset(); // Clear all state
   ```

3. **Use selector hooks for performance**
   ```typescript
   const status = useBaselineStatus(); // Only re-renders when this changes
   ```

### ❌ DON'T

1. **Don't compute state from other state**
   ```typescript
   // ❌ WRONG
   const canCreateTimeline = baselineStatus === 'EXISTS' && timelineStatus === 'NONE';
   // This should be computed in component, not stored in state
   ```

2. **Don't update state from UI interactions**
   ```typescript
   // ❌ WRONG
   const handleClick = () => {
     setBaselineStatus('EXISTS'); // Don't do this!
   };
   ```

3. **Don't derive state from state**
   ```typescript
   // ❌ WRONG
   const analyticsAvailable = timelineStatus === 'COMMITTED';
   // This should be computed, not stored
   ```

## Summary

- **Read**: Use `useBaselineStatus()`, `useTimelineStatus()`, etc.
- **Write**: Use `setBaselineStatus()`, `setTimelineStatus()`, etc. **only after API calls**
- **Reset**: Use `reset()` on logout, reload, or error recovery
- **No computed values**: Compute derived values in components, not in state

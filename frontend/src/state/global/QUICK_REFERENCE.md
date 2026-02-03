# Global State Store - Quick Reference

## Import

```typescript
import { 
  useBaselineStatus,
  useTimelineStatus,
  useDoctorStatus,
  useAnalyticsStatus,
  useGlobalStateActions 
} from '@/state/global';
```

## Read State

```typescript
// Individual status hooks (optimized)
const baselineStatus = useBaselineStatus();
const timelineStatus = useTimelineStatus();

// Or all at once
const state = useGlobalStateStore();
```

## Update State (After API Calls)

```typescript
const { setBaselineStatus, setTimelineStatus, setState, reset } = useGlobalStateActions();

// Update single status
setBaselineStatus('EXISTS');

// Update multiple at once
setState({
  baselineStatus: 'EXISTS',
  timelineStatus: 'COMMITTED',
});

// Reset all state
reset();
```

## Common Patterns

### After Creating Baseline
```typescript
await baselineService.create(data);
setBaselineStatus('EXISTS');
```

### After Committing Timeline
```typescript
await timelineService.commit({ draftTimelineId });
setTimelineStatus('COMMITTED');
setAnalyticsStatus('AVAILABLE');
```

### After Submitting Questionnaire
```typescript
await assessmentService.submitQuestionnaire({ responses });
setDoctorStatus('SUBMITTED');
```

### On Logout
```typescript
reset(); // Clear all state
```

## Rules

✅ **DO**: Update state from API responses  
✅ **DO**: Reset on logout/reload  
✅ **DO**: Use selector hooks for performance  

❌ **DON'T**: Compute state from other state  
❌ **DON'T**: Update state from UI interactions  
❌ **DON'T**: Store derived/computed values  

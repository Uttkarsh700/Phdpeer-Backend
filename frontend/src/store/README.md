# Global State Store

## Overview

Global frontend state that mirrors backend state only. No computed flags, no intelligence.

## State Structure

```typescript
{
  baselineStatus: 'NONE' | 'EXISTS',
  timelineStatus: 'NONE' | 'DRAFT' | 'COMMITTED',
  doctorStatus: 'NONE' | 'DRAFT' | 'SUBMITTED',
  analyticsStatus: 'NONE' | 'AVAILABLE'
}
```

## Usage

```typescript
import { useGlobalStateStore } from '@/store';

// In a component
const MyComponent = () => {
  // Read state
  const baselineStatus = useGlobalStateStore((state) => state.baselineStatus);
  const timelineStatus = useGlobalStateStore((state) => state.timelineStatus);
  
  // Get actions
  const setBaselineStatus = useGlobalStateStore((state) => state.setBaselineStatus);
  const setTimelineStatus = useGlobalStateStore((state) => state.setTimelineStatus);
  
  // Update state (after successful API call)
  const handleCreateBaseline = async () => {
    const response = await createBaseline(...);
    if (response) {
      setBaselineStatus('EXISTS'); // Mirror backend state
    }
  };
};
```

## State Update Locations

### baselineStatus

**Set to 'EXISTS':**
- After `POST /baselines` succeeds
- After `GET /baselines` succeeds and returns a baseline

**Set to 'NONE':**
- On user logout
- On state reset

### timelineStatus

**Set to 'DRAFT':**
- After `POST /timelines/draft/generate` succeeds
- After `GET /timelines/draft/:id` succeeds

**Set to 'COMMITTED':**
- After `POST /timelines/draft/:id/commit` succeeds
- After `GET /timelines/committed/:id` succeeds

**Set to 'NONE':**
- On user logout
- On state reset

### doctorStatus

**Set to 'DRAFT':**
- After `POST /doctor/save-draft` succeeds
- After `GET /doctor/draft` succeeds

**Set to 'SUBMITTED':**
- After `POST /doctor/submit` succeeds

**Set to 'NONE':**
- On user logout
- On state reset

### analyticsStatus

**Set to 'AVAILABLE':**
- After timeline is committed (analytics become available)
- After `GET /analytics/summary` succeeds

**Set to 'NONE':**
- On user logout
- On state reset
- When timeline is deleted

## Rules

1. **No computed flags** - State values come directly from backend responses
2. **No intelligence** - State is a simple mirror of backend state
3. **Update on API success** - State is updated only when API calls succeed
4. **Persistent** - State is persisted to localStorage to survive page refreshes

## Example: Updating State After API Call

```typescript
import { useGlobalStateStore } from '@/store';
import { get } from '@/api';

const MyComponent = () => {
  const setBaselineStatus = useGlobalStateStore((state) => state.setBaselineStatus);
  
  const loadBaseline = async () => {
    try {
      const response = await get<Baseline>('/baselines');
      if (response.data) {
        setBaselineStatus('EXISTS'); // Mirror backend: baseline exists
      } else {
        setBaselineStatus('NONE'); // Mirror backend: no baseline
      }
    } catch (error) {
      // Don't update state on error - backend state unchanged
    }
  };
};
```

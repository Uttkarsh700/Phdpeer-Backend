# Global Frontend State Setup

## ✅ Complete

Global frontend state has been created to mirror backend state only.

## State Structure

```typescript
{
  baselineStatus: 'NONE' | 'EXISTS',
  timelineStatus: 'NONE' | 'DRAFT' | 'COMMITTED',
  doctorStatus: 'NONE' | 'DRAFT' | 'SUBMITTED',
  analyticsStatus: 'NONE' | 'AVAILABLE'
}
```

## Files Created

1. **`src/store/global-state.ts`** - Zustand store with state and actions
2. **`src/store/index.ts`** - Exports for easy importing
3. **`src/store/README.md`** - Usage documentation

## Dependencies

- ✅ **Zustand** - Installed (`npm install zustand`)
- ✅ **zustand/middleware** - For localStorage persistence

## State Update Locations

### 1. baselineStatus

**Update to 'EXISTS':**
- Location: After `POST /baselines` API call succeeds
- Location: After `GET /baselines` API call succeeds and returns baseline
- Example:
  ```typescript
  const response = await post<Baseline>('/baselines', data);
  if (response.data) {
    setBaselineStatus('EXISTS');
  }
  ```

**Update to 'NONE':**
- Location: On user logout
- Location: On state reset

### 2. timelineStatus

**Update to 'DRAFT':**
- Location: After `POST /timelines/draft/generate` API call succeeds
- Location: After `GET /timelines/draft/:id` API call succeeds
- Example:
  ```typescript
  const response = await post<DraftTimeline>('/timelines/draft/generate', data);
  if (response.data) {
    setTimelineStatus('DRAFT');
  }
  ```

**Update to 'COMMITTED':**
- Location: After `POST /timelines/draft/:id/commit` API call succeeds
- Location: After `GET /timelines/committed/:id` API call succeeds
- Example:
  ```typescript
  const response = await post('/timelines/draft/:id/commit', data);
  if (response.data) {
    setTimelineStatus('COMMITTED');
    setAnalyticsStatus('AVAILABLE'); // Analytics become available
  }
  ```

**Update to 'NONE':**
- Location: On user logout
- Location: On state reset

### 3. doctorStatus

**Update to 'DRAFT':**
- Location: After `POST /doctor/save-draft` API call succeeds
- Location: After `GET /doctor/draft` API call succeeds
- Example:
  ```typescript
  const response = await post('/doctor/save-draft', data);
  if (response.data) {
    setDoctorStatus('DRAFT');
  }
  ```

**Update to 'SUBMITTED':**
- Location: After `POST /doctor/submit` API call succeeds
- Example:
  ```typescript
  const response = await post('/doctor/submit', data);
  if (response.data) {
    setDoctorStatus('SUBMITTED');
  }
  ```

**Update to 'NONE':**
- Location: On user logout
- Location: On state reset

### 4. analyticsStatus

**Update to 'AVAILABLE':**
- Location: After timeline is committed (analytics become available)
- Location: After `GET /analytics/summary` API call succeeds
- Example:
  ```typescript
  // When timeline is committed
  setTimelineStatus('COMMITTED');
  setAnalyticsStatus('AVAILABLE');
  
  // Or when analytics are fetched
  const response = await get<AnalyticsSummary>('/analytics/summary');
  if (response.data) {
    setAnalyticsStatus('AVAILABLE');
  }
  ```

**Update to 'NONE':**
- Location: On user logout
- Location: On state reset
- Location: When timeline is deleted

## Usage Example

```typescript
import { useGlobalStateStore } from '@/store';
import { get, post } from '@/api';
import type { Baseline } from '@/api';

const MyComponent = () => {
  // Read state
  const baselineStatus = useGlobalStateStore((state) => state.baselineStatus);
  const timelineStatus = useGlobalStateStore((state) => state.timelineStatus);
  
  // Get actions
  const setBaselineStatus = useGlobalStateStore((state) => state.setBaselineStatus);
  const setTimelineStatus = useGlobalStateStore((state) => state.setTimelineStatus);
  
  // Update state after API call
  const createBaseline = async () => {
    try {
      const response = await post<Baseline>('/baselines', data);
      if (response.data) {
        setBaselineStatus('EXISTS'); // Mirror backend state
      }
    } catch (error) {
      // Don't update state on error - backend state unchanged
    }
  };
  
  return (
    <div>
      <p>Baseline: {baselineStatus}</p>
      <p>Timeline: {timelineStatus}</p>
    </div>
  );
};
```

## Rules

1. ✅ **No computed flags** - State values come directly from backend responses
2. ✅ **No intelligence** - State is a simple mirror of backend state
3. ✅ **Update on API success** - State is updated only when API calls succeed
4. ✅ **Persistent** - State is persisted to localStorage (survives page refresh)

## Next Steps

When implementing API calls, update state in the following locations:

1. **Baseline creation/fetching** - Update `baselineStatus`
2. **Timeline generation/commit** - Update `timelineStatus`
3. **PhD Doctor save/submit** - Update `doctorStatus`
4. **Analytics availability** - Update `analyticsStatus`

See `src/store/README.md` for detailed usage examples.

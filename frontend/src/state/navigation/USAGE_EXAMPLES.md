# State-to-Screen Mapping - Usage Examples

## Overview

The state-to-screen mapping determines which screen to show based on the user's current global state. It follows a priority order to show the most relevant screen.

## Basic Usage

### Get Screen from State

```typescript
import { getScreenFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';

function MyComponent() {
  const state = useGlobalStateStore();
  const screen = getScreenFromState(state);
  
  console.log('Current screen:', screen);
  // Output: 'upload' | 'timeline-generation' | 'draft-timeline' | 
  //         'progress-tracking' | 'health-summary' | 'dashboard'
}
```

### Get Route from State

```typescript
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';
import { useNavigate } from 'react-router-dom';

function AutoNavigate() {
  const state = useGlobalStateStore();
  const navigate = useNavigate();
  
  const handleAutoNavigate = () => {
    const route = getRouteFromState(state);
    navigate(route);
  };
  
  return <button onClick={handleAutoNavigate}>Go to Current Screen</button>;
}
```

## Common Patterns

### Redirect Based on State

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';

function StateBasedRedirect() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  useEffect(() => {
    // Redirect to appropriate screen based on state
    const route = getRouteFromState(state);
    navigate(route, { replace: true });
  }, [state, navigate]);
  
  return null; // This component just redirects
}
```

### Conditional Rendering

```typescript
import { getScreenFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';

function ConditionalContent() {
  const state = useGlobalStateStore();
  const screen = getScreenFromState(state);
  
  switch (screen) {
    case 'upload':
      return <DocumentUploadPrompt />;
    case 'timeline-generation':
      return <TimelineGenerationPrompt />;
    case 'draft-timeline':
      return <DraftTimelineEditor />;
    case 'progress-tracking':
      return <ProgressTrackingView />;
    case 'health-summary':
      return <HealthSummaryView />;
    case 'dashboard':
      return <AnalyticsDashboard />;
    default:
      return <LoadingSpinner />;
  }
}
```

### Navigation Guard

```typescript
import { useLocation, useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';
import { useEffect } from 'react';

function NavigationGuard({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  useEffect(() => {
    const expectedRoute = getRouteFromState(state);
    
    // If user is not on the expected route, redirect
    if (location.pathname !== expectedRoute) {
      navigate(expectedRoute, { replace: true });
    }
  }, [state, location.pathname, navigate]);
  
  return <>{children}</>;
}
```

### Home Page Redirect

```typescript
import { Navigate } from 'react-router-dom';
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';

function HomePage() {
  const state = useGlobalStateStore();
  const route = getRouteFromState(state);
  
  // Redirect to appropriate screen based on state
  return <Navigate to={route} replace />;
}
```

### State Change Handler

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore } from '@/state/global';

function StateChangeHandler() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  useEffect(() => {
    // When state changes, navigate to appropriate screen
    const route = getRouteFromState(state);
    navigate(route);
  }, [
    state.baselineStatus,
    state.timelineStatus,
    state.doctorStatus,
    state.analyticsStatus,
    navigate,
  ]);
  
  return null;
}
```

## Priority Order

The mapping follows this priority order (highest to lowest):

1. **Dashboard** - Analytics available
2. **Health Summary** - Doctor submitted
3. **Progress Tracking** - Committed timeline
4. **Draft Timeline** - Draft timeline
5. **Timeline Generation** - Baseline exists
6. **Upload** - No baseline

This ensures the most relevant screen is shown when multiple conditions are met.

## Example: Complete App Flow

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/state/navigation';
import { useGlobalStateStore, useGlobalStateActions } from '@/state/global';
import { baselineService, timelineService } from '@/services';

function AppInitializer() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  const { setState } = useGlobalStateActions();
  
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Fetch all state from backend
        const [baselines, timelines, drafts] = await Promise.all([
          baselineService.getUserBaselines(),
          timelineService.getUserCommitted(),
          timelineService.getUserDrafts(),
        ]);
        
        // Update state from API responses
        setState({
          baselineStatus: baselines.length > 0 ? 'EXISTS' : 'NONE',
          timelineStatus: timelines.length > 0 ? 'COMMITTED' : 
                          drafts.length > 0 ? 'DRAFT' : 'NONE',
          // ... other status updates
        });
        
        // Navigate to appropriate screen based on updated state
        const route = getRouteFromState(state);
        navigate(route, { replace: true });
      } catch (error) {
        console.error('Failed to initialize app:', error);
      }
    };
    
    initializeApp();
  }, []);
  
  return null;
}
```

## Screen Routes

| Screen | Route | Condition |
|--------|-------|-----------|
| `upload` | `/documents/upload` | No baseline |
| `timeline-generation` | `/timelines` | Baseline exists, no timeline |
| `draft-timeline` | `/timelines` | Draft timeline exists |
| `progress-tracking` | `/progress` | Committed timeline exists |
| `health-summary` | `/health` | Doctor submitted |
| `dashboard` | `/dashboard` | Analytics available |

## Rules

✅ **DO**: Use `getRouteFromState()` for navigation  
✅ **DO**: Check screen type for conditional rendering  
✅ **DO**: Update state from API before navigating  

❌ **DON'T**: Hardcode routes based on assumptions  
❌ **DON'T**: Navigate without updating state first  
❌ **DON'T**: Override the priority order manually  

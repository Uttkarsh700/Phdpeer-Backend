# Route Guards - Usage Examples

## Overview

Route guards prevent navigation to invalid screens based on global state. They rely **only** on global state (no API calls) and gracefully redirect to valid screens.

## Basic Usage

### Wrap Routes with Guard

```typescript
import { RouteGuard } from '@/guards';
import { DashboardPage } from '@/pages/DashboardPage';

// In router configuration
{
  path: 'dashboard',
  element: (
    <RouteGuard>
      <DashboardPage />
    </RouteGuard>
  ),
}
```

### Global Route Guard

```typescript
import { RouteGuard } from '@/guards';
import { Outlet } from 'react-router-dom';

function App() {
  return (
    <RouteGuard>
      <Outlet />
    </RouteGuard>
  );
}
```

## Route Validation

### Check if Route is Valid

```typescript
import { isRouteValidForState } from '@/guards';
import { useGlobalStateStore } from '@/state/global';
import { useLocation } from 'react-router-dom';

function MyComponent() {
  const location = useLocation();
  const state = useGlobalStateStore();
  
  const isValid = isRouteValidForState(location.pathname, state);
  
  if (!isValid) {
    // Route is not valid for current state
    return <div>This screen is not available yet.</div>;
  }
  
  return <div>Content</div>;
}
```

### Manual Navigation Guard

```typescript
import { useNavigate } from 'react-router-dom';
import { isRouteValidForState, getRouteFromState } from '@/guards';
import { useGlobalStateStore } from '@/state/global';

function NavigationButton({ targetRoute }: { targetRoute: string }) {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  const handleClick = () => {
    // Check if route is valid before navigating
    if (isRouteValidForState(targetRoute, state)) {
      navigate(targetRoute);
    } else {
      // Redirect to valid route
      const validRoute = getRouteFromState(state);
      navigate(validRoute);
    }
  };
  
  return <button onClick={handleClick}>Navigate</button>;
}
```

## Router Integration

### Update Router with Guards

```typescript
import { createBrowserRouter } from 'react-router-dom';
import { RouteGuard } from '@/guards';
import App from '@/App';

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <RouteGuard>
        <App />
      </RouteGuard>
    ),
    children: [
      {
        path: 'dashboard',
        lazy: () => import('@/pages/DashboardPage'),
      },
      {
        path: 'timelines',
        lazy: () => import('@/pages/TimelinesPage'),
      },
      // ... other routes
    ],
  },
]);
```

### Guard Specific Routes

```typescript
import { RouteGuard } from '@/guards';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      // Guard only specific routes
      {
        path: 'dashboard',
        element: (
          <RouteGuard>
            <DashboardPage />
          </RouteGuard>
        ),
      },
      {
        path: 'progress',
        element: (
          <RouteGuard>
            <ProgressPage />
          </RouteGuard>
        ),
      },
      // Unprotected routes
      {
        path: 'documents',
        element: <DocumentsPage />,
      },
    ],
  },
]);
```

## Conditional Navigation

### Prevent Invalid Navigation

```typescript
import { useNavigate } from 'react-router-dom';
import { isRouteValidForState } from '@/guards';
import { useGlobalStateStore } from '@/state/global';

function NavigationMenu() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  const handleNavigate = (route: string) => {
    if (isRouteValidForState(route, state)) {
      navigate(route);
    } else {
      // Show message or redirect
      alert('This screen is not available yet. Please complete the required steps.');
    }
  };
  
  return (
    <nav>
      <button onClick={() => handleNavigate('/dashboard')}>Dashboard</button>
      <button onClick={() => handleNavigate('/progress')}>Progress</button>
      <button onClick={() => handleNavigate('/health')}>Health</button>
    </nav>
  );
}
```

### Disable Invalid Links

```typescript
import { Link } from 'react-router-dom';
import { isRouteValidForState } from '@/guards';
import { useGlobalStateStore } from '@/state/global';

function NavigationLink({ to, children }: { to: string; children: React.ReactNode }) {
  const state = useGlobalStateStore();
  const isValid = isRouteValidForState(to, state);
  
  if (!isValid) {
    return (
      <span className="opacity-50 cursor-not-allowed" title="Not available yet">
        {children}
      </span>
    );
  }
  
  return <Link to={to}>{children}</Link>;
}
```

## State-Based Redirects

### Redirect on State Change

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/guards';
import { useGlobalStateStore } from '@/state/global';

function StateChangeRedirect() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  useEffect(() => {
    // When state changes, ensure we're on a valid route
    const validRoute = getRouteFromState(state);
    navigate(validRoute, { replace: true });
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

### Redirect After State Update

```typescript
import { useNavigate } from 'react-router-dom';
import { getRouteFromState } from '@/guards';
import { useGlobalStateStore, useGlobalStateActions } from '@/state/global';
import { baselineService } from '@/services/baseline.service';

function CreateBaselineForm() {
  const navigate = useNavigate();
  const { setBaselineStatus } = useGlobalStateActions();
  
  const handleSubmit = async (data: CreateBaselineRequest) => {
    try {
      await baselineService.create(data);
      
      // Update state
      setBaselineStatus('EXISTS');
      
      // Redirect to valid route for new state
      const state = useGlobalStateStore.getState();
      const validRoute = getRouteFromState(state);
      navigate(validRoute);
    } catch (error) {
      console.error('Failed to create baseline:', error);
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

## Validation Rules

### Route Validation Rules

| Route | Valid When | Description |
|-------|------------|-------------|
| `/documents/upload` | `baselineStatus === 'NONE'` | No baseline exists |
| `/timelines` | `baselineStatus === 'EXISTS'` | Baseline exists |
| `/progress` | `timelineStatus === 'COMMITTED'` | Committed timeline exists |
| `/health` | `doctorStatus === 'SUBMITTED'` | Questionnaire submitted |
| `/dashboard` | `analyticsStatus === 'AVAILABLE'` | Analytics available |

## Complete Example

```typescript
import { RouteGuard } from '@/guards';
import { Outlet, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useGlobalStateStore } from '@/state/global';
import { getRouteFromState } from '@/guards';

function App() {
  const navigate = useNavigate();
  const state = useGlobalStateStore();
  
  useEffect(() => {
    // On app load, ensure we're on a valid route
    const validRoute = getRouteFromState(state);
    navigate(validRoute, { replace: true });
  }, []);
  
  return (
    <RouteGuard>
      <Outlet />
    </RouteGuard>
  );
}
```

## Rules

✅ **DO**: Use RouteGuard to wrap protected routes  
✅ **DO**: Check route validity before manual navigation  
✅ **DO**: Redirect to valid route when state changes  

❌ **DON'T**: Make API calls in guards  
❌ **DON'T**: Compute state in guards  
❌ **DON'T**: Bypass guards for "convenience"  

# Route Guards Guide

## Overview

Route guards prevent users from navigating to screens that don't match backend state. They fall back gracefully to the correct screen without crashes.

## Components

### 1. `ProtectedRoute`

Simple wrapper for routes that require specific state.

```tsx
import { ProtectedRoute } from '@/guards';

<ProtectedRoute requires="analytics" fallbackRoute="/timeline">
  <Dashboard />
</ProtectedRoute>
```

**Props:**
- `requires`: `'baseline' | 'draft' | 'committed' | 'analytics'`
- `fallbackRoute`: Optional custom fallback route
- `fallbackMessage`: Optional custom fallback message

### 2. `RouteGuard`

Advanced route guard with custom guard functions.

```tsx
import { RouteGuard, guardAnalyticsRequiresCommittedTimeline } from '@/guards';

<RouteGuard
  customGuard={guardAnalyticsRequiresCommittedTimeline}
  fallbackRoute="/timeline"
  fallbackMessage="Please commit a timeline first."
>
  <Dashboard />
</RouteGuard>
```

### 3. `RouteErrorBoundary`

Catches errors in route guards and prevents crashes.

```tsx
import { RouteErrorBoundary } from '@/guards';

<RouteErrorBoundary fallbackRoute="/home">
  <Routes>
    {/* Your routes */}
  </Routes>
</RouteErrorBoundary>
```

## Hooks

### `useRouteAccessible`

Check if a route is accessible before rendering links/buttons.

```tsx
import { useRouteAccessible } from '@/guards';

const MyComponent = () => {
  const { accessible, reason } = useRouteAccessible('/dashboard');
  
  return (
    <Button 
      disabled={!accessible}
      onClick={() => navigate('/dashboard')}
    >
      View Dashboard
      {!accessible && <span className="text-xs">({reason})</span>}
    </Button>
  );
};
```

### `useNavigationGuard`

Provides safe navigation utilities.

```tsx
import { useNavigationGuard } from '@/guards';

const MyComponent = () => {
  const { navigateSafely, isRouteAccessible } = useNavigationGuard();
  
  return (
    <Button 
      disabled={!isRouteAccessible('/dashboard')}
      onClick={() => navigateSafely('/dashboard')}
    >
      View Dashboard
    </Button>
  );
};
```

## Route Requirements

Routes are automatically protected based on pathname patterns:

- `/timelines/generate` → Requires baseline
- `/timelines/draft/:draftId` → Requires baseline
- `/timelines/commit` → Requires draft
- `/timelines/progress` → Requires committed timeline
- `/timelines/:committedId/progress` → Requires committed timeline
- `/dashboard` → Requires committed timeline (analytics)
- `/analytics` → Requires committed timeline

## Integration Example

```tsx
// App.tsx
import { ProtectedRoute, RouteErrorBoundary } from '@/guards';

<BrowserRouter>
  <RouteErrorBoundary fallbackRoute="/home">
    <Routes>
      <Route path="/dashboard" 
        element={
          <ProtectedRoute requires="analytics" fallbackRoute="/timeline">
            <Dashboard />
          </ProtectedRoute>
        } 
      />
    </Routes>
  </RouteErrorBoundary>
</BrowserRouter>
```

## Behavior

1. **State Check**: Guard checks backend state from global store
2. **Redirect**: If state doesn't match, redirects to fallback route
3. **Toast Notification**: Shows toast explaining why navigation was blocked
4. **No Crashes**: Error boundary catches any errors and shows fallback UI
5. **Graceful Fallback**: User is redirected to appropriate screen

## Error Handling

- Route guards throw `GuardViolationError` which is caught and handled gracefully
- `RouteErrorBoundary` catches unexpected errors and prevents app crashes
- All errors are logged for debugging
- User sees friendly error messages, not stack traces

## Best Practices

1. **Wrap routes with ProtectedRoute** for routes that require state
2. **Use RouteErrorBoundary** at the router level to catch all errors
3. **Disable navigation buttons** using `useRouteAccessible` or `useNavigationGuard`
4. **Provide clear fallback routes** that guide users to the correct screen
5. **Show toast notifications** to explain why navigation was blocked

## State Flow

```
User navigates to /dashboard
  ↓
RouteGuard checks state
  ↓
State check: timelineStatus === 'COMMITTED'?
  ↓
  ├─ Yes → Render Dashboard
  └─ No → Redirect to /timeline with toast message
```

## No Crashes Guarantee

- All route guards are wrapped in try-catch
- RouteErrorBoundary catches component errors
- Fallback UI is always shown instead of crashes
- Errors are logged but don't break the app
